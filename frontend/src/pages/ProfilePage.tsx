import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  MoonIcon,
  SunIcon,
  PersonFillIcon,
  ArrowLeftShortIcon,
  QuestionLgIcon,
} from "../components/icons/Icons";

import UserStats from "../components/profile/UserStats";
import MatchHistory from "../components/profile/MatchHistory";
import type { MatchHistoryItem } from "../components/profile/MatchHistory";
import type { UserStatsData } from "../components/profile/UserStats";

type UserProfile = UserStatsData & {
  email?: string;
};

const ProfilePage = () => {
  const { username } = useParams<{ username: string }>();

  const navigate = useNavigate();

  const nick = username ?? "player";
  const initials = nick
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  const [userData, setUserData] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<MatchHistoryItem[]>([]);

  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedTheme = localStorage.getItem("theme");
    return savedTheme ? savedTheme === "dark" : true;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.remove("light");
      localStorage.setItem("theme", "dark");
    } else {
      root.classList.add("light");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  useEffect(() => {
    fetch(`api/users/${nick}`, { credentials: "include" })
      .then((res) => res.json())
      .then((data: unknown) => setUserData((data as UserProfile) ?? null));

    fetch(`api/users/${nick}/matches`, { credentials: "include" })
      .then((res) => res.json())
      .then((data: unknown) =>
        setMatches(Array.isArray(data) ? (data as MatchHistoryItem[]) : []),
      );
  }, [nick]);

  return (
    <div className="container-main">
      <main className="content-main">
        <div className="profile-nav-shell">
          <nav className="profile-nav" aria-label="Profile navigation">
            <button
              type="button"
              onClick={() => navigate("/home")}
              className="profile-nav-btn"
              aria-label="Back"
            >
              <ArrowLeftShortIcon className="profile-nav-arrow" />
            </button>

            <h1 className="profile-nav-title">
              <PersonFillIcon className="profile-nav-icon icon-svg icon-cyan" />
              User Profile
            </h1>

            <button
              type="button"
              onClick={() => setIsDarkMode((prev) => !prev)}
              className="profile-theme-btn"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <SunIcon /> : <MoonIcon />}
            </button>
          </nav>
        </div>

        <div className="profile-page-content">
          <div className="profile-page-layout">
            <div className="profile-page-user-card">
              <div className="profile-page-avatar-wrap">
                <div className="profile-page-avatar" aria-label={`Avatar of ${nick}`}>
                  {initials || "JG"}
                </div>
              </div>

              <div>
                <h2 className="profile-page-name">{nick}</h2>
                <p className="profile-page-email">
                  {userData?.email ?? "example@email.com"}
                </p>
              </div>
            </div>

            <section className="profile-page-section-card">
              <h3 className="profile-section-title">STATS</h3>
              <UserStats username={nick} stats={userData} />
            </section>

            <section className="profile-page-section-card">
              <h3 className="profile-section-title">RECENT HISTORY</h3>
              <MatchHistory username={nick} matches={matches} />
            </section>
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
