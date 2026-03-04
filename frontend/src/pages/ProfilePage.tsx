import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { PersonFillIcon, QuestionLgIcon } from "../components/icons/Icons";

import PageNavbar from "../components/common/PageNavbar";
import UserStats from "../components/profile/UserStats";
import MatchHistory from "../components/profile/MatchHistory";
import type { MatchHistoryItem } from "../components/profile/MatchHistory";
import type { UserStatsData } from "../components/profile/UserStats";

type UserProfile = UserStatsData & {
  email?: string;
};

const ProfilePage = () => {
  const { username } = useParams<{ username: string }>();

  const nick = username ?? "player";
  const initials = nick
    .split(/[\s._-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  const [userData, setUserData] = useState<UserProfile | null>(null);
  const [matches, setMatches] = useState<MatchHistoryItem[]>([]);

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
        <PageNavbar title="User Profile" icon={PersonFillIcon} />

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
