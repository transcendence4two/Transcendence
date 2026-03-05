import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../components/layout/Footer";
import Button from "../components/common/Button";
import StatGrid from "../components/common/StatGrid";
import PageNavbar from "../components/common/PageNavbar";
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
      <main className="content-main flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-2xl space-y-6">
          {/* Profile Card */}
          <div
            className="border border-slate-700/50 in-[.light]:border-gray-200
                        bg-slate-800/50 in-[.light]:bg-white/80
                        backdrop-blur-sm rounded-2xl p-8 text-center space-y-4"
          >
            {/* Avatar */}
            <div className="flex justify-center">
              <div
                className="w-20 h-20 rounded-full bg-linear-to-r from-cyan-400 to-purple-600
                                flex items-center justify-center text-white text-2xl font-bold shadow-lg"
              >
                {initials}
              </div>
            </div>

            {/* User Info */}
            <div>
              <h2 className="text-xl font-bold text-white in-[.light]:text-gray-900">
                {user.username}
              </h2>
              <p className="text-sm text-slate-400 in-[.light]:text-gray-500">
                {user.email}
              </p>
            </div>
          </div>

          {/* Start Game Card */}
          <div
            className="border border-slate-700/50 in-[.light]:border-gray-200
                        bg-slate-800/50 in-[.light]:bg-white/80
                        backdrop-blur-sm rounded-2xl p-6 space-y-4"
          >
            <div>
              <h3 className="text-lg font-semibold text-white in-[.light]:text-gray-900 flex items-center gap-2">
                <span>🎮</span> Play a Game
              </h3>
              <p className="text-sm text-slate-400 in-[.light]:text-gray-500 mt-1">
                Ready for a match?
              </p>
            </div>

            <Button
              className="w-full py-3 text-lg font-semibold shadow-lg hover:shadow-cyan-500/30
                                flex items-center justify-center gap-2"
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
