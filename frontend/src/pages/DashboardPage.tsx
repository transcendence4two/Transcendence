import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../components/layout/Footer";
import Button from "../components/common/Button";
import StatGrid from "../components/common/StatGrid";
import PageNavbar from "../components/common/PageNavbar";
import TicTacToeAnimation from "../components/common/TicTacToeAnimation";
import {
  TrophyFillIcon,
  BullseyeFillIcon,
  GraphUpArrowFillIcon,
  ControllerFillIcon,
} from "../components/icons/Icons";

interface UserData {
  id: string;
  username: string;
  email: string;
}

interface PlayerStats {
  wins: number;
  losses: number;
  matches_played: number;
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

const DashboardPage = () => {
  const navigate = useNavigate();
  const [user] = useState<UserData | null>(getInitialUser);
  const [stats, setStats] = useState<PlayerStats | null>(null);

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
  }, [user]);

  if (!user) return null;

  const initials = user.username
    .split(/[\s_-]/)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("")
    .slice(0, 2);

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
      <PageNavbar />
      <main className="content-main dashboard-main">
        <div className="dashboard-layout">
          {/* Profile Card */}
          <div className="dashboard-card dashboard-profile-card">
            <div className="dashboard-card-content">
              {/* Avatar */}
              <div className="dashboard-avatar-wrap">
                <div className="dashboard-avatar">
                  {initials}
                </div>
              </div>

              {/* User Info */}
              <div>
                <h2 className="dashboard-user-name">
                  {user.username}
                </h2>
                <p className="dashboard-user-email">
                  {user.email}
                </p>
              </div>
            </div>
          </div>

          {/* Start Game Card */}
          <div className="dashboard-card dashboard-game-card">
            <div className="dashboard-game-animation-bg">
              <TicTacToeAnimation />
            </div>

            <div className="dashboard-game-content">
              <h3 className="dashboard-game-title">
                <span>🎮</span> Play a Game
              </h3>
              <p className="dashboard-game-text">
                Ready for a match?
              </p>
            </div>

            <Button
              className="dashboard-play-btn"
              onClick={() => alert("Game feature coming soon!")}
            >
              <span>🎮</span> Play
            </Button>
          </div>

          <StatGrid title="Stats" stats={statItems} columns={4} />
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default DashboardPage;
