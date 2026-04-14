import React, { useEffect, useState, useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
import AlertModal from "../../components/AlertModal";
import AdminService, { AdminUser, CreateUserRequest } from "../../services/adminService";
import "./AdminUsersPage.css";

type RoleFilter = "" | "STUDENT" | "COUNSELOR" | "ADMIN";

const ROLE_LABELS: Record<string, string> = {
  STUDENT: "Học sinh",
  COUNSELOR: "Tư vấn viên",
  ADMIN: "Quản trị viên",
  PARENT: "Phụ huynh",
};

const ROLE_COLORS: Record<string, string> = {
  STUDENT: "badge--student",
  COUNSELOR: "badge--counselor",
  ADMIN: "badge--admin",
  PARENT: "badge--parent",
};

const ROLE_TABS: RoleFilter[] = ["", "STUDENT", "COUNSELOR", "ADMIN"];

const formatDate = (value?: string) => {
  if (!value) return "--/--/----";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--/--/----";
  return date.toLocaleDateString("vi-VN");
};

const getInitial = (name: string) => {
  const trimmed = name?.trim();
  return trimmed ? trimmed.charAt(0).toUpperCase() : "?";
};

// ---- Sub-components ----

interface UserCardProps {
  user: AdminUser;
  onAction: (user: AdminUser) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onAction }) => (
  <button
    type="button"
    className={`user-card ${!user.is_active ? "user-card--inactive" : ""}`}
    onClick={() => onAction(user)}
  >
    <div className="user-card__avatar">
      {getInitial(user.full_name)}
    </div>
    <div className="user-card__info">
      <p className="user-card__name">{user.full_name}</p>
      <p className="user-card__email">{user.email}</p>
      <p className="user-card__secondary">{user.phone?.trim() || "Chưa có số điện thoại"}</p>
    </div>
    <div className="user-card__meta">
      <span className={`badge ${ROLE_COLORS[user.role] || ""}`}>
        {ROLE_LABELS[user.role] || user.role}
      </span>
      <span className={`badge ${user.is_active ? "badge--active" : "badge--inactive"}`}>
        {user.is_active ? "Hoạt động" : "Tạm khóa"}
      </span>
      <span className="user-card__created">Tạo: {formatDate(user.created_at)}</span>
    </div>
  </button>
);

// ---- Main page ----

const AdminUsersPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const defaultRole = (searchParams.get("role") || "") as RoleFilter;

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState<RoleFilter>(defaultRole);
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");

  // Sheet state
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [sheetMode, setSheetMode] = useState<"action" | "edit" | "reset-pw" | "create" | null>(null);

  // Form state
  const [editName, setEditName] = useState("");
  const [editPhone, setEditPhone] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [createForm, setCreateForm] = useState<CreateUserRequest>({
    email: "", full_name: "", phone: "", role: "COUNSELOR", password: ""
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setLoadError("");
      const data = await AdminService.listUsers(roleFilter || undefined, search || undefined);
      setUsers(data);
    } catch {
      console.error("Failed to load users");
      setUsers([]);
      setLoadError("Không tải được danh sách người dùng. Bạn có thể thử lại.");
    } finally {
      setLoading(false);
    }
  }, [roleFilter, search]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const overview = useMemo(() => {
    const total = users.length;
    const active = users.filter((u) => u.is_active).length;
    const inactive = total - active;
    return { total, active, inactive };
  }, [users]);

  const filterLabel = roleFilter ? ROLE_LABELS[roleFilter] : "Tất cả vai trò";

  const handleClearSearch = () => {
    setSearchInput("");
    setSearch("");
  };

  const openActionSheet = (user: AdminUser) => {
    setSelectedUser(user);
    setFormError("");
    setDeleteConfirmOpen(false);
    setSheetMode("action");
  };

  const openEdit = () => {
    if (!selectedUser) return;
    setEditName(selectedUser.full_name);
    setEditPhone(selectedUser.phone || "");
    setFormError("");
    setSheetMode("edit");
  };

  const openResetPw = () => {
    setNewPassword("");
    setFormError("");
    setSheetMode("reset-pw");
  };

  const openCreate = () => {
    setCreateForm({ email: "", full_name: "", phone: "", role: "COUNSELOR", password: "" });
    setFormError("");
    setSheetMode("create");
    setSelectedUser(null);
  };

  const closeSheet = () => {
    setSheetMode(null);
    setSelectedUser(null);
    setFormError("");
    setDeleteConfirmOpen(false);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearch(searchInput);
  };

  // Actions
  const handleSaveEdit = async () => {
    if (!selectedUser) return;
    setFormLoading(true);
    setFormError("");
    try {
      await AdminService.updateUser(selectedUser.id, {
        full_name: editName,
        phone: editPhone || undefined,
      });
      closeSheet();
      void loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Cập nhật thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  const handleResetPw = async () => {
    if (!selectedUser || !newPassword) return;
    setFormLoading(true);
    setFormError("");
    try {
      await AdminService.resetPassword(selectedUser.id, newPassword);
      closeSheet();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Đặt lại mật khẩu thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  const handleToggleActive = async () => {
    if (!selectedUser) return;
    setFormLoading(true);
    try {
      await AdminService.toggleActive(selectedUser.id);
      closeSheet();
      void loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Thao tác thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  const requestDelete = () => {
    if (!selectedUser) return;
    setDeleteConfirmOpen(true);
  };

  const handleDelete = async () => {
    if (!selectedUser) return;

    setDeleteConfirmOpen(false);
    setFormLoading(true);
    setFormError("");

    try {
      await AdminService.deleteUser(selectedUser.id);
      closeSheet();
      void loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Xoá tài khoản thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  const handleCreate = async () => {
    setFormLoading(true);
    setFormError("");
    try {
      await AdminService.createUser(createForm);
      closeSheet();
      void loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Tạo tài khoản thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="admin-users">
        <div className="admin-users__hero">
          <div>
            <h2 className="admin-users__title">Quản lý người dùng</h2>
            <p className="admin-users__subtitle">Theo dõi danh sách tài khoản và thao tác nhanh trong một màn hình.</p>
          </div>
          <button className="admin-users__add-btn" onClick={openCreate}>+ Tạo tài khoản</button>
        </div>

        <div className="admin-users__panel">
          <form className="admin-users__search" onSubmit={handleSearchSubmit}>
            <div className="admin-users__search-wrap">
              <span className="admin-users__search-icon">⌕</span>
              <input
                type="text"
                className="admin-users__search-input"
                placeholder="Tìm theo tên hoặc email..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
            </div>
            {(search || searchInput) && (
              <button type="button" className="admin-users__clear-btn" onClick={handleClearSearch}>
                Xoá
              </button>
            )}
            <button type="submit" className="admin-users__search-btn">Tìm</button>
          </form>

          <div className="admin-users__tabs">
            {ROLE_TABS.map((r) => (
              <button
                key={r}
                className={`admin-users__tab ${roleFilter === r ? "active" : ""}`}
                onClick={() => setRoleFilter(r)}
              >
                {r === "" ? "Tất cả" : ROLE_LABELS[r]}
              </button>
            ))}
          </div>

          <div className="admin-users__meta">
            <span className="admin-users__meta-pill">Bộ lọc: {filterLabel}</span>
            {search && <span className="admin-users__meta-pill">Từ khoá: {search}</span>}
          </div>
        </div>

        <div className="admin-users__insights">
          <div className="admin-users__insight-card">
            <span className="admin-users__insight-label">Đang hiển thị</span>
            <strong className="admin-users__insight-value">{overview.total}</strong>
          </div>
          <div className="admin-users__insight-card">
            <span className="admin-users__insight-label">Hoạt động</span>
            <strong className="admin-users__insight-value">{overview.active}</strong>
          </div>
          <div className="admin-users__insight-card">
            <span className="admin-users__insight-label">Tạm khóa</span>
            <strong className="admin-users__insight-value">{overview.inactive}</strong>
          </div>
        </div>

        {loadError && <div className="admin-users__error">{loadError}</div>}

        <div className="admin-users__list-head">
          <h3 className="admin-users__list-title">Danh sách tài khoản</h3>
          <button className="admin-users__refresh-btn" onClick={loadUsers} disabled={loading}>
            {loading ? "Đang tải..." : "Làm mới"}
          </button>
        </div>

        {loading ? (
          <div className="admin-users__skeleton-list">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="user-card-skeleton" />
            ))}
          </div>
        ) : users.length === 0 ? (
          <div className="admin-users__empty">Không tìm thấy người dùng</div>
        ) : (
          <div className="admin-users__list">
            {users.map((u) => (
              <UserCard key={u.id} user={u} onAction={openActionSheet} />
            ))}
          </div>
        )}
      </div>

      {/* Bottom Sheet Overlay */}
      {sheetMode && (
        <div className="sheet-overlay" onClick={closeSheet}>
          <div className="sheet" onClick={(e) => e.stopPropagation()}>
            <div className="sheet__handle" />

            {/* ACTION menu */}
            {sheetMode === "action" && selectedUser && (
              <>
                <div className="sheet__user-info">
                  <p className="sheet__user-name">{selectedUser.full_name}</p>
                  <p className="sheet__user-email">{selectedUser.email}</p>
                </div>
                {formError && <p className="sheet__error">{formError}</p>}
                <button className="sheet-btn" onClick={openEdit}>✏️ Chỉnh sửa thông tin</button>
                <button className="sheet-btn" onClick={openResetPw}>🔑 Đặt lại mật khẩu</button>
                <button className={`sheet-btn ${selectedUser.is_active ? "sheet-btn--warn" : "sheet-btn--success"}`} onClick={handleToggleActive} disabled={formLoading}>
                  {selectedUser.is_active ? "🚫 Vô hiệu hoá" : "✅ Kích hoạt"}
                </button>
                <button className="sheet-btn sheet-btn--danger" onClick={requestDelete} disabled={formLoading}>
                  🗑️ Xoá tài khoản
                </button>
                <button className="sheet-btn sheet-btn--cancel" onClick={closeSheet}>Huỷ</button>
              </>
            )}

            {/* EDIT form */}
            {sheetMode === "edit" && selectedUser && (
              <>
                <h3 className="sheet__title">Chỉnh sửa thông tin</h3>
                {formError && <p className="sheet__error">{formError}</p>}
                <label className="sheet__label">Họ tên</label>
                <input className="sheet__input" value={editName} onChange={(e) => setEditName(e.target.value)} />
                <label className="sheet__label">Số điện thoại</label>
                <input className="sheet__input" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} placeholder="(tuỳ chọn)" />
                <button className="sheet-btn sheet-btn--primary" onClick={handleSaveEdit} disabled={formLoading || !editName}>
                  {formLoading ? "Đang lưu..." : "Lưu"}
                </button>
                <button className="sheet-btn sheet-btn--cancel" onClick={() => setSheetMode("action")}>Quay lại</button>
              </>
            )}

            {/* RESET PASSWORD form */}
            {sheetMode === "reset-pw" && selectedUser && (
              <>
                <h3 className="sheet__title">Đặt lại mật khẩu</h3>
                <p className="sheet__subtitle">{selectedUser.full_name}</p>
                {formError && <p className="sheet__error">{formError}</p>}
                <label className="sheet__label">Mật khẩu mới</label>
                <input className="sheet__input" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Tối thiểu 6 ký tự" />
                <button className="sheet-btn sheet-btn--primary" onClick={handleResetPw} disabled={formLoading || newPassword.length < 6}>
                  {formLoading ? "Đang xử lý..." : "Đặt lại mật khẩu"}
                </button>
                <button className="sheet-btn sheet-btn--cancel" onClick={() => setSheetMode("action")}>Quay lại</button>
              </>
            )}

            {/* CREATE form */}
            {sheetMode === "create" && (
              <>
                <h3 className="sheet__title">Tạo tài khoản mới</h3>
                {formError && <p className="sheet__error">{formError}</p>}
                <label className="sheet__label">Họ tên *</label>
                <input className="sheet__input" value={createForm.full_name} onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })} />
                <label className="sheet__label">Email *</label>
                <input className="sheet__input" type="email" value={createForm.email} onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })} />
                <label className="sheet__label">Số điện thoại</label>
                <input className="sheet__input" value={createForm.phone} onChange={(e) => setCreateForm({ ...createForm, phone: e.target.value })} placeholder="(tuỳ chọn)" />
                <label className="sheet__label">Vai trò *</label>
                <select className="sheet__input sheet__select" value={createForm.role} onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}>
                  <option value="COUNSELOR">Tư vấn viên</option>
                  <option value="STUDENT">Học sinh</option>
                  <option value="ADMIN">Quản trị viên</option>
                </select>
                <label className="sheet__label">Mật khẩu *</label>
                <input className="sheet__input" type="password" value={createForm.password} onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })} placeholder="Tối thiểu 6 ký tự" />
                <button className="sheet-btn sheet-btn--primary" onClick={handleCreate} disabled={formLoading || !createForm.email || !createForm.full_name || createForm.password.length < 6}>
                  {formLoading ? "Đang tạo..." : "Tạo tài khoản"}
                </button>
                <button className="sheet-btn sheet-btn--cancel" onClick={closeSheet}>Huỷ</button>
              </>
            )}
          </div>
        </div>
      )}

      <AlertModal
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        type="warning"
        title="Xác nhận xoá tài khoản"
        message={
          selectedUser
            ? `Bạn có chắc muốn xoá tài khoản \"${selectedUser.full_name}\" không?`
            : "Bạn có chắc muốn xoá tài khoản này không?"
        }
        confirmText="Xoá tài khoản"
        cancelText="Huỷ"
        onConfirm={handleDelete}
        showCancel
      />
    </MainLayout>
  );
};

export default AdminUsersPage;
