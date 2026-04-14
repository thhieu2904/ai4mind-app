import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./NotImplementedPage.css";

type PageContent = {
  title: string;
  description: string;
  actionLabel: string;
  actionPath: string;
};

const CONTENT_BY_PATH: Record<string, PageContent> = {
  "/forgot-password": {
    title: "Quen mat khau chua san sang",
    description:
      "Tinh nang quen mat khau chua duoc xay dung. Tam thoi, ban vui long lien he quan tri vien de reset mat khau.",
    actionLabel: "Quay lai dang nhap",
    actionPath: "/login",
  },
  "/terms": {
    title: "Dieu khoan dang cap nhat",
    description:
      "Noi dung dieu khoan su dung chua hoan thien. Ban co the quay lai de tiep tuc dang ky, he thong se cap nhat sau.",
    actionLabel: "Quay lai dang ky",
    actionPath: "/register",
  },
  "/privacy": {
    title: "Chinh sach bao mat dang cap nhat",
    description:
      "Noi dung chinh sach bao mat chua hoan thien. Ban co the quay lai de tiep tuc dang ky, he thong se cap nhat sau.",
    actionLabel: "Quay lai dang ky",
    actionPath: "/register",
  },
};

const DEFAULT_CONTENT: PageContent = {
  title: "Tinh nang chua hoan thien",
  description: "Tinh nang nay chua duoc trien khai o phien ban hien tai.",
  actionLabel: "Ve trang dang nhap",
  actionPath: "/login",
};

const NotImplementedPage: React.FC = () => {
  const location = useLocation();
  const content = CONTENT_BY_PATH[location.pathname] || DEFAULT_CONTENT;

  return (
    <div className="not-implemented-container">
      <div className="not-implemented-card">
        <h1>{content.title}</h1>
        <p>{content.description}</p>
        <Link to={content.actionPath} className="not-implemented-action">
          {content.actionLabel}
        </Link>
      </div>
    </div>
  );
};

export default NotImplementedPage;
