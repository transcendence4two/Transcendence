import { useEffect, useState, type ComponentType } from "react";
import { useNavigate } from "react-router-dom";
import {
  ArrowLeftShortIcon,
  MoonIcon,
  SunIcon,
  type IconProps,
} from "../icons/Icons";

interface PageNavbarProps {
  title: string;
  icon: ComponentType<IconProps>;
}

const PageNavbar = ({ title, icon: Icon }: PageNavbarProps) => {
  const navigate = useNavigate();
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

  return (
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
          <Icon className="profile-nav-icon icon-svg icon-cyan" />
          {title}
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
  );
};

export default PageNavbar;
