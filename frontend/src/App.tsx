import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import RegisterPage from "./pages/RegisterPage";
import LoginPage from "./pages/LoginPage";
import TFAPage from "./pages/TFAPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
<<<<<<< HEAD
import FriendsPage from "./pages/FriendsPage";
=======
import ProfileSettingsPage from "./pages/ProfileSettingsPage";
>>>>>>> 3cd06f7e36bf73c80781ec3c203e07f30c3e6e85

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
        <Route path="/profile" element={<ProfilePage />} />
<<<<<<< HEAD
        <Route path="/friends" element={<FriendsPage />} />
=======
        <Route path="/settings" element={<ProfileSettingsPage />} />
>>>>>>> 3cd06f7e36bf73c80781ec3c203e07f30c3e6e85
      </Routes>
    </BrowserRouter>
  );
}

export default App;
