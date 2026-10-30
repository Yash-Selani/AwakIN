import logging
import httpx
import asyncio
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.alert import NewsItem
from app.db.database import AsyncSessionLocal
from app.core.config import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
KEYWORDS = ["flood", "earthquake", "fire", "cyclone", "landslide", "accident", "blast"]

async def parse_with_gemini(news_batch: list[dict]) -> list[dict]:
    if not settings.GEMINI_API_KEY:
        logger.warning("No Gemini API key, skipping Gemini parsing.")
        return []

    system_prompt = """You are a news filtering and summarization assistant for a disaster management app.
Your task is to analyze a batch of news headlines and snippets.
For each item, determine if it relates to a disaster, emergency, or accident in India.
If it does, output `is_disaster_related`: true, extract the `city` mentioned (if any, otherwise null), assign a `disaster_slug` (one of: flood, earthquake, fire, cyclone, landslide, accident, blast, or other), and write a concise, one-line `one_line_summary` in English.
If it is NOT a disaster, simply output `is_disaster_related`: false for that item.
"""

    prompt = "Analyze these news items:\n"
    for i, item in enumerate(news_batch):
        prompt += f"Item {i}:\nTitle: {item['title']}\n\n"

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        async def call_gemini():
            return await asyncio.to_thread(
                client.models.generate_content,
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "index": {"type": "INTEGER", "description": "Index of the item in the batch"},
                                "is_disaster_related": {"type": "BOOLEAN"},
                                "disaster_slug": {"type": "STRING", "nullable": True},
                                "city": {"type": "STRING", "nullable": True},
                                "one_line_summary": {"type": "STRING", "nullable": True}
                            },
                            "required": ["index", "is_disaster_related"]
                        }
                    },
                    temperature=0.2
                )
            )
            
        response = await asyncio.wait_for(call_gemini(), timeout=30.0)
        data = json.loads(response.text)
        
        results = []
        # Merge results back
        for res in data:
            idx = res.get("index")
            if idx is not None and 0 <= idx < len(news_batch):
                if res.get("is_disaster_related"):
                    news_batch[idx].update({
                        "summary": res.get("one_line_summary"),
                        "disaster_slug": res.get("disaster_slug"),
                        "city": res.get("city")
                    })
                    results.append(news_batch[idx])
        return results

    except Exception as e:
        logger.error(f"Error in Gemini parsing: {e}")
        return []

async def fetch_google_news_rss(query: str) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    items = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=15.0)
            if resp.status_code == 200:
                root = ET.fromstring(resp.text)
                for item in root.findall(".//item")[:10]: # limit to top 10 per query to avoid massive batches
                    title = item.findtext("title")
                    link = item.findtext("link")
                    pubDate = item.findtext("pubDate")
                    source = item.find("source")
                    source_text = source.text if source is not None else "Google News"
                    
                    parsed_date = None
                    try:
                        if pubDate:
                            parsed_date = parsedate_to_datetime(pubDate)
                    except Exception:
                        pass
                        
                    items.append({
                        "title": title,
                        "url": link,
                        "source": source_text,
                        "published_at": parsed_date,
                    })
    except Exception as e:
        logger.error(f"Error fetching Google News for query {query}: {e}")
    return items

async def poll_news():
    logger.info("Polling nearby-incident news...")
    
    # We query for a few cities + generic disaster keywords to not overwhelm the limits
    all_raw_items = []
    
    for city in CITIES[:3]: # Poll only top 3 cities at a time or cycle them in production
        query = f"({' OR '.join(KEYWORDS)}) {city}"
        items = await fetch_google_news_rss(query)
        all_raw_items.extend(items)
        
    if not all_raw_items:
        return
        
    # Deduplicate by URL
    seen_urls = set()
    unique_items = []
    for item in all_raw_items:
        if item["url"] not in seen_urls:
            unique_items.append(item)
            seen_urls.add(item["url"])
            
    # Process with Gemini in batches of 15
    valid_news = []
    batch_size = 15
    for i in range(0, len(unique_items), batch_size):
        batch = unique_items[i:i+batch_size]
        processed = await parse_with_gemini(batch)
        valid_news.extend(processed)
        await asyncio.sleep(1) # avoid rate limits
        
    if not valid_news:
        logger.info("No valid disaster news found in this poll.")
        return
        
    async with AsyncSessionLocal() as db:
        # Delete old news (older than 2 days) to keep DB clean
        two_days_ago = datetime.now(timezone.utc).timestamp() - (2 * 24 * 3600)
        await db.execute(delete(NewsItem).where(
            NewsItem.published_at < datetime.fromtimestamp(two_days_ago, tz=timezone.utc)
        ))
        
        # Upsert valid news
        for item in valid_news:
            stmt = select(NewsItem).where(NewsItem.url == item["url"])
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                new_item = NewsItem(
                    title=item.get("title"),
                    url=item.get("url"),
                    source=item.get("source"),
                    summary=item.get("summary"),
                    disaster_slug=item.get("disaster_slug"),
                    city=item.get("city"),
                    published_at=item.get("published_at")
                )
                db.add(new_item)
                
        await db.commit()
        logger.info(f"Processed and inserted {len(valid_news)} disaster news items.")
