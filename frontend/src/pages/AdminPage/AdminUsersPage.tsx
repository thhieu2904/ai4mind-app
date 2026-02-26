import React, { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import MainLayout from "../../components/layout/MainLayout";
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

// ---- Sub-components ----

interface UserCardProps {
  user: AdminUser;
  onAction: (user: AdminUser) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onAction }) => (
  <div className={`user-card ${!user.is_active ? "user-card--inactive" : ""}`} onClick={() => onAction(user)}>
    <div className="user-card__avatar">
      {user.full_name.charAt(0).toUpperCase()}
    </div>
    <div className="user-card__info">
      <p className="user-card__name">{user.full_name}</p>
      <p className="user-card__email">{user.email}</p>
    </div>
    <div className="user-card__meta">
      <span className={`badge ${ROLE_COLORS[user.role] || ""}`}>
        {ROLE_LABELS[user.role] || user.role}
      </span>
      {!user.is_active && <span className="badge badge--inactive">Tắt</span>}
    </div>
  </div>
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

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const data = await AdminService.listUsers(roleFilter || undefined, search || undefined);
      setUsers(data);
    } catch {
      console.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  }, [roleFilter, search]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const openActionSheet = (user: AdminUser) => {
    setSelectedUser(user);
    setFormError("");
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
      loadUsers();
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
      loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Thao tác thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;
    if (!window.confirm(`Xoá tài khoản "${selectedUser.full_name}"?`)) return;
    setFormLoading(true);
    try {
      await AdminService.deleteUser(selectedUser.id);
      closeSheet();
      loadUsers();
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
      loadUsers();
    } catch (err: any) {
      setFormError(err?.response?.data?.detail || "Tạo tài khoản thất bại");
    } finally {
      setFormLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="admin-users">
        {/* Header */}
        <div className="admin-users__header">
          <h2 className="admin-users__title">Người dùng</h2>
          <button className="admin-users__add-btn" onClick={openCreate}>+ Thêm</button>
        </div>

        {/* Search */}
        <form className="admin-users__search" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            className="admin-users__search-input"
            placeholder="Tìm tên hoặc email..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button type="submit" className="admin-users__search-btn">Tìm</button>
        </form>

        {/* Role filter tabs */}
        <div className="admin-users__tabs">
          {(["", "STUDENT", "COUNSELOR", "ADMIN"] as RoleFilter[]).map((r) => (
            <button
              key={r}
              className={`admin-users__tab ${roleFilter === r ? "active" : ""}`}
              onClick={() => setRoleFilter(r)}
            >
              {r === "" ? "Tất cả" : ROLE_LABELS[r]}
            </button>
          ))}
        </div>

        {/* User list */}
        {loading ? (
          <div className="admin-users__loading">Đang tải...</div>
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
                <button className="sheet-btn sheet-btn--danger" onClick={handleDelete} disabled={formLoading}>
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
    </MainLayout>
  );
};

export default AdminUsersPage;
