import { useNavigate } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { normalizeAvatarUrl } from "../utils";

import {
  FriendsIcon,
  UserAddIcon,
  EyeIcon,
  CheckIcon,
  XIcon,
} from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import Footer from "../components/layout/Footer";

type UserData = {
  id: string;
  username: string;
  email: string;
};

type FriendRequest = {
  id: string;
  userId: string;
  username: string;
  initials: string;
  color: string;
  avatarUrl?: string;
};

type Friend = {
  id: string;
  userId: string;
  username: string;
  initials: string;
  color: string;
  online: boolean;
  avatarUrl?: string;
};

type ApiPaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

type ApiFriendRequest = {
  id: string;
  requesterId: string;
  receiverId: string;
  status: string;
};

type ApiFriendship = {
  id: string;
  userId1: string;
  userId2: string;
  active: boolean;
};

type ApiUserProfile = {
  id: string;
  username: string;
  email: string;
  avatar_url?: string | null;
};

type ApiUserPresenceResponse = {
  user_id: string;
  online: boolean;
};

function getInitialUser(): UserData | null {
  const token = localStorage.getItem("access_token");
  const userData = localStorage.getItem("user");
  if (!token || !userData) return null;
  try {
    return JSON.parse(userData) as UserData;
  } catch {
    return null;
  }
}

const avatarColors = [
  "bg-blue-500",
  "bg-purple-500",
  "bg-pink-500",
  "bg-cyan-500",
  "bg-emerald-500",
  "bg-amber-500",
];

function getColorFromSeed(seed: string): string {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return avatarColors[hash % avatarColors.length];
}

function getInitials(username: string): string {
  const initials = username
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");

  return initials || username.slice(0, 2).toUpperCase();
}

function getApiErrorMessage(data: unknown): string | null {
  if (!data || typeof data !== "object") return null;
  const parsed = data as Record<string, unknown>;
  if (typeof parsed.error === "string") return parsed.error;
  if (typeof parsed.detail === "string") return parsed.detail;
  if (typeof parsed.message === "string") return parsed.message;
  return null;
}

