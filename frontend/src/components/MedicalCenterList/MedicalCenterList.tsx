/**
 * Medical Center List Component
 * Hiển thị danh sách medical centers dạng cards với filter và sort
 */

import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  Alert,
} from "@mui/material";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import PhoneIcon from "@mui/icons-material/Phone";
import EmailIcon from "@mui/icons-material/Email";
import LanguageIcon from "@mui/icons-material/Language";
import DirectionsIcon from "@mui/icons-material/Directions";
import { MedicalCenter } from "../../services/medicalCenterService";

interface MedicalCenterListProps {
  centers: MedicalCenter[];
  onCenterClick?: (center: MedicalCenter) => void;
  userLocation?: { lat: number; lng: number } | null;
}

const MedicalCenterList: React.FC<MedicalCenterListProps> = ({
  centers,
  onCenterClick,
  userLocation,
}) => {
  // Handle open Google Maps directions
  const handleGetDirections = (center: MedicalCenter) => {
    const origin = userLocation
      ? `${userLocation.lat},${userLocation.lng}`
      : "current+location";
    const destination = `${center.latitude},${center.longitude}`;
    const url = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}`;
    window.open(url, "_blank");
  };

  // Render empty state
  if (centers.length === 0) {
    return (
      <Alert severity="info">
        Không tìm thấy trung tâm y tế nào. Hãy thử tăng bán kính tìm kiếm hoặc
        thay đổi bộ lọc.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Tìm thấy {centers.length} trung tâm y tế
      </Typography>

      <Stack spacing={2}>
        {centers.map((center) => (
          <Card
            key={center.id}
            sx={{
              cursor: "pointer",
              transition: "all 0.3s",
              "&:hover": {
                transform: "translateY(-4px)",
                boxShadow: 4,
              },
            }}
            onClick={() => onCenterClick && onCenterClick(center)}
          >
            <CardContent>
              {/* Header: Name + Distance */}
              <Box
                display="flex"
                justifyContent="space-between"
                alignItems="flex-start"
                mb={1}
              >
                <Typography
                  variant="h6"
                  component="div"
                  sx={{ flex: 1, fontWeight: 600 }}
                >
                  {center.name}
                </Typography>
                {center.distance !== undefined && center.distance !== null && (
                  <Chip
                    label={`${center.distance.toFixed(2)} km`}
                    color="primary"
                    size="small"
                    sx={{ ml: 1 }}
                  />
                )}
              </Box>

              {/* Address */}
              <Box display="flex" alignItems="flex-start" mb={1}>
                <LocationOnIcon
                  sx={{
                    fontSize: 20,
                    color: "text.secondary",
                    mr: 0.5,
                    mt: 0.2,
                  }}
                />
                <Typography variant="body2" color="text.secondary">
                  {center.address}
                </Typography>
              </Box>

              {/* Contact Info */}
              <Stack direction="row" spacing={2} mb={1.5} flexWrap="wrap">
                {center.phone && (
                  <Box display="flex" alignItems="center">
                    <PhoneIcon
                      sx={{ fontSize: 18, color: "text.secondary", mr: 0.5 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {center.phone}
                    </Typography>
                  </Box>
                )}
                {center.email && (
                  <Box display="flex" alignItems="center">
                    <EmailIcon
                      sx={{ fontSize: 18, color: "text.secondary", mr: 0.5 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {center.email}
                    </Typography>
                  </Box>
                )}
                {center.website && (
                  <Box display="flex" alignItems="center">
                    <LanguageIcon
                      sx={{ fontSize: 18, color: "text.secondary", mr: 0.5 }}
                    />
                    <Typography
                      variant="body2"
                      color="primary"
                      component="a"
                      href={center.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      sx={{ textDecoration: "none" }}
                    >
                      Website
                    </Typography>
                  </Box>
                )}
              </Stack>

              {/* Services */}
              {center.services && center.services.length > 0 && (
                <Box mb={1}>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                    mb={0.5}
                  >
                    Dịch vụ:
                  </Typography>
                  <Stack
                    direction="row"
                    spacing={0.5}
                    flexWrap="wrap"
                    useFlexGap
                  >
                    {center.services.slice(0, 4).map((service, index) => (
                      <Chip
                        key={index}
                        label={service}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {center.services.length > 4 && (
                      <Chip
                        label={`+${center.services.length - 4}`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Stack>
                </Box>
              )}

              {/* Description */}
              {center.description && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                    mb: 1,
                  }}
                >
                  {center.description}
                </Typography>
              )}

              {/* Actions */}
              <Box display="flex" justifyContent="flex-end" mt={1}>
                <Tooltip title="Chỉ đường trên Google Maps">
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGetDirections(center);
                    }}
                  >
                    <DirectionsIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Box>
  );
};

export default MedicalCenterList;
