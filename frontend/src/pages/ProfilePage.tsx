import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  TrophyIcon,
  BullseyeIcon,
  GraphUpArrowIcon,
  GamepadIcon,
  UserIconUntitledUi,
} from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import StatGrid from "../components/common/StatGrid";
import MatchHistory from "../components/profile/MatchHistory";
import HelpFab from "../components/common/HelpFab";
import type { MatchHistoryItem } from "../components/profile/MatchHistory";

type UserData = {
  id: string;
  username: string;
  email: string;
  profileImageUrl?: string;
};

type PlayerStats = {
  wins: number;
  losses: number;
  matches_played: number;
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

const ProfilePage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loggedUser] = useState<UserData | null>(getInitialUser);
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [avatarLoadError, setAvatarLoadError] = useState(false);
  const avatarImageUrl = (user?.profileImageUrl ?? "").trim();
  const nick = user?.username ?? "player";
  const initials = nick
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [matches, setMatches] = useState<MatchHistoryItem[]>([]);

  const targetUserId = searchParams.get("id")?.trim() ?? "";

  useEffect(() => {
    if (!loggedUser) {
      navigate("/login", { replace: true });
    }
  }, [loggedUser, navigate]);

  useEffect(() => {
    if (!loggedUser) return;

    const token = localStorage.getItem("access_token");
    const effectiveUserId = targetUserId || loggedUser.id;

    if (effectiveUserId === loggedUser.id) {
      setUser(loggedUser);
      setIsLoadingProfile(false);
      return;
    }

    setIsLoadingProfile(true);
    fetch(`/api/users/${effectiveUserId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data: UserData) => setUser(data))
      .catch(() => setUser(null))
      .finally(() => setIsLoadingProfile(false));
  }, [loggedUser, targetUserId]);

  useEffect(() => {
    if (!user) return;
    const token = localStorage.getItem("access_token");

    fetch(`/api/tournaments/stats/players/${user.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data: PlayerStats) => setStats(data))
      .catch(() => setStats(null));

    fetch(`/api/users/${user.username}/matches`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data: unknown) =>
        setMatches(Array.isArray(data) ? (data as MatchHistoryItem[]) : []),
      )
      .catch(() => setMatches([]));
  }, [user]);

  useEffect(() => {
    if (!user) return;

    const timeout = setTimeout(() => {
      setAvatarLoadError(false);
    }, 0);

    return () => clearTimeout(timeout);
  }, [avatarImageUrl, user]);

  if (!loggedUser || isLoadingProfile || !user) return null;

  const wins = stats?.wins ?? null;
  const losses = stats?.losses ?? null;
  const total = wins !== null && losses !== null ? wins + losses : null;
  const winRate =
    total !== null && total > 0
      ? `${Math.round((wins! / total) * 100)}%`
      : total === 0
        ? "0%"
        : null;

  const statItems = [
    {
      icon: <TrophyIcon className="stat-icon icon-svg icon-emerald" />,
      value: wins !== null ? String(wins) : "N/A",
      color: "text-emerald-400",
      label: "Wins",
    },
    {
      icon: <BullseyeIcon className="stat-icon icon-svg icon-rose" />,
      value: losses !== null ? String(losses) : "N/A",
      color: "text-rose-400",
      label: "Losses",
    },
    {
      icon: <GraphUpArrowIcon className="stat-icon icon-svg icon-blue" />,
      value: winRate ?? "N/A",
      color: "text-blue-400",
      label: "Win Rate",
    },
    {
      icon: <GamepadIcon className="stat-icon icon-svg icon-cyan" />,
      value: total !== null ? String(total) : "N/A",
      color: "text-cyan-400",
      label: "Total Games",
    },
  ];

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar
          title="User Profile"
          icon={UserIconUntitledUi}
          showHamburgerMenu
        />

        <div className="profile-page-content">
          <div className="profile-page-layout">
            <div className="profile-page-user-card">
              <div className="profile-page-avatar-wrap">
                <div
                  className="profile-page-avatar"
                  aria-label={`Avatar of ${nick}`}
                >
                  {avatarImageUrl && !avatarLoadError ? (
                    <img
                      src={avatarImageUrl}
                      alt={`Avatar of ${nick}`}
                      className="profile-page-avatar-image"
                      onLoad={() => setAvatarLoadError(false)}
                      onError={() => setAvatarLoadError(true)}
                    />
                  ) : (
                    initials || "JG"
                  )}
                </div>
              </div>

              <div>
                <h2 className="profile-page-name">{nick}</h2>
                <p className="profile-page-email">{user.email}</p>
              </div>

              <StatGrid title="STATS" stats={statItems} columns={4} />

              <MatchHistory
                title="RECENT HISTORY"
                username={nick}
                matches={matches}
              />
            </div>
          </div>

          <HelpFab />
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
