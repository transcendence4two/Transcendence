import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  PersonFillIcon,
  QuestionLgIcon,
  TrophyFillIcon,
  BullseyeFillIcon,
  GraphUpArrowFillIcon,
  ControllerFillIcon,
} from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import StatGrid from "../components/common/StatGrid";
import MatchHistory from "../components/profile/MatchHistory";
import type { MatchHistoryItem } from "../components/profile/MatchHistory";

type UserData = {
  id: string;
  username: string;
  email: string;
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
  const [user] = useState<UserData | null>(getInitialUser);
  const nick = user?.username ?? "player";
  const initials = nick
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [matches, setMatches] = useState<MatchHistoryItem[]>([]);

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

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

  if (!user) return null;

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
      icon: <TrophyFillIcon className="stat-icon icon-svg icon-emerald" />,
      value: wins !== null ? String(wins) : "N/A",
      label: "Wins",
      color: "text-emerald-400",
    },
    {
      icon: <BullseyeFillIcon className="stat-icon icon-svg icon-rose" />,
      value: losses !== null ? String(losses) : "N/A",
      label: "Losses",
      color: "text-rose-400",
    },
    {
      icon: <GraphUpArrowFillIcon className="stat-icon icon-svg icon-blue" />,
      value: winRate ?? "N/A",
      label: "Win Rate",
      color: "text-blue-400",
    },
    {
      icon: <ControllerFillIcon className="stat-icon icon-svg icon-cyan" />,
      value: total !== null ? String(total) : "N/A",
      label: "Total Games",
      color: "text-cyan-400",
    },
  ];

  return (
    <div className="container-main">
      <main className="content-main">
        <PageNavbar title="User Profile" icon={PersonFillIcon} />

        <div className="profile-page-content">
          <div className="profile-page-layout">
            <div className="profile-page-user-card">
              <div className="profile-page-avatar-wrap">
                <div
                  className="profile-page-avatar"
                  aria-label={`Avatar of ${nick}`}
                >
                  {initials || "JG"}
                </div>
              </div>

              <div>
                <h2 className="profile-page-name">{nick}</h2>
                <p className="profile-page-email">{user.email}</p>
              </div>
            </div>

            <StatGrid
              title="STATS"
              className="profile-page-section-card"
              stats={statItems}
              columns={4}
            />

            <MatchHistory
              className="profile-page-section-card"
              title="RECENT HISTORY"
              username={nick}
              matches={matches}
            />
          </div>

          <button type="button" className="profile-help-fab" aria-label="Help">
            <QuestionLgIcon className="profile-help-icon icon-white" />
          </button>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
