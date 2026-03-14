import { useState, useEffect, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";

import { GearIcon, UserIconUntitledUi } from "../components/icons/Icons";
import PageNavbar from "../components/common/PageNavbar";
import Button from "../components/common/Button";

interface UserData {
  id: string;
  username: string;
  email: string;
  profileImageUrl?: string;
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
  const [confirmPassword, setConfirmPassword] = useState("");

  const [tempImageFile, setTempImageFile] = useState<File | null>(null);
  const [tempPreviewUrl, setTempPreviewUrl] = useState<string>("");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<
    string | null
  >(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  if (!user) return null;

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setTempImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setTempPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setPasswordError(null);
    setConfirmPasswordError(null);
    setSuccess(false);

    const token = localStorage.getItem("access_token");
    const body: Record<string, string> = {};
    if (username !== user.username) body.username = username;
    if (email !== user.email) body.email = email;

    if (password.length > 0 || confirmPassword.length > 0) {
      if (password !== confirmPassword) {
        setConfirmPasswordError("Passwords do not match");
        setSaving(false);
        return;
      }

      if (password.length < 6) {
        setPasswordError("Password must have at least 6 characters");
        setSaving(false);
        return;
      }

      if (password.length > 255) {
        setPasswordError("Password must not exceed 255 characters");
        setSaving(false);
        return;
      }

      body.password = password;
    }

    try {
      let currentProfileImageUrl = user.profileImageUrl;

      if (tempImageFile) {
        const formData = new FormData();
        formData.append("file", tempImageFile);

        const avatarRes = await fetch("/api/users/me/avatar", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        if (!avatarRes.ok) {
          const data = await avatarRes.json().catch(() => ({}));
          throw new Error(data.detail || "Failed to upload avatar.");
        }

        const avatarData = await avatarRes.json();
        currentProfileImageUrl = avatarData.avatar_url;
      }

      if (Object.keys(body).length > 0) {
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

        const updated = await res.json();
        const newUserData = {
          ...user,
          username: updated.username,
          email: updated.email,
          profileImageUrl: currentProfileImageUrl,
        };
        localStorage.setItem("user", JSON.stringify(newUserData));
        setUser(newUserData);
      } else if (tempImageFile) {
        const newUserData = {
          ...user,
          profileImageUrl: currentProfileImageUrl,
        };
        localStorage.setItem("user", JSON.stringify(newUserData));
        setUser(newUserData);
      }

      setTempImageFile(null);
      setTempPreviewUrl("");
      setPassword("");
      setConfirmPassword("");
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setSaving(false);
    }
  };

  const currentAvatarUrl =
    tempPreviewUrl || user.profileImageUrl || "/default-avatar.png";

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
                <div className="settings-avatar-edit-modern">
                  <div className="settings-avatar-container">
                    <div className="settings-avatar-circle">
                      <img
                        src={currentAvatarUrl}
                        alt="Profile Preview"
                        className="settings-avatar-img-modern"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src =
                            "/default-avatar.png";
                        }}
                      />
                    </div>
                    <label
                      htmlFor="avatar-upload"
                      className="settings-edit-btn-modern"
                    >
                      <svg
                        className="settings-edit-icon"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                      Edit
                    </label>
                    <input
                      id="avatar-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      style={{ display: "none" }}
                    />
                  </div>
                  <span className="settings-hint">
                    JPG or PNG. Max 5MB.
                  </span>
                </div>

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
                  {passwordError && (
                    <p className="settings-error">{passwordError}</p>
                  )}
                  <span className="settings-hint">
                    Leave blank to keep the current password
                  </span>
                </div>

                <div className="settings-field-group">
                  <label className="settings-label">Confirm Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                    className="settings-input"
                  />
                  {confirmPasswordError && (
                    <p className="settings-error">{confirmPasswordError}</p>
                  )}
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
