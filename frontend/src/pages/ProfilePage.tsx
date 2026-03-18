import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { normalizeAvatarUrl } from "../utils";
import {
  TrophyIcon,
  BullseyeIcon,
  GraphUpArrowIcon,
  GamepadIcon,
  UserIconUntitledUi,
} from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import Footer from "../components/layout/Footer";
import StatGrid from "../components/common/StatGrid";
import MatchHistory from "../components/profile/MatchHistory";
import type { MatchHistoryItem } from "../components/profile/MatchHistory";

type UserData = {
  id: string;
  username: string;
  email: string;
  avatar_url?: string;
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
  const [remoteProfileState, setRemoteProfileState] = useState<{
    requestedUserId: string;
    user: UserData | null;
    loaded: boolean;
  }>({ requestedUserId: "", user: null, loaded: false });
  const [avatarLoadError, setAvatarLoadError] = useState(false);
  const targetUserId = searchParams.get("id")?.trim() ?? "";
  const effectiveUserId = targetUserId || loggedUser?.id || "";
  const isOwnProfile = Boolean(loggedUser && effectiveUserId === loggedUser.id);
  const user = isOwnProfile
    ? loggedUser
    : remoteProfileState.requestedUserId === effectiveUserId
      ? remoteProfileState.user
      : null;
  const isLoadingProfile =
    !isOwnProfile &&
    (!remoteProfileState.loaded ||
      remoteProfileState.requestedUserId !== effectiveUserId);

  const avatarImageUrl = normalizeAvatarUrl(user?.avatar_url);
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
    if (!loggedUser) {
      navigate("/login", { replace: true });
    }
  }, [loggedUser, navigate]);

  useEffect(() => {
    if (!loggedUser || isOwnProfile) return;

    const token = localStorage.getItem("access_token");

    fetch(`/api/users/${effectiveUserId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data: UserData) => {
        setRemoteProfileState({
          requestedUserId: effectiveUserId,
          user: data,
          loaded: true,
        });
      })
      .catch(() => {
        setRemoteProfileState({
          requestedUserId: effectiveUserId,
          user: null,
          loaded: true,
        });
      });
  }, [effectiveUserId, isOwnProfile, loggedUser]);

  useEffect(() => {
    if (!user) return;
    const token = localStorage.getItem("access_token");

    fetch(`/api/tournaments/stats/players/${user.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data: PlayerStats) => setStats(data))
      .catch(() => setStats(null));

    fetch(`/api/tournaments/stats/players/${user.id}/matches`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(async (data: unknown) => {
        if (!Array.isArray(data)) {
          setMatches([]);
          return;
        }

        type MatchPlayerRaw = {
          user_id: string;
          is_winner: boolean;
          display_name?: string;
          score: number;
        };
        type MatchRecordRaw = { players?: MatchPlayerRaw[] };

        const rawMatches = data as MatchRecordRaw[];

        // Resolve opponent usernames to avoid displaying user_hash_id
        const uniqueOpponentIds = Array.from(
          new Set(
            rawMatches
              .map((matchData) => {
                const opponents = matchData.players?.find((p) => p.user_id !== user.id);
                return opponents?.user_id;
              })
              .filter(Boolean) as string[]
          )
        );

        const opponentMap: Record<string, string> = {};
        await Promise.allSettled(
          uniqueOpponentIds.map(async (id) => {
            try {
              const res = await fetch(`/api/users/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
              });
              if (res.ok) {
                const userData: UserData & { deleted?: boolean } = await res.json();
                if (userData?.username && !userData.deleted) {
                  opponentMap[id] = userData.username;
                } else {
                  opponentMap[id] = `#${id.slice(0, 8)}`;
                }
              } else {
                opponentMap[id] = `#${id.slice(0, 8)}`;
              }
            } catch {
              opponentMap[id] = `#${id.slice(0, 8)}`;
            }
          })
        );

        const history: MatchHistoryItem[] = rawMatches.map((matchData) => {
          const players = matchData.players || [];
          const playerSnapshot = players.find((p) => p.user_id === user.id);
          const opponentSnapshot = players.find((p) => p.user_id !== user.id);

          const result = (playerSnapshot && playerSnapshot.is_winner) ? "win" : "loss";
          const resolvedUsername = opponentSnapshot?.user_id
            ? opponentMap[opponentSnapshot.user_id]
            : undefined;

          return {
            result,
            opponent: {
              username: resolvedUsername || opponentSnapshot?.display_name || `#${opponentSnapshot?.user_id?.slice(0, 8) ?? "unknown"}`,
              score: opponentSnapshot?.score || 0
            },
            player: {
              score: playerSnapshot?.score || 0
            }
          };
        });

        setMatches(history);
      })
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

        </div>
      </main>
      <Footer />
    </div>
  );
};

export default ProfilePage;
