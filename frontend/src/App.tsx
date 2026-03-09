import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import TFAPage from "./pages/TFAPage";
import DashboardPage from "./pages/DashboardPage";
import MatchmakingPage from "./pages/MatchmakingPage";
import GamePage from "./pages/GamePage";
import ProfilePage from "./pages/ProfilePage";
import OAuthCallbackPage from "./pages/OAuthCallbackPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/verify-otp" element={<TFAPage />} />
        <Route path="/home" element={<DashboardPage />} />
        <Route path="/matchmaking" element={<MatchmakingPage />} />
        <Route path="/game/:sessionId" element={<GamePage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
