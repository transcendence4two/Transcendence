import { useEffect, useState, type ComponentType } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeftShortIcon,
  MoonIcon,
  SunIcon,
  type IconProps,
} from "../icons/Icons";
import HamburgerMenu from "./HamburgerMenu";

interface PageNavbarProps {
  title?: string;
  icon?: ComponentType<IconProps>;
  backTo?: string;
}

const PageNavbar = ({
  title,
  icon: Icon,
  backTo = "/home",
}: PageNavbarProps) => {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isHome = pathname === "/home";
  const isRoot = pathname === "/";
  const hasHeading = Boolean(title || Icon);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem("theme") !== "light";
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
      <nav className="profile-nav" aria-label="Page navigation">
        {isHome ? (
          <div className="profile-nav-menu-wrap">
            <HamburgerMenu />
          </div>
        ) : isRoot ? (
          <span className="inline-flex h-10 w-10" aria-hidden="true" />
        ) : (
          <button
            type="button"
            onClick={() => navigate(backTo)}
            className="profile-nav-btn"
            aria-label="Back"
          >
            <ArrowLeftShortIcon className="profile-nav-arrow" />
          </button>
        )}

        {hasHeading ? (
          <h1 className="profile-nav-title text-[1.12rem] items-center leading-none">
            {Icon ? (
              <Icon className="profile-nav-icon icon-svg icon-cyan" />
            ) : null}
            {title ?? ""}
          </h1>
        ) : (
          <span className="inline-flex" aria-hidden="true" />
        )}

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
