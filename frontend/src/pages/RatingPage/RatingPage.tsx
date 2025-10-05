/**
 * RatingPage - Embedded Google Form for app rating
 */
import React from "react";
import { Box, Container } from "@mui/material";
import MainLayout from "../../components/layout/MainLayout/MainLayout";

const RatingPage: React.FC = () => {
  const googleFormUrl = import.meta.env.VITE_GOOGLE_FORM_URL;

  return (
    <MainLayout>
      <Container
        maxWidth={false}
        disableGutters
        sx={{
          height: "calc(100vh - 64px - 56px)", // Trừ header (64px) và bottom nav (56px)
          display: "flex",
          flexDirection: "column",
          p: 0,
        }}
      >
        <Box
          sx={{
            flex: 1,
            width: "100%",
            height: "100%",
          }}
        >
          <iframe
            src={googleFormUrl}
            width="100%"
            height="100%"
            frameBorder="0"
            marginHeight={0}
            marginWidth={0}
            title="Rating Form"
            style={{
              border: "none",
              display: "block",
            }}
          >
            Đang tải form đánh giá...
          </iframe>
        </Box>
      </Container>
    </MainLayout>
  );
};

export default RatingPage;
