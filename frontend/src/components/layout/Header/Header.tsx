import React from "react";
import { useAuth } from "../../../contexts/AuthContext";
import "./Header.css";

interface HeaderProps {
  showMenu?: boolean;
  onMenuClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ showMenu = false, onMenuClick }) => {
  const { user } = useAuth();

  return (
    <header className="mobile-header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-logo">ai4mind</h1>
        </div>

        <div className="header-right">
          <button className="user-profile-button" aria-label="User Profile">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
