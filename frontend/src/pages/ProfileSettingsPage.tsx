import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { GearIcon, UserIconUntitledUi } from "../components/icons/Icons";
import PageNavbar from "../components/common/PageNavbar";
import Button from "../components/common/Button";

interface UserData {
  id: string;
  username: string;
  email: string;
}

function getInitialUser(): UserData | null {
  const token = localStorage.getItem("access_token");
  const userData = localStorage.getItem("user");

  if (!token || !userData) return null;
  try {
    return JSON.parse(userData);
  } catch {
    return null;
  }
}

const ProfileSettingsPage = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserData | null>(getInitialUser);

  const [username, setUsername] = useState(
    () => getInitialUser()?.username ?? "",
  );
  const [email, setEmail] = useState(() => getInitialUser()?.email ?? "");
  const [password, setPassword] = useState("");
  const [profileImage, setProfileImage] = useState("");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  if (!user) return null;

  const handleSave = async (e: React.SubmitEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    const token = localStorage.getItem("access_token");
    const body: Record<string, string> = {};
    if (username !== user.username) body.username = username;
    if (email !== user.email) body.email = email;

    if (Object.keys(body).length === 0) {
      setSaving(false);
      setSuccess(true);
      return;
    }

    try {
      const res = await fetch(`/api/users/${user.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Error saving changes.",
        );
      }

      const updated: UserData = await res.json();
      const newUserData = {
        ...user,
        username: updated.username,
        email: updated.email,
      };
      localStorage.setItem("user", JSON.stringify(newUserData));
      setUser(newUserData);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar title="Settings" icon={GearIcon} />

        <div className="settings-page-content">
          <div className="settings-page-layout">
            <div className="settings-page-card">
              <header className="settings-card-header">
                <UserIconUntitledUi className="profile-nav-icon icon-svg icon-cyan" />
                <h2 className="settings-card-title">Profile</h2>
              </header>

              <form onSubmit={handleSave} className="settings-form">
                <div className="settings-field-group">
                  <label className="settings-label">Username</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="settings-input"
                  />
                </div>

                <div className="settings-field-group">
                  <label className="settings-label">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="settings-input"
                  />
                </div>

                <div className="settings-field-group">
                  <label className="settings-label">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="New password"
                    className="settings-input"
                  />
                  <span className="settings-hint">
                    Leave blank to keep the current password
                  </span>
                </div>

                <div className="settings-field-group">
                  <label className="settings-label">Profile Image</label>
                  <input
                    type="url"
                    value={profileImage}
                    onChange={(e) => setProfileImage(e.target.value)}
                    placeholder="https://link.to/your-profile-image"
                    className="settings-input"
                  />
                  <span className="settings-hint">
                    Add a URL for your profile image
                  </span>
                </div>

                {error && <p className="settings-error">{error}</p>}
                {success && (
                  <p className="settings-success">
                    Changes saved successfully!
                  </p>
                )}

                <Button
                  type="submit"
                  disabled={saving}
                  className="settings-save-btn"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfileSettingsPage;
