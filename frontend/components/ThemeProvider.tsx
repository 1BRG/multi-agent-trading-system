"use client";

import { useEffect } from "react";

import { initializeTheme } from "../lib/theme";

export function ThemeProvider() {
  useEffect(() => {
    initializeTheme();
  }, []);

  return null;
}
