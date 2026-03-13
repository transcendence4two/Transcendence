import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import {
  FriendsIcon,
  UserAddIcon,
  EyeIcon,
  CombatIcon,
  CheckIcon,
  XIcon,
} from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import HelpFab from "../components/common/HelpFab";

type UserData = {
  id: string;
  username: string;
  email: string;
};

type FriendRequest = {
  id: string;
  username: string;
  initials: string;
  color: string;
};

type Friend = {
  id: string;
  username: string;
  initials: string;
  color: string;
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

const mockRequests: FriendRequest[] = [
  {
    id: "1",
    username: "newplayer99",
    initials: "NP",
    color: "bg-blue-500",
  },
  {
    id: "2",
    username: "challenger42",
    initials: "C4",
    color: "bg-purple-500",
  },
];

const mockFriends: Friend[] = [
  {
    id: "1",
    username: "player123",
    initials: "P1",
    color: "bg-blue-500",
    online: true,
  },
  {
    id: "2",
    username: "gamerpro",
    initials: "GP",
    color: "bg-purple-500",
    online: true,
  },
  {
    id: "3",
    username: "gamemaster",
    initials: "GM",
    color: "bg-pink-500",
    online: false,
  },
];

const FriendsPage = () => {
  const navigate = useNavigate();
  const [user] = useState<UserData | null>(getInitialUser);
  const [searchInput, setSearchInput] = useState("");

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  if (!user) return null;

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar icon={FriendsIcon} title="Friends" />

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
                  <button className="friends-page-add-btn">Add</button>
                </div>
              </section>

              {/* ── FRIEND REQUESTS ── */}
              <section className="mb-6">
                <h2 className="friends-page-section-title">
                  <UserAddIcon className="w-6 h-6 text-cyan-400 in-[.light]:brightness-0" />
                  Friend Requests
                  <span className="friends-page-request-badge">
                    {mockRequests.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {mockRequests.map((req) => (
                    <div
                      key={req.id}
                      className="friends-page-friend-request-card"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`${req.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm`}
                        >
                          {req.initials}
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
                        >
                          <CheckIcon className="w-4 h-4" />
                        </button>
                        <button
                          className="friends-page-decline-btn"
                          aria-label={`Decline ${req.username} friend request`}
                        >
                          <XIcon className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* ── MY FRIENDS ── */}
              <section>
                <h2 className="friends-page-section-title">
                  <FriendsIcon className="w-6 h-6 text-cyan-400 in-[.light]:brightness-0" />
                  My Friends
                  <span className="friends-page-friends-badge">
                    {mockFriends.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {mockFriends.map((friend) => (
                    <div key={friend.id} className="friends-page-friend-card">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div
                            className={`${friend.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm`}
                          >
                            {friend.initials}
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
                          disabled={!friend.online}
                          className="friends-page-challenge-btn"
                        >
                          <CombatIcon className="w-4 h-4" />
                          Challenge
                        </button>
                        <button className="friends-page-view-profile-btn">
                          <EyeIcon className="w-4 h-4" />
                          View Profile
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>
          <HelpFab />
        </div>
      </main>
    </div>
  );
};

export default FriendsPage;
