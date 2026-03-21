import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useEffect } from "react";
import ProtectedRoute from "./components/ProtectedRoute";
import HomePage from "./pages/HomePage";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import TFAPage from "./pages/TFAPage";
import DashboardPage from "./pages/DashboardPage";
import MatchmakingPage from "./pages/MatchmakingPage";
import GamePage from "./pages/GamePage";
import ProfilePage from "./pages/ProfilePage";
import FriendsPage from "./pages/FriendsPage";
import ProfileSettingsPage from "./pages/ProfileSettingsPage";
import OAuthCallbackPage from "./pages/OAuthCallbackPage";
import NotFoundPage from "./pages/NotFoundPage";

function PresenceHeartbeat() {
  const location = useLocation();

  useEffect(() => {
    let isMounted = true;

    const sendHeartbeat = async () => {
      if (!isMounted) return;

      const token = localStorage.getItem("access_token");
      const user = localStorage.getItem("user");
      if (!token || !user) return;

      await fetch("/api/users/presence/heartbeat", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }).catch(() => {
        // Ignore heartbeat failures; next cycle/navigation will retry.
      });
    };

    // Send as soon as route changes (important for SPA logins, e.g. OAuth callback).
    void sendHeartbeat();

    const intervalId = window.setInterval(() => {
      void sendHeartbeat();
    }, 25000);

    const onVisible = () => {
      if (document.visibilityState === "visible") {
        void sendHeartbeat();
      }
    };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [location.pathname]);

  return null;
}

function App() {
  return (
    <BrowserRouter>
      <PresenceHeartbeat />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/verify-otp" element={<TFAPage />} />
        <Route path="/home" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/matchmaking" element={<ProtectedRoute><MatchmakingPage /></ProtectedRoute>} />
        <Route path="/game/:sessionId" element={<ProtectedRoute><GamePage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        <Route path="/friends" element={<ProtectedRoute><FriendsPage /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><ProfileSettingsPage /></ProtectedRoute>} />
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
