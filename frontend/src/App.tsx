import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
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
import RatingPage from "./pages/RatingPage";
import AdminDashboardPage from "./pages/AdminPage/AdminDashboardPage";
import AdminUsersPage from "./pages/AdminPage/AdminUsersPage";
import CounselorDashboardPage from "./pages/CounselorDashboardPage/CounselorDashboardPage";

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

// Smart root redirect based on role
const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, loading } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  const role = (user?.role as string)?.toUpperCase();
  if (role === "ADMIN") return <Navigate to="/admin/dashboard" replace />;
  if (role === "COUNSELOR") return <Navigate to="/counselor/chats" replace />;
  return <Navigate to="/dashboard" replace />;
};

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

              <Route
                path="/rating"
                element={
                  <ProtectedRoute>
                    <RatingPage />
                  </ProtectedRoute>
                }
              />

              {/* Admin Routes */}
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute>
                    <AdminDashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/users"
                element={
                  <ProtectedRoute>
                    <AdminUsersPage />
                  </ProtectedRoute>
                }
              />

              {/* Counselor Routes */}
              <Route
                path="/counselor/chats"
                element={
                  <ProtectedRoute>
                    <CounselorDashboardPage />
                  </ProtectedRoute>
                }
              />

              {/* Redirect root to role-based home */}
              <Route path="/" element={<RootRedirect />} />

              {/* 404 - Redirect to role-based home */}
              <Route path="*" element={<RootRedirect />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
