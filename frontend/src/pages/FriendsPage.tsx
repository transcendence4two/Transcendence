import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";

import PageNavbar from "../components/common/PageNavbar";
import HelpFab from "../components/common/HelpFab";

type UserData = {
  id: string;
  username: string;
  email: string;
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

const FriendsPage = () => {
  const navigate = useNavigate();
  const [user] = useState<UserData | null>(getInitialUser);

  useEffect(() => {
    if (!user) {
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  if (!user) return null;

  return (
    <div className="container-main">
      <main className="container-main">
        <PageNavbar title="Friends" />

        <div className="friends-page-content">
          <div className="friends-page-layout">
            <div className="friends-page-card">
              <h1 className="text-white">Hello World of Unicorns</h1>
              <div className="text-white mt-5">The power of friendship 🦄 </div>
            </div>
          </div>
          <HelpFab />
        </div>
      </main>
    </div>
  );
};

export default FriendsPage;
