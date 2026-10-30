import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { APIProvider, Map, AdvancedMarker, Pin } from '@vis.gl/react-google-maps';
import api from '../services/api';
import FilterChips from '../components/Map/FilterChips';
import PlacesSidebar from '../components/Map/PlacesSidebar';
import './MapPage.css';

const DELHI_COORDS = { lat: 28.6139, lng: 77.2090 };

const MapPage = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialType = queryParams.get('type') || 'hospital';

  const [center, setCenter] = useState(DELHI_COORDS);
  const [userLocation, setUserLocation] = useState(null);
  const [places, setPlaces] = useState([]);
  const [selectedType, setSelectedType] = useState(initialType);
  const [selectedRadius, setSelectedRadius] = useState(3000);
  const [selectedPlaceId, setSelectedPlaceId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fallback map ID if none provided. In a real app, use mapId from env.
  const mapId = import.meta.env.VITE_GOOGLE_MAP_ID || "DEMO_MAP_ID";
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

  useEffect(() => {
    // Get user location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          setCenter(loc);
          setUserLocation(loc);
        },
        (err) => {
          console.warn("Geolocation failed or denied, using default location.", err);
        }
      );
    }
  }, []);

  const fetchPlaces = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/api/places/nearby', {
        params: {
          lat: center.lat,
          lon: center.lng,
          type: selectedType,
          radius: selectedRadius
        }
      });
      setPlaces(response.data.places || []);
    } catch (err) {
      if (err.response) {
        if (err.response.status === 403) {
          setError('Permission denied to use Places API.');
        } else if (err.response.status === 429) {
          setError('API Quota exceeded. Please try again later.');
        } else {
          setError(err.response.data?.detail || 'Failed to fetch places.');
        }
      } else {
        setError('Network error. Failed to fetch places.');
      }
      setPlaces([]);
    } finally {
      setLoading(false);
    }
  }, [center, selectedType, selectedRadius]);

  useEffect(() => {
    fetchPlaces();
  }, [fetchPlaces]);

  const handlePlaceClick = (id) => {
    setSelectedPlaceId(id);
    const place = places.find(p => p.id === id);
    if (place) {
      setCenter(place.location);
    }
  };

  const getMarkerColor = (type) => {
    switch (type) {
      case 'hospital': return '#d32f2f';
      case 'fire_station': return '#ff9800';
      case 'police': return '#1976d2';
      case 'pharmacy': return '#4caf50';
      case 'blood_bank': return '#b71c1c';
      default: return '#757575';
    }
  };

  return (
    <div className="map-page-container">
      {/* Mobile-first layout: sidebar takes top/bottom depending on media query. */}
      <div className="map-page-layout">
        
        {/* Sidebar */}
        <div className="map-sidebar">
          <div className="map-sidebar-header">
            <h2 className="map-title">Emergency Map</h2>
            <FilterChips
              selectedType={selectedType}
              onTypeChange={setSelectedType}
              selectedRadius={selectedRadius}
              onRadiusChange={setSelectedRadius}
            />
            {error && <div style={styles.errorBanner}>{error}</div>}
            {loading && <div style={styles.loading}>Searching nearby...</div>}
          </div>
          
          <div className="map-list-container">
            <PlacesSidebar
              places={places}
              selectedPlaceId={selectedPlaceId}
              onPlaceClick={handlePlaceClick}
            />
          </div>
        </div>

        {/* Map Area */}
        <div className="map-area">
          {!apiKey ? (
            <div style={styles.noKey}>
              VITE_GOOGLE_MAPS_API_KEY is missing in .env
            </div>
          ) : (
            <APIProvider apiKey={apiKey}>
              <Map
                mapId={mapId}
                defaultZoom={13}
                defaultCenter={DELHI_COORDS}
                center={center}
                onCenterChanged={ev => setCenter(ev.detail.center)}
                gestureHandling={'greedy'}
                disableDefaultUI={true}
              >
                {/* User Location Marker */}
                {userLocation && (
                  <AdvancedMarker position={userLocation}>
                    <Pin background={'#000'} borderColor={'#fff'} glyphColor={'#fff'} />
                  </AdvancedMarker>
                )}

                {/* Places Markers */}
                {places.map(place => (
                  <AdvancedMarker
                    key={place.id}
                    position={place.location}
                    onClick={() => handlePlaceClick(place.id)}
                  >
                    <Pin 
                      background={getMarkerColor(place.type)} 
                      borderColor={'#fff'} 
                      glyphColor={'#fff'} 
                      scale={selectedPlaceId === place.id ? 1.2 : 1}
                    />
                  </AdvancedMarker>
                ))}
              </Map>
            </APIProvider>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  errorBanner: {
    background: 'rgba(244, 67, 54, 0.1)',
    color: '#f44336',
    padding: '0.5rem',
    borderRadius: '4px',
    marginBottom: '1rem',
    fontSize: '0.85rem',
  },
  loading: {
    color: 'var(--text-secondary, #b3b3b3)',
    fontSize: '0.85rem',
    marginBottom: '1rem',
  },
  noKey: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    background: '#333',
    color: '#fff',
  }
};

export default MapPage;
