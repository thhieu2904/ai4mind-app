/**
 * Medical Center Map Component
 * Hiển thị Mapbox Map với markers cho các trung tâm y tế
 */

import React, { useState, useEffect, useRef } from "react";
import Map, {
  Marker,
  Popup,
  NavigationControl,
  GeolocateControl,
  Source,
  Layer,
} from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import {
  Box,
  Typography,
  Alert,
  Button,
  CircularProgress,
} from "@mui/material";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import PersonPinCircleIcon from "@mui/icons-material/PersonPinCircle";
import DirectionsIcon from "@mui/icons-material/Directions";
import CloseIcon from "@mui/icons-material/Close";
import { MedicalCenter } from "../../services/medicalCenterService";

// Constants
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || "";
const DEFAULT_CENTER = { latitude: 10.7769, longitude: 106.7009 }; // TP.HCM
const DEFAULT_ZOOM = 12;

interface MedicalCenterMapProps {
  centers: MedicalCenter[];
  onCenterClick?: (center: MedicalCenter) => void;
  userLocation?: { lat: number; lng: number } | null;
  onLocationUpdate?: (lat: number, lng: number) => void;
  selectedCenterForRoute?: MedicalCenter | null; // Auto-route to this center
}

const MedicalCenterMap: React.FC<MedicalCenterMapProps> = ({
  centers,
  onCenterClick,
  userLocation,
  onLocationUpdate,
  selectedCenterForRoute,
}) => {
  const [viewState, setViewState] = useState({
    longitude: DEFAULT_CENTER.longitude,
    latitude: DEFAULT_CENTER.latitude,
    zoom: DEFAULT_ZOOM,
  });
  const [selectedCenter, setSelectedCenter] = useState<MedicalCenter | null>(
    null
  );
  const [locationError, setLocationError] = useState<string | null>(null);
  const [routeData, setRouteData] = useState<any>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);
  const mapRef = useRef<any>(null);

  // Update map center when userLocation changes
  useEffect(() => {
    if (userLocation) {
      setViewState({
        longitude: userLocation.lng,
        latitude: userLocation.lat,
        zoom: 13,
      });
    }
  }, [userLocation]);

  // Get user's current location on mount
  useEffect(() => {
    if (!userLocation && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          if (onLocationUpdate) {
            onLocationUpdate(lat, lng);
          }
        },
        (error) => {
          console.error("Geolocation error:", error);
        }
      );
    }
  }, [userLocation, onLocationUpdate]);

  // Handle marker click
  const handleMarkerClick = (center: MedicalCenter) => {
    setSelectedCenter(center);
    setRouteData(null); // Clear previous route
    if (onCenterClick) {
      onCenterClick(center);
    }
  };

  // Fetch directions from Mapbox Directions API
  const getDirections = async (destination: MedicalCenter) => {
    if (!userLocation) {
      setLocationError("Cần có vị trí của bạn để chỉ đường");
      return;
    }

    setIsLoadingRoute(true);
    setLocationError(null);

    try {
      const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${userLocation.lng},${userLocation.lat};${destination.longitude},${destination.latitude}?geometries=geojson&access_token=${MAPBOX_TOKEN}`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.routes && data.routes.length > 0) {
        const route = data.routes[0];
        setRouteData({
          type: "Feature",
          geometry: route.geometry,
          properties: {
            distance: (route.distance / 1000).toFixed(2), // km
            duration: Math.round(route.duration / 60), // minutes
          },
        });

        // Fit map to show entire route
        if (mapRef.current) {
          const coordinates = route.geometry.coordinates;
          const bounds: [[number, number], [number, number]] = [
            [
              Math.min(...coordinates.map((c: number[]) => c[0])),
              Math.min(...coordinates.map((c: number[]) => c[1])),
            ],
            [
              Math.max(...coordinates.map((c: number[]) => c[0])),
              Math.max(...coordinates.map((c: number[]) => c[1])),
            ],
          ];
          mapRef.current.fitBounds(bounds, {
            padding: 50,
            duration: 1000,
          });
        }
      } else {
        setLocationError("Không tìm thấy đường đi");
      }
    } catch (error) {
      console.error("Directions error:", error);
      setLocationError("Lỗi khi tìm đường đi");
    } finally {
      setIsLoadingRoute(false);
    }
  };

  // Clear route
  const clearRoute = () => {
    setRouteData(null);
  };

  // Auto-route when selectedCenterForRoute changes (from list click)
  useEffect(() => {
    if (selectedCenterForRoute && userLocation) {
      setSelectedCenter(selectedCenterForRoute);
      getDirections(selectedCenterForRoute);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCenterForRoute, userLocation]);

  if (!MAPBOX_TOKEN) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Thiếu Mapbox token. Vui lòng thêm VITE_MAPBOX_TOKEN vào file .env
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", height: "600px", position: "relative" }}>
      {locationError && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {locationError}
        </Alert>
      )}

      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt: any) => setViewState(evt.viewState)}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/streets-v12"
        mapboxAccessToken={MAPBOX_TOKEN}
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" />

        {/* Geolocate Control - tự động lấy vị trí user */}
        <GeolocateControl
          position="top-right"
          trackUserLocation
          showUserLocation
          onGeolocate={(e: any) => {
            if (onLocationUpdate) {
              onLocationUpdate(e.coords.latitude, e.coords.longitude);
            }
            setLocationError(null);
          }}
          onError={(e: any) => {
            setLocationError(`Không thể lấy vị trí: ${e.message}`);
          }}
        />

        {/* User Location Marker (Blue Pin) */}
        {userLocation && (
          <Marker
            longitude={userLocation.lng}
            latitude={userLocation.lat}
            anchor="bottom"
          >
            <PersonPinCircleIcon
              sx={{
                fontSize: 40,
                color: "#1976d2",
                filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.3))",
              }}
            />
          </Marker>
        )}

        {/* Route Line Layer */}
        {routeData && (
          <Source id="route" type="geojson" data={routeData}>
            <Layer
              id="route-layer"
              type="line"
              paint={{
                "line-color": "#1976d2",
                "line-width": 4,
                "line-opacity": 0.8,
              }}
            />
          </Source>
        )}

        {/* Medical Center Markers (Red Pins) */}
        {centers.map((center) => (
          <Marker
            key={center.id}
            longitude={center.longitude}
            latitude={center.latitude}
            anchor="bottom"
          >
            <LocationOnIcon
              sx={{
                fontSize: 36,
                color: "#d32f2f",
                cursor: "pointer",
                transition: "transform 0.2s",
                filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.3))",
                "&:hover": {
                  transform: "scale(1.2)",
                },
              }}
              onClick={() => handleMarkerClick(center)}
            />
          </Marker>
        ))}

        {/* Info Popup khi click marker */}
        {selectedCenter && (
          <Popup
            longitude={selectedCenter.longitude}
            latitude={selectedCenter.latitude}
            anchor="top"
            onClose={() => setSelectedCenter(null)}
            closeButton={true}
            closeOnClick={false}
            offset={25}
          >
            <Box sx={{ p: 1, minWidth: 250, maxWidth: 350 }}>
              <Typography
                variant="h6"
                sx={{ fontWeight: "bold", mb: 1, fontSize: "1rem" }}
              >
                {selectedCenter.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                📍 {selectedCenter.address}
              </Typography>
              {selectedCenter.distance !== undefined &&
                selectedCenter.distance !== null && (
                  <Typography
                    variant="body2"
                    color="primary"
                    sx={{ fontWeight: "bold", mb: 1 }}
                  >
                    📏 Cách bạn: {selectedCenter.distance.toFixed(2)} km
                  </Typography>
                )}
              {selectedCenter.services &&
                selectedCenter.services.length > 0 && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    🏥 <strong>Dịch vụ:</strong>{" "}
                    {selectedCenter.services.join(", ")}
                  </Typography>
                )}
              {selectedCenter.opening_hours && (
                <Typography
                  variant="caption"
                  display="block"
                  sx={{ mt: 1, color: "text.secondary" }}
                >
                  🕐{" "}
                  {selectedCenter.opening_hours.weekday ||
                    "Liên hệ để biết giờ mở cửa"}
                </Typography>
              )}

              {/* Route Info */}
              {routeData && (
                <Box sx={{ mt: 2, p: 1, bgcolor: "#e3f2fd", borderRadius: 1 }}>
                  <Typography
                    variant="body2"
                    sx={{ fontWeight: "bold", color: "#1976d2" }}
                  >
                    🚗 {routeData.properties.distance} km •{" "}
                    {routeData.properties.duration} phút
                  </Typography>
                </Box>
              )}

              {/* Navigation Buttons */}
              <Box
                sx={{ mt: 2, display: "flex", flexDirection: "column", gap: 1 }}
              >
                {!routeData ? (
                  <>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={
                        isLoadingRoute ? (
                          <CircularProgress size={16} color="inherit" />
                        ) : (
                          <DirectionsIcon />
                        )
                      }
                      onClick={() => getDirections(selectedCenter)}
                      disabled={!userLocation || isLoadingRoute}
                      fullWidth
                    >
                      {isLoadingRoute ? "Đang tìm..." : "Chỉ đường"}
                    </Button>
                    {!userLocation && (
                      <Typography
                        variant="caption"
                        color="warning.main"
                        sx={{ textAlign: "center" }}
                      >
                        ⚠️ Cần cho phép truy cập vị trí để chỉ đường
                      </Typography>
                    )}
                  </>
                ) : (
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<CloseIcon />}
                    onClick={clearRoute}
                    fullWidth
                  >
                    Xóa đường đi
                  </Button>
                )}
              </Box>
            </Box>
          </Popup>
        )}
      </Map>
    </Box>
  );
};

export default MedicalCenterMap;
