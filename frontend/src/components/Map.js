import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

// Replace with your Mapbox access token
mapboxgl.accessToken = 'your_mapbox_access_token_here';

function Map() {
  const mapContainer = useRef(null);
  const map = useRef(null);

  useEffect(() => {
    if (map.current) return; // initialize map only once

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-74.5, 40], // Starting position [lng, lat]
      zoom: 9 // Starting zoom
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl());

    // Cleanup on unmount
    return () => map.current.remove();
  }, []);

  return (
    <div 
      ref={mapContainer} 
      style={{ 
        width: '100%', 
        height: '100vh' 
      }} 
    />
  );
}

export default Map; 