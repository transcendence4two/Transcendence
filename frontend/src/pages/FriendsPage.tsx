import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import { FriendsIcon, UserAddIcon, EyeIcon } from "../components/icons/Icons";

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
  timeAgo: string;
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
    timeAgo: "2 horas atrás",
  },
  {
    id: "2",
    username: "challenger42",
    initials: "C4",
    color: "bg-purple-500",
    timeAgo: "5 horas atrás",
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
                <h2 className="flex items-center gap-2 text-gray-400 font-semibold text-sm uppercase tracking-widest mb-3">
                  <UserAddIcon className="w-6 h-6 text-cyan-400" />
                  Add Friend
                </h2>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Username"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="flex-1 bg-[#0d1b2a] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/30 text-sm focus:outline-none focus:border-white/15 transition-colors duration-500"
                  />
                  <button className="bg-linear-to-r from-cyan-500 to-blue-600 text-white font-semibold px-5 py-1 rounded-xl text-sm hover:opacity-80 transition-all">
                    Add
                  </button>
                </div>
              </section>

              {/* ── FRIEND REQUESTS ── */}
              <section className="mb-6">
                <h2 className="flex items-center gap-2 text-gray-400 font-semibold text-sm uppercase tracking-widest mb-3">
                  <UserAddIcon className="w-6 h-6 text-cyan-400" />
                  Friend Requests
                  <span className="bg-linear-to-r from-cyan-500 to-blue-600 text-white text-xs font-bold rounded-xl w-5 h-4.5 flex items-center justify-center ml-1">
                    {mockRequests.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {mockRequests.map((req) => (
                    <div
                      key={req.id}
                      className="flex items-center justify-between bg-[#0d1b2a] border border-white/10 rounded-xl px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`${req.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm`}
                        >
                          {req.initials}
                        </div>
                        <div>
                          <p className="text-white font-medium text-sm">
                            {req.username}
                          </p>
                          <p className="text-white/40 text-xs">{req.timeAgo}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button className="bg-green-500 hover:bg-green-700 text-white font-bold px-4 py-1.5 rounded-lg text-sm transition-colors">
                          Accept
                        </button>
                        <button className="bg-red-500 hover:bg-red-700 text-white font-bold px-4 py-1.5 rounded-lg text-sm transition-colors">
                          Decline
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* ── MY FRIENDS ── */}
              <section>
                <h2 className="flex items-center gap-2 text-gray-400 font-semibold text-sm uppercase tracking-widest mb-3">
                  <FriendsIcon className="w-6 h-6 text-cyan-400" />
                  My Friends
                  <span className="bg-gray-600 text-white text-xs font-bold rounded-xl w-5 h-4.5 flex items-center justify-center ml-1">
                    {mockFriends.length}
                  </span>
                </h2>

                <div className="flex flex-col gap-2">
                  {mockFriends.map((friend) => (
                    <div
                      key={friend.id}
                      className="flex items-center justify-between bg-[#0d1b2a] border border-white/10 rounded-xl px-4 py-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <div
                            className={`${friend.color} w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm`}
                          >
                            {friend.initials}
                          </div>
                          <span
                            className={`absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-[#0d1b2a] ${friend.online ? "bg-green-400" : "bg-gray-500"}`}
                          />
                        </div>
                        <div>
                          <p className="text-white font-medium text-sm">
                            {friend.username}
                          </p>
                          <p
                            className={`text-xs ${friend.online ? "text-green-400" : "text-white/40"}`}
                          >
                            {friend.online ? "Online" : "Offline"}
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          disabled={!friend.online}
                          className="flex items-center gap-1.5 bg-linear-to-r from-cyan-500 via-blue-500 to-blue-400 bg-[length:200%_auto] bg-left disabled:bg-none disabled:bg-white/10 disabled:text-white/30 text-white font-semibold px-4 py-1.5 rounded-lg text-sm transition-all duration-600 hover:bg-right"
                        >
                          Challenge
                        </button>
                        <button className="flex items-center gap-1.5 bg-white/10 hover:bg-white/20 text-white font-semibold px-4 py-1.5 rounded-lg text-sm transition-colors">
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
