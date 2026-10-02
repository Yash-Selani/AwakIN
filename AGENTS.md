# AI Agent Rules for AwakIN

When writing or modifying code for this project, you MUST adhere to the following rules:

1. **API Routes**: All API routes must be nested under `/api`.
2. **Pydantic Schemas**: Use Pydantic schemas for every request and response in the backend.
3. **No Secrets in Code**: Never hardcode secrets. Always use `.env` and `.env.example`.
4. **Async FastAPI**: All FastAPI endpoints must be asynchronous (`async def`).
5. **External Calls**: Every external API call (e.g., Gemini API, Firebase) must be wrapped with a timeout and proper error handling.
6. **Mobile-First UI**: The frontend must be designed with a mobile-first responsive approach.
7. **Accessibility**: All UI components must be accessible (e.g., aria-labels, minimum contrast ratio of AA).
8. **Emergency Notice**: **CRITICAL:** Every AI-generated response provided to the user must include the notice: `"call 112 for immediate danger"`.
