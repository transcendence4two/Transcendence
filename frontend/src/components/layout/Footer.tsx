import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="footer-main">
      <div className="footer-content">
        <p className="footer-copy text-sm">
          © 2026 Transcendence 42 Rio C2G1. All rights reserved.
        </p>
        <nav className="footer-links" aria-label="Footer links">
          <Link
            to="/privacy-policy"
            className="text-sm link-base in-[.light]:hover:text-gray-500"
          >
            Privacy Policy
          </Link>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
