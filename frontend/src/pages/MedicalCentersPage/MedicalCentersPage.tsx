/**
 * Medical Centers Page
 * Main page hiển thị map và list các trung tâm y tế hỗ trợ sức khỏe tâm thần
 */

import React, { useState, useEffect } from "react";
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Chip,
  Stack,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import TuneIcon from "@mui/icons-material/Tune";
import MapIcon from "@mui/icons-material/Map";
import ListIcon from "@mui/icons-material/List";
import SearchIcon from "@mui/icons-material/Search";
import MyLocationIcon from "@mui/icons-material/MyLocation";
import MainLayout from "../../components/layout/MainLayout";
import medicalCenterService, {
  MedicalCenter,
  NearbyRequest,
} from "../../services/medicalCenterService";
import MedicalCenterMap from "../../components/MedicalCenterMap/MedicalCenterMap";
import MedicalCenterList from "../../components/MedicalCenterList/MedicalCenterList";

type ViewMode = "map" | "list" | "both";

// Available services for filtering
const AVAILABLE_SERVICES = [
  "Khám Tâm thần",
  "Tư vấn Tâm lý",
  "Điều trị Nội trú",
  "Điều trị Ngoại trú",
  "Trị liệu Tâm lý",
  "Trị liệu Nhóm",
  "Thiền định",
  "Quản lý Căng thẳng",
];