const FriendsPage = () => {
  const navigate = useNavigate();
  const [user] = useState<UserData | null>(getInitialUser);
  const [searchInput, setSearchInput] = useState("");
  const [requests, setRequests] = useState<FriendRequest[]>([]);
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingFriend, setAddingFriend] = useState(false);
  const [processingRequestId, setProcessingRequestId] = useState<string | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  const getUserProfileById = useCallback(async (
    userId: string,
  ): Promise<ApiUserProfile> => {
    const response = await fetch(`/api/users/${userId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Could not load user profile");
    }

    return (await response.json()) as ApiUserProfile;
  }, [token]);

  const getUserIdByUsername = async (
    username: string,
  ): Promise<string | null> => {
    const normalized = username.trim().toLowerCase();
    if (!normalized) return null;

    let page = 1;
    const pageSize = 100;

    while (true) {
      const response = await fetch(
        `/api/users/?page=${page}&page_size=${pageSize}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("Could not search users");
      }

      const data =
        (await response.json()) as ApiPaginatedResponse<ApiUserProfile>;
      const found = data.items.find(
        (item) => item.username.toLowerCase() === normalized,
      );

      if (found) return found.id;
      if (data.page >= data.total_pages || data.items.length === 0) return null;

      page += 1;
    }
  };

  const isUserOnline = useCallback(async (userId: string): Promise<boolean> => {
    try {
      const presenceResponse = await fetch(
        `/api/users/${userId}/presence`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!presenceResponse.ok) {
        return false;
      }

      const presenceData =
        (await presenceResponse.json()) as ApiUserPresenceResponse;
      return Boolean(presenceData.online);
    } catch {
      return false;
    }
  }, [token]);

  const resolveOnlineStatuses = useCallback(async (
    userIds: string[],
  ): Promise<Map<string, boolean>> => {
    const statuses = await Promise.all(
      userIds.map(async (id) => [id, await isUserOnline(id)] as const),
    );

    return new Map<string, boolean>(statuses);
  }, [isUserOnline]);

  const loadFriendsData = useCallback(async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const [requestsResponse, friendsResponse] = await Promise.all([
        fetch("/api/friends/requests?page=1&page_size=100", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }),
        fetch("/api/friends/?page=1&page_size=100", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }),
      ]);

      if (!requestsResponse.ok || !friendsResponse.ok) {
        throw new Error("Could not load friends data");
      }

      const requestsData =
        (await requestsResponse.json()) as ApiPaginatedResponse<ApiFriendRequest>;
      const friendsData =
        (await friendsResponse.json()) as ApiPaginatedResponse<ApiFriendship>;

      const requesterIds = requestsData.items.map((item) => item.requesterId);
      const friendUserIds = friendsData.items.map((item) =>
        item.userId1 === user.id ? item.userId2 : item.userId1,
      );
      const userIds = Array.from(new Set([...requesterIds, ...friendUserIds]));

      const onlineByUserId = await resolveOnlineStatuses(friendUserIds);

      const users = await Promise.all(
        userIds.map(async (id) => {
          try {
            const profile = await getUserProfileById(id);
            return [id, { username: profile.username, avatarUrl: normalizeAvatarUrl(profile.avatar_url) || undefined }] as const;
          } catch {
            return [id, { username: `user-${id.slice(0, 8)}` }] as const;
          }
        }),
      );

      const userDataById = new Map<string, { username: string; avatarUrl?: string }>(users);

      const mappedRequests: FriendRequest[] = requestsData.items.map((item) => {
        const userData = userDataById.get(item.requesterId);
        const username = userData?.username ?? "unknown";
        const avatarUrl = userData?.avatarUrl;

        return {
          id: item.id,
          userId: item.requesterId,
          username,
          initials: getInitials(username),
          color: getColorFromSeed(username),
          avatarUrl,
        };
      });

      const mappedFriends: Friend[] = friendsData.items.map((item) => {
        const friendUserId =
          item.userId1 === user.id ? item.userId2 : item.userId1;
        const userData = userDataById.get(friendUserId);
        const username = userData?.username ?? "unknown";
        const avatarUrl = userData?.avatarUrl;

        return {
          id: item.id,
          userId: friendUserId,
          username,
          initials: getInitials(username),
          color: getColorFromSeed(username),
          online: onlineByUserId.get(friendUserId) ?? false,
          avatarUrl,
        };
      });

      setRequests(mappedRequests);
      setFriends(mappedFriends);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }, [getUserProfileById, resolveOnlineStatuses, token, user]);

  useEffect(() => {
    if (!user || !token) return;
    void loadFriendsData();
  }, [loadFriendsData, token, user]);

  const handleAddFriend = async () => {
    if (!user || !token) return;

    setSuccessMessage(null);
    setError(null);

    const targetUsername = searchInput.trim();
    if (!targetUsername) {
      setError("Please enter a username");
      return;
    }

    if (targetUsername.toLowerCase() === user.username.toLowerCase()) {
      setError("You cannot add yourself");
      return;
    }

    setAddingFriend(true);
    try {
      const receiverId = await getUserIdByUsername(targetUsername);
      if (!receiverId) {
        setError("User not found");
        return;
      }

      const response = await fetch("/api/friends/requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ receiverId }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(
          getApiErrorMessage(data) ?? "Could not send friend request",
        );
      }

      setSearchInput("");
      setSuccessMessage("Friend request sent successfully");
      await loadFriendsData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setAddingFriend(false);
    }
  };

  const handleRequestAction = async (
    requestId: string,
    action: "accept" | "reject",
  ) => {
    if (!token) return;

    setError(null);
    setSuccessMessage(null);
    setProcessingRequestId(requestId);

    try {
      const response = await fetch(
        `/api/friends/requests/${requestId}/${action}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );

      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(
          getApiErrorMessage(data) ?? "Could not process request",
        );
      }

      setSuccessMessage(
        action === "accept"
          ? "Friend request accepted"
          : "Friend request declined",
      );
      await loadFriendsData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setProcessingRequestId(null);
    }
  };

  if (!user) return null;

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar icon={FriendsIcon} title="Friends" showHamburgerMenu />

        <div className="friends-page-content">
          <div className="friends-page-layout">
            <div className="friends-page-card">
              {/* ── ADD FRIEND ── */}
              <section className="mb-6">
                <h2 className="friends-page-section-title">
                  <UserAddIcon className="w-6 h-6 text-cyan-400 in-[.light]:brightness-0" />
                  Add Friend
                </h2>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Username"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="friends-page-input"
                  />
                  <button
                    className="friends-page-add-btn"
                    onClick={handleAddFriend}
                    disabled={addingFriend}
                  >
                    {addingFriend ? "Adding..." : "Add"}
                  </button>
                </div>
                {error && <p className="settings-error mt-2">{error}</p>}
                {successMessage && (
                  <p className="settings-success mt-2">{successMessage}</p>
                )}
              </section>

              {/* ── FRIEND REQUESTS ── */}
              <section className="mb-6">
                <h2 className="friends-page-section-title">
                  <UserAddIcon className="w-6 h-6 text-cyan-400 in-[.light]:brightness-0" />
                  Friend Requests
                  <span className="friends-page-request-badge">
                    {requests.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {loading ? (
                    <p className="friends-page-user-status text-sm text-white">
                      Loading...
                    </p>
                  ) : requests.length === 0 ? (
                    <p className="friends-page-user-status text-sm text-gray-400/50">
                      No pending requests
                    </p>
                  ) : (
                    requests.map((req) => (
                      <div
                        key={req.id}
                        className="friends-page-friend-request-card"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`${req.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm overflow-hidden`}
                          >
                            {req.avatarUrl ? (
                              <img
                                src={req.avatarUrl}
                                alt={`Avatar of ${req.username}`}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  (e.target as HTMLImageElement).style.display = 'none';
                                }}
                              />
                            ) : (
                              req.initials
                            )}
                          </div>
                          <div>
                            <p className="friends-page-username">
                              {req.username}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            className="friends-page-accept-btn"
                            aria-label={`Accept ${req.username} friend request`}
                            onClick={() =>
                              void handleRequestAction(req.id, "accept")
                            }
                            disabled={processingRequestId === req.id}
                          >
                            <CheckIcon className="w-4 h-4" />
                          </button>
                          <button
                            className="friends-page-decline-btn"
                            aria-label={`Decline ${req.username} friend request`}
                            onClick={() =>
                              void handleRequestAction(req.id, "reject")
                            }
                            disabled={processingRequestId === req.id}
                          >
                            <XIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>

              {/* ── MY FRIENDS ── */}
              <section>
                <h2 className="friends-page-section-title">
                  <FriendsIcon className="w-6 h-6 text-cyan-400 in-[.light]:brightness-0" />
                  My Friends
                  <span className="friends-page-friends-badge">
                    {friends.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {loading ? (
                    <p className="friends-page-user-status text-sm text-white">
                      Loading...
                    </p>
                  ) : friends.length === 0 ? (
                    <p className="friends-page-user-status text-sm text-gray-400/50">
                      You do not have friends yet
                    </p>
                  ) : (
                    friends.map((friend) => (
                      <div key={friend.id} className="friends-page-friend-card">
                        <div className="flex items-center gap-3">
                          <div className="relative">
                            <div
                              className={`${friend.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm overflow-hidden`}
                            >
                              {friend.avatarUrl ? (
                                <img
                                  src={friend.avatarUrl}
                                  alt={`Avatar of ${friend.username}`}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = 'none';
                                  }}
                                />
                              ) : (
                                friend.initials
                              )}
                            </div>
                            <span
                              className={`friends-page-mini-circle-status absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-[#0d1b2a] ${friend.online ? "bg-green-500" : "bg-gray-500"}`}
                            />
                          </div>
                          <div>
                            <p className="friends-page-username">
                              {friend.username}
                            </p>
                            <p
                              className={`friends-page-user-status text-xs ${friend.online ? "friends-page-user-status-online" : "friends-page-user-status-offline"}`}
                            >
                              {friend.online ? "Online" : "Offline"}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            className="friends-page-view-profile-btn"
                            onClick={() =>
                              navigate(
                                `/profile?&id=${encodeURIComponent(friend.userId)}`,
                              )
                            }
                          >
                            <EyeIcon className="w-4 h-4" />
                            View Profile
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default FriendsPage;
