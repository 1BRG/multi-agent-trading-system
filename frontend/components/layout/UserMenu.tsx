"use client";

import { useEffect, useRef, useState } from "react";

import { API_BASE_URL } from "../../lib/api";
import type { User } from "../../types/auth";

interface UserMenuProps {
  user: User | null;
  onLogout: () => void;
  onOpenSettings: () => void;
}

export function UserMenu({ user, onLogout, onOpenSettings }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const userLabel = user?.full_name || user?.username || "Account";

  useEffect(() => {
    function handleDocumentClick(event: MouseEvent) {
      if (!menuRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("click", handleDocumentClick);
    return () => document.removeEventListener("click", handleDocumentClick);
  }, []);

  function handleSettingsClick() {
    setIsOpen(false);
    onOpenSettings();
  }

  function handleLogoutClick() {
    setIsOpen(false);
    onLogout();
  }

  return (
    <div className="user-menu" ref={menuRef}>
      {isOpen ? (
        <div className="user-menu-popover">
          <button onClick={handleSettingsClick} type="button">
            Settings
          </button>
          <button onClick={handleLogoutClick} type="button">
            Log out
          </button>
        </div>
      ) : null}
      <button
        className="sidebar-user-button"
        onClick={() => setIsOpen((currentValue) => !currentValue)}
        type="button"
      >
        {user?.profile_photo ? (
          <img
            className="sidebar-user-avatar sidebar-user-avatar-image"
            alt="Profile"
            src={new URL(user.profile_photo, API_BASE_URL).toString()}
          />
        ) : (
          <span className="sidebar-user-avatar">
            {(userLabel || "A").slice(0, 1).toUpperCase()}
          </span>
        )}
        <span className="sidebar-user-text">
          <strong>{userLabel}</strong>
          <small>{user?.role || "user"}</small>
        </span>
      </button>
    </div>
  );
}
