import { useState, useEffect, useRef, type ChangeEvent } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import { normalizeAvatarUrl } from "../utils";

import { GearIcon, UserIconUntitledUi } from "../components/icons/Icons";
import PageNavbar from "../components/common/PageNavbar";
import Button from "../components/common/Button";

interface UserData {
  id: string;
  username: string;
  email: string;
  avatar_url?: string;
  enable_2fa?: boolean;
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

  const [enable2FA, setEnable2FA] = useState(
    () => getInitialUser()?.enable_2fa ?? false,
  );

  const [tempImageFile, setTempImageFile] = useState<File | null>(null);
  const [tempPreviewUrl, setTempPreviewUrl] = useState<string>("");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<
    string | null
  >(null);
  const [avatarLoadError, setAvatarLoadError] = useState(false);
  const [success, setSuccess] = useState(false);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const deleteModalRef = useRef<HTMLDivElement>(null);

  const DELETE_PHRASE = "Yes, delete my user";

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    if (!showDeleteModal) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowDeleteModal(false);
    };

    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [showDeleteModal]);

  if (!user) return null;

  const initials = user.username
    .split(/[\s_-]/)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 2);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError("File size must be less than 5MB");
        return;
      }

      const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
      if (!allowedTypes.includes(file.type)) {
        setError("Invalid file type. Supported: JPG, PNG, GIF");
        return;
      }

      setError(null);
      setTempImageFile(file);

      const url = URL.createObjectURL(file);

      if (tempPreviewUrl && tempPreviewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(tempPreviewUrl);
      }

      setTempPreviewUrl(url);
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
    const body: Record<string, string | boolean> = {};
    if (username !== user.username) body.username = username;
    if (email !== user.email) body.email = email;
    if (enable2FA !== (user.enable_2fa ?? false)) body.enable_2fa = enable2FA;
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
      let currentAvatarUrl = user.avatar_url;

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
        currentAvatarUrl = avatarData.avatar_url;
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
          enable_2fa: updated.enable_2fa,
          avatar_url: currentAvatarUrl,
        };
        localStorage.setItem("user", JSON.stringify(newUserData));
        setUser(newUserData);
      } else if (tempImageFile) {
        const newUserData = {
          ...user,
          avatar_url: currentAvatarUrl,
        };
        localStorage.setItem("user", JSON.stringify(newUserData));
        setUser(newUserData);
      }

      setTempImageFile(null);
      if (tempPreviewUrl && tempPreviewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(tempPreviewUrl);
      }
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

  const avatarImageUrl = tempPreviewUrl || normalizeAvatarUrl(user?.avatar_url);

  const handleDeleteAccount = async () => {
    if (deleteConfirmText !== DELETE_PHRASE) return;
    setDeleting(true);
    setDeleteError(null);
    const token = localStorage.getItem("access_token");
    try {
      const res = await fetch(`/api/users/${user.id}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ confirmation_text: DELETE_PHRASE }),
      });
      if (!res.ok && res.status !== 204) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to delete account.");
      }
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
      navigate("/login", { replace: true });
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Unexpected error.");
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (deleteModalRef.current && !deleteModalRef.current.contains(e.target as Node)) {
      setShowDeleteModal(false);
    }
  };

  const deleteModal =
    showDeleteModal &&
    createPortal(
      <div
        className="fixed inset-0 z-50 flex items-center justify-center p-6"
        onClick={handleDeleteBackdropClick}
      >
        <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" aria-hidden="true" />
        <div
          ref={deleteModalRef}
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-account-title"
          style={{ width: "100%", maxWidth: "500px", minWidth: "300px" }}
          className="relative flex flex-col rounded-2xl border border-slate-700/50 in-[.light]:border-gray-200 bg-slate-900 in-[.light]:bg-white shadow-2xl"
        >
          <div className="px-6 sm:px-8 py-5 border-b border-slate-700/50 in-[.light]:border-gray-200">
            <h3
              id="delete-account-title"
              className="text-xl font-bold text-white in-[.light]:text-gray-900"
            >
              Delete Account
            </h3>
          </div>

          <div className="px-6 sm:px-8 py-6 space-y-4 text-slate-300 in-[.light]:text-gray-700">
            <p>
              This action is <strong className="text-white in-[.light]:text-gray-900">permanent</strong> and cannot be undone. All your
              data will be deleted.
            </p>
            <p>
              Type <strong className="text-white in-[.light]:text-gray-900">{DELETE_PHRASE}</strong> to confirm:
            </p>
            <input
              type="text"
              value={deleteConfirmText}
              onChange={(e) => setDeleteConfirmText(e.target.value)}
              placeholder={DELETE_PHRASE}
              className="settings-input w-full"
              autoFocus
            />
            {deleteError && <p className="settings-error">{deleteError}</p>}
          </div>

          <div className="flex flex-col-reverse sm:flex-row justify-end gap-3 px-6 sm:px-8 py-5 border-t border-slate-700/50 in-[.light]:border-gray-200 shrink-0">
            <Button
              type="button"
              className="settings-delete-btn"
              disabled={deleteConfirmText !== DELETE_PHRASE || deleting}
              onClick={handleDeleteAccount}
            >
              {deleting ? "Deleting..." : "Confirm Delete"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="px-5 py-2 text-sm font-medium"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>,
      document.body,
    );

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar title="Settings" icon={GearIcon} showHamburgerMenu />

        <div className="settings-page-content">
          <div className="settings-page-layout">
            <div className="settings-page-card">
              <header className="settings-card-header">
                <UserIconUntitledUi className="profile-nav-icon icon-svg icon-cyan" />
                <h2 className="settings-card-title">Profile</h2>
              </header>

              <form onSubmit={handleSave} className="settings-form">
                <div className="flex flex-col items-center gap-4 mb-6">
                  <div className="settings-avatar-container">
                    <div className="settings-avatar-circle">
                      {avatarImageUrl && !avatarLoadError ? (
                        <img
                          src={avatarImageUrl}
                          alt={`Avatar of ${user?.username}`}
                          className="settings-avatar-img-modern"
                          onLoad={() => setAvatarLoadError(false)}
                          onError={() => setAvatarLoadError(true)}
                        />
                      ) : (
                        initials || "JG"
                      )}
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

                <div className="settings-field-group">
                  <label className="settings-label">Two-Factor Authentication</label>
                  <div className="flex items-center gap-3 mt-1">
                    <button
                      type="button"
                      role="switch"
                      aria-checked={enable2FA}
                      onClick={() => setEnable2FA((v) => !v)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${enable2FA ? "bg-cyan-500" : "bg-(--border-color)"}`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${enable2FA ? "translate-x-6" : "translate-x-1"}`}
                      />
                    </button>
                    <span className="settings-hint">
                      {enable2FA ? "Enabled — OTP required at login" : "Disabled"}
                    </span>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={saving}
                  className="settings-save-btn"
                >
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </form>

              <div className="settings-danger-zone">
                <h3 className="settings-danger-title">Delete Account</h3>
                <p className="settings-hint mb-3">
                  Once you delete your account, there is no going back.
                </p>
                <Button
                  type="button"
                  className="settings-delete-btn"
                  onClick={() => {
                    setShowDeleteModal(true);
                    setDeleteConfirmText("");
                    setDeleteError(null);
                  }}
                >
                  Delete Account
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {deleteModal}
    </div>
  );
};

export default ProfileSettingsPage;
