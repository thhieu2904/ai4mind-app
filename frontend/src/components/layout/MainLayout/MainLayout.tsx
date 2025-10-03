import React, { ReactNode } from "react";
import Header from "../Header";
import BottomNav from "../BottomNav";
import "./MainLayout.css";

interface MainLayoutProps {
  children: ReactNode;
  showHeader?: boolean;
  showBottomNav?: boolean;
}

const MainLayout: React.FC<MainLayoutProps> = ({
  children,
  showHeader = true,
  showBottomNav = true,
}) => {
  return (
    <div className="main-layout">
      {showHeader && <Header />}

      <main className="main-content">{children}</main>

      {showBottomNav && <BottomNav />}
    </div>
  );
};

export default MainLayout;
