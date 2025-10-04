import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  Typography,
  Box,
} from "@mui/material";
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
} from "@mui/icons-material";

export type AlertType = "success" | "info" | "warning" | "error";

interface AlertModalProps {
  open: boolean;
  onClose: () => void;
  type: AlertType;
  title: string;
  message: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  showCancel?: boolean;
}

const alertIcons = {
  success: <SuccessIcon />,
  info: <InfoIcon />,
  warning: <WarningIcon />,
  error: <ErrorIcon />,
};

const AlertModal: React.FC<AlertModalProps> = ({
  open,
  onClose,
  type,
  title,
  message,
  confirmText = "Đồng ý",
  cancelText = "Hủy",
  onConfirm,
  showCancel = false,
}) => {
  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: 3,
        },
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Box display="flex" alignItems="center" gap={1.5}>
          {alertIcons[type]}
          <Typography variant="h6" component="span">
            {title}
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity={type} variant="outlined" sx={{ mt: 1 }}>
          {typeof message === "string" ? (
            <Typography variant="body1">{message}</Typography>
          ) : (
            message
          )}
        </Alert>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        {showCancel && (
          <Button onClick={onClose} variant="outlined" color="inherit">
            {cancelText}
          </Button>
        )}
        <Button
          onClick={handleConfirm}
          variant="contained"
          color={type === "error" ? "error" : "primary"}
          autoFocus
        >
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AlertModal;
