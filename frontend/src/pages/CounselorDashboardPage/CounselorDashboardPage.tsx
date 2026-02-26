import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import MainLayout from "../../components/layout/MainLayout";
import { listMyConversations } from "../../services/counselorChatService";
import { CounselorConversation } from "../../types/counselorChat";
import "./CounselorDashboardPage.css";

const formatTime = (iso: string): string => {
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / 86400000);
  if (diffDays === 0) {
    return date.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" });
  }
  if (diffDays === 1) return "Hôm qua";
  if (diffDays < 7) return `${diffDays} ngày trước`;
  return date.toLocaleDateString("vi-VN", { day: "2-digit", month: "2-digit" });
};

const statusLabel: Record<string, string> = {
  active: "Đang hoạt động",
  closed: "Đã đóng",
  archived: "Lưu trữ",
};

const CounselorDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<CounselorConversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listMyConversations();
      setConversations(data);
    } catch (err: any) {
      console.error("Failed to load conversations", err);
      setError("Không thể tải danh sách trò chuyện");
    } finally {
      setLoading(false);
    }
  };

  const totalUnread = conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0);

  return (
    <MainLayout>
      <div className="counselor-dashboard">
        {/* Header card */}
        <div className="counselor-dashboard__header">
          <div className="counselor-dashboard__avatar">
            {user?.full_name?.charAt(0)?.toUpperCase() || "C"}
          </div>
          <div className="counselor-dashboard__header-info">
            <h2 className="counselor-dashboard__name">{user?.full_name || "Tư vấn viên"}</h2>
            <p className="counselor-dashboard__role">Tư vấn viên tâm lý</p>
          </div>
          {totalUnread > 0 && (
            <div className="counselor-dashboard__badge">{totalUnread}</div>
          )}
        </div>

        {/* Section title */}
        <div className="counselor-dashboard__section-header">
          <h3 className="counselor-dashboard__section-title">
            Cuộc hội thoại
            {conversations.length > 0 && (
              <span className="counselor-dashboard__count"> ({conversations.length})</span>
            )}
          </h3>
          <button className="counselor-dashboard__refresh-btn" onClick={loadConversations}>
            ↻
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div className="counselor-dashboard__loading">
            <div className="counselor-dashboard__spinner" />
            <p>Đang tải...</p>
          </div>
        ) : error ? (
          <div className="counselor-dashboard__error">
            <p>{error}</p>
            <button onClick={loadConversations} className="counselor-dashboard__retry-btn">Thử lại</button>
          </div>
        ) : conversations.length === 0 ? (
          <div className="counselor-dashboard__empty">
            <span className="counselor-dashboard__empty-icon">💬</span>
            <p>Chưa có cuộc hội thoại nào</p>
            <p className="counselor-dashboard__empty-sub">Học sinh sẽ xuất hiện ở đây khi họ liên hệ bạn</p>
          </div>
        ) : (
          <div className="counselor-convlist">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                className="counselor-conv-item"
                onClick={() => navigate(`/counselor-chat/${conv.id}`)}
              >
                <div className="counselor-conv-item__avatar">
                  {(conv.student_name || "S").charAt(0).toUpperCase()}
                </div>
                <div className="counselor-conv-item__info">
                  <p className="counselor-conv-item__name">
                    {conv.student_name || `Học sinh #${conv.student_id}`}
                  </p>
                  <p className="counselor-conv-item__status">
                    {statusLabel[conv.status] || conv.status}
                  </p>
                </div>
                <div className="counselor-conv-item__right">
                  <span className="counselor-conv-item__time">
                    {formatTime(conv.last_message_at)}
                  </span>
                  {(conv.unread_count || 0) > 0 && (
                    <span className="counselor-conv-item__unread">{conv.unread_count}</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default CounselorDashboardPage;
