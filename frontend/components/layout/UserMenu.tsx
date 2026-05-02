"use client";

import { useEffect, useRef, useState } from "react";

import type { User } from "../../types/auth";

interface UserMenuProps {
  user: User | null;
  onLogout: () => void;
  onOpenProfile: () => void;
  onOpenSettings: () => void;
}

export function UserMenu({ user, onLogout, onOpenProfile, onOpenSettings }: UserMenuProps) {
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

  function handleProfileClick() {
    setIsOpen(false);
    onOpenProfile();
  }

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
          <button onClick={handleProfileClick} type="button">
            Profile
          </button>
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
        <span className="sidebar-user-avatar">
          {(userLabel || "A").slice(0, 1).toUpperCase()}
        </span>
        <span className="sidebar-user-text">
          <strong>{userLabel}</strong>
          <small>{user?.role || "user"}</small>
        </span>
      </button>
    </div>
  );
}
