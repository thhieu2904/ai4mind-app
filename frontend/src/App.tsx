import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/common/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import AssessmentPage from "./pages/AssessmentPage";
import ResultsPage from "./pages/ResultsPage";
import ComprehensiveResultsPage from "./pages/ComprehensiveResultsPage";
import VoiceAnalysisPage from "./pages/VoiceAnalysisPage";
import AssessmentHistoryPage from "./pages/AssessmentHistoryPage";
import StatisticsPage from "./pages/StatisticsPage";
import ProfilePage from "./pages/ProfilePage";
import AIChatPage from "./pages/AIChatPage/AIChatPage";
import MedicalCentersPage from "./pages/MedicalCentersPage/MedicalCentersPage";
import CounselorListPage from "./pages/CounselorListPage";
import CounselorChatPage from "./pages/CounselorChatPage";
import SupportHubPage from "./pages/SupportHubPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const theme = createTheme({
  palette: {
    primary: {
      main: "#667eea",
    },
    secondary: {
      main: "#764ba2",
    },
  },
  typography: {
    fontFamily: [
      "-apple-system",
      "BlinkMacSystemFont",
      '"Segoe UI"',
      "Roboto",
      '"Helvetica Neue"',
      "Arial",
      "sans-serif",
    ].join(","),
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              {/* Public Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />

              {/* Protected Routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/assessment"
                element={
                  <ProtectedRoute>
                    <AssessmentPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/assessment/results"
                element={
                  <ProtectedRoute>
                    <ResultsPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/comprehensive-results"
                element={
                  <ProtectedRoute>
                    <ComprehensiveResultsPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/voice-analysis"
                element={
                  <ProtectedRoute>
                    <VoiceAnalysisPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <AssessmentHistoryPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/statistics"
                element={
                  <ProtectedRoute>
                    <StatisticsPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/ai-chat"
                element={
                  <ProtectedRoute>
                    <AIChatPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/support-hub"
                element={
                  <ProtectedRoute>
                    <SupportHubPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/medical-centers"
                element={
                  <ProtectedRoute>
                    <MedicalCentersPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/counselor-list"
                element={
                  <ProtectedRoute>
                    <CounselorListPage />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/counselor-chat/:conversationId"
                element={
                  <ProtectedRoute>
                    <CounselorChatPage />
                  </ProtectedRoute>
                }
              />

              {/* Redirect root to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />

              {/* 404 - Redirect to dashboard */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
