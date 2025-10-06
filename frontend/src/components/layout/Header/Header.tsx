import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Snackbar,
  Alert,
} from "@mui/material";
import {
  Person as PersonIcon,
  RateReview as RateReviewIcon,
  Download as DownloadIcon,
  Logout as LogoutIcon,
} from "@mui/icons-material";
import { useAuth } from "../../../contexts/AuthContext";
import "./Header.css";

const Header: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: "success" | "error" | "info" | "warning";
  }>({
    open: false,
    message: "",
    severity: "success",
  });

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const showSnackbar = (
    message: string,
    severity: "success" | "error" | "info" | "warning"
  ) => {
    setSnackbar({ open: true, message, severity });
  };

  const handleRating = () => {
    handleMenuClose();
    navigate("/rating");
  };

  const handleExportData = async () => {
    handleMenuClose();
    try {
      showSnackbar("Đang xuất dữ liệu...", "info");

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/export/user-data`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Export error response:", errorText);
        throw new Error(`Export failed: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AI4Mind_Data_${new Date().toISOString().split("T")[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showSnackbar("Đã xuất dữ liệu thành công!", "success");
    } catch (error) {
      console.error("Export failed:", error);
      showSnackbar("Không thể xuất dữ liệu. Vui lòng thử lại sau.", "error");
    }
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate("/login");
  };

  return (
    <header className="mobile-header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-logo">ai4mind</h1>
        </div>

        <div className="header-right">
          <IconButton
            onClick={handleMenuOpen}
            size="small"
            aria-label="User Profile Menu"
            aria-controls={open ? "user-menu" : undefined}
            aria-haspopup="true"
            aria-expanded={open ? "true" : undefined}
            sx={{ color: "#667eea" }}
          >
            <PersonIcon />
          </IconButton>

          <Menu
            id="user-menu"
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: "bottom",
              horizontal: "right",
            }}
            transformOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 200,
              },
            }}
          >
            <MenuItem onClick={handleRating}>
              <ListItemIcon>
                <RateReviewIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Đánh giá ứng dụng</ListItemText>
            </MenuItem>

            <MenuItem onClick={handleExportData}>
              <ListItemIcon>
                <DownloadIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Xuất dữ liệu cá nhân</ListItemText>
            </MenuItem>

            <Divider />

            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Đăng xuất</ListItemText>
            </MenuItem>
          </Menu>
        </div>
      </div>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </header>
  );
};

export default Header;
