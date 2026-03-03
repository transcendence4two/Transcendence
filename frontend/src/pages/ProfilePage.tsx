import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { MoonIcon, SunIcon } from "../components/icons/Icons";
import personIcon from "../assets/profile/person.svg";
import arrowLeftIcon from "../assets/profile/arrow-left-short.svg";
import questionIcon from "../assets/profile/question-lg.svg";

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

  const nick = username ?? "jogador";
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
          <nav className="profile-nav" aria-label="Navegação do perfil">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="profile-nav-btn"
              aria-label="Voltar"
            >
              <img
                src={arrowLeftIcon}
                alt=""
                aria-hidden="true"
                className="profile-nav-arrow"
              />
            </button>

            <h1 className="profile-nav-title">
              <img
                src={personIcon}
                alt=""
                aria-hidden="true"
                className="profile-nav-icon icon-svg icon-cyan"
              />
              Perfil do Usuário
            </h1>

            <button
              type="button"
              onClick={() => setIsDarkMode((prev) => !prev)}
              className="profile-theme-btn"
              aria-label="Alternar tema"
            >
              {isDarkMode ? <SunIcon /> : <MoonIcon />}
            </button>
          </nav>
        </div>

        <div className="px-4 sm:px-6 py-8 sm:py-10">
          <div className="profile-shell">
            <div className="profile-header">
              <div
                className="profile-initials"
                aria-label={`Avatar de ${nick}`}
              >
                {initials || "JG"}
              </div>
              <h2 className="profile-name">{nick}</h2>
              <p className="profile-email">
                {userData?.email ?? "example@email.com"}
              </p>
            </div>

            <section>
              <h3 className="profile-section-title">ESTATÍSTICAS</h3>
              <UserStats username={nick} stats={userData} />
            </section>

            <section>
              <h3 className="profile-section-title">HISTÓRICO RECENTE</h3>
              <MatchHistory username={nick} matches={matches} />
            </section>
          </div>

          <button type="button" className="profile-help-fab" aria-label="Ajuda">
            <img
              src={questionIcon}
              alt=""
              aria-hidden="true"
              className="profile-help-icon icon-white"
            />
          </button>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