const MedicalCentersPage: React.FC = () => {
  const [centers, setCenters] = useState<MedicalCenter[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("both");

  // Location & Search
  const [userLocation, setUserLocation] = useState<{
    lat: number;
    lng: number;
  } | null>(null);
  const [radius, setRadius] = useState(50); // km
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [limit, setLimit] = useState(20);

  // Manual location input
  const [manualLat, setManualLat] = useState("");
  const [manualLng, setManualLng] = useState("");

  // Map ref to trigger routing from list
  const [selectedCenterForRoute, setSelectedCenterForRoute] =
    useState<MedicalCenter | null>(null);

  // Auto-get user location on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          setUserLocation({ lat, lng });
          setManualLat(lat.toFixed(6));
          setManualLng(lng.toFixed(6));
          // Auto search nearby centers with user location
          searchNearbyCenters(lat, lng);
        },
        (error) => {
          console.error("Geolocation error:", error);
          // Fallback to load all centers if geolocation fails
          loadAllCenters();
        }
      );
    } else {
      // Fallback if geolocation not supported
      loadAllCenters();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load all centers (fallback)
  const loadAllCenters = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await medicalCenterService.getAllCenters({ limit: 100 });
      setCenters(data);
    } catch (err) {
      console.error("Error loading centers:", err);
      setError("Không thể tải danh sách trung tâm y tế. Vui lòng thử lại sau.");
    } finally {
      setLoading(false);
    }
  };

  // Search nearby centers
  const searchNearbyCenters = async (lat: number, lng: number) => {
    try {
      setLoading(true);
      setError(null);

      const request: NearbyRequest = {
        latitude: lat,
        longitude: lng,
        radius,
        services: selectedServices.length > 0 ? selectedServices : undefined,
        limit,
      };

      const response = await medicalCenterService.getNearby(request);
      setCenters(response.centers);

      if (response.centers.length === 0) {
        setError(
          `Không tìm thấy trung tâm y tế trong bán kính ${radius}km. Hãy thử tăng bán kính.`
        );
      }
    } catch (err) {
      console.error("Error searching nearby centers:", err);
      setError("Không thể tìm kiếm trung tâm y tế gần bạn. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  // Handle location update from map component
  const handleLocationUpdate = (lat: number, lng: number) => {
    setUserLocation({ lat, lng });
    setManualLat(lat.toFixed(6));
    setManualLng(lng.toFixed(6));
    searchNearbyCenters(lat, lng);
  };

  // Handle manual search
  const handleManualSearch = () => {
    const lat = parseFloat(manualLat);
    const lng = parseFloat(manualLng);

    if (isNaN(lat) || isNaN(lng)) {
      setError(
        "Vui lòng nhập tọa độ hợp lệ (Vĩ độ: -90 đến 90, Kinh độ: -180 đến 180)"
      );
      return;
    }

    if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
      setError("Tọa độ không hợp lệ. Vĩ độ: -90 đến 90, Kinh độ: -180 đến 180");
      return;
    }

    handleLocationUpdate(lat, lng);
  };

  // Handle service filter change
  const handleServiceChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    setSelectedServices(typeof value === "string" ? value.split(",") : value);
  };

  // Handle view mode change
  const handleViewModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: ViewMode | null
  ) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  return (
    <MainLayout>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box mb={4}>
          <Typography variant="h4" gutterBottom fontWeight={600}>
            🏥 Tìm Trung Tâm Y Tế Hỗ Trợ Sức Khỏe Tâm Thần
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Tìm bệnh viện, phòng khám, và trung tâm tư vấn gần bạn
          </Typography>
        </Box>

        {/* Search Controls */}
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={3} alignItems="center">
            {/* Radius Slider - Main Control */}
            <Grid item xs={12} md={6}>
              <Typography variant="body2" fontWeight={600} gutterBottom>
                📏 Bán kính tìm kiếm: {radius} km
              </Typography>
              <Slider
                value={radius}
                onChange={(_e, value) => {
                  setRadius(value as number);
                  // Auto re-search if user location available
                  if (userLocation) {
                    searchNearbyCenters(userLocation.lat, userLocation.lng);
                  }
                }}
                min={5}
                max={200}
                step={5}
                marks={[
                  { value: 5, label: "5km" },
                  { value: 50, label: "50km" },
                  { value: 100, label: "100km" },
                  { value: 200, label: "200km" },
                ]}
                valueLabelDisplay="auto"
              />
            </Grid>

            {/* Service Filter */}
            <Grid item xs={12} md={6}>
              <FormControl fullWidth size="small">
                <InputLabel>🏥 Lọc theo dịch vụ (tùy chọn)</InputLabel>
                <Select
                  multiple
                  value={selectedServices}
                  onChange={(e) => {
                    handleServiceChange(e);
                    // Auto re-search with new filter
                    if (userLocation) {
                      setTimeout(
                        () =>
                          searchNearbyCenters(
                            userLocation.lat,
                            userLocation.lng
                          ),
                        100
                      );
                    }
                  }}
                  label="🏥 Lọc theo dịch vụ (tùy chọn)"
                  renderValue={(selected) => (
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {AVAILABLE_SERVICES.map((service) => (
                    <MenuItem key={service} value={service}>
                      {service}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Advanced Options - Collapsible */}
            <Grid item xs={12}>
              <Accordion elevation={0} sx={{ bgcolor: "grey.50" }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <TuneIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      Tùy chọn nâng cao (Nhập tọa độ thủ công)
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="Vĩ độ (Latitude)"
                        type="number"
                        value={manualLat}
                        onChange={(e) => setManualLat(e.target.value)}
                        placeholder="Ví dụ: 9.9345"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="Kinh độ (Longitude)"
                        type="number"
                        value={manualLng}
                        onChange={(e) => setManualLng(e.target.value)}
                        placeholder="Ví dụ: 106.3420"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<SearchIcon />}
                        onClick={handleManualSearch}
                        disabled={loading}
                      >
                        Tìm kiếm
                      </Button>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* View Mode Toggle */}
            <Grid item xs={12} md={3}>
              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewModeChange}
                fullWidth
                size="small"
              >
                <ToggleButton value="map">
                  <MapIcon sx={{ mr: 0.5 }} /> Bản đồ
                </ToggleButton>
                <ToggleButton value="list">
                  <ListIcon sx={{ mr: 0.5 }} /> Danh sách
                </ToggleButton>
                <ToggleButton value="both">Cả hai</ToggleButton>
              </ToggleButtonGroup>
            </Grid>
          </Grid>

          {/* Quick Location Buttons */}
          <Stack direction="row" spacing={1} mt={2} flexWrap="wrap">
            <Chip
              label="📍 Trà Vinh (9.9345, 106.3420)"
              onClick={() => {
                setManualLat("9.9345");
                setManualLng("106.3420");
                handleLocationUpdate(9.9345, 106.342);
              }}
              color="primary"
              variant="outlined"
            />
            <Chip
              label="📍 TP.HCM (10.7769, 106.7009)"
              onClick={() => {
                setManualLat("10.7769");
                setManualLng("106.7009");
                handleLocationUpdate(10.7769, 106.7009);
              }}
              color="primary"
              variant="outlined"
            />
          </Stack>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert
            severity="warning"
            sx={{ mb: 3 }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading && (
          <Box display="flex" justifyContent="center" my={4}>
            <CircularProgress />
          </Box>
        )}

        {/* Content */}
        {!loading && (
          <Grid container spacing={3}>
            {/* Map View */}
            {(viewMode === "map" || viewMode === "both") && (
              <Grid item xs={12} md={viewMode === "both" ? 7 : 12}>
                <Paper elevation={2}>
                  <MedicalCenterMap
                    centers={centers}
                    userLocation={userLocation}
                    onLocationUpdate={handleLocationUpdate}
                    selectedCenterForRoute={selectedCenterForRoute}
                  />
                </Paper>
              </Grid>
            )}

            {/* List View */}
            {(viewMode === "list" || viewMode === "both") && (
              <Grid item xs={12} md={viewMode === "both" ? 5 : 12}>
                <Paper
                  elevation={2}
                  sx={{ p: 2, maxHeight: "600px", overflowY: "auto" }}
                >
                  <MedicalCenterList
                    centers={centers}
                    userLocation={userLocation}
                    onCenterClick={(center) => {
                      // Trigger routing on map
                      setSelectedCenterForRoute(center);
                      console.log("Auto routing to:", center.name);
                    }}
                  />
                </Paper>
              </Grid>
            )}
          </Grid>
        )}
      </Container>
    </MainLayout>
  );
};

export default MedicalCentersPage;
