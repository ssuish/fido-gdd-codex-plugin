import { useCallback, useEffect, useState } from "react";
import { applyTheme, readStoredTheme, writeStoredTheme, type Theme } from "../theme";

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() =>
    typeof window === "undefined" ? "dark" : readStoredTheme(),
  );

  useEffect(() => {
    applyTheme(theme);
    writeStoredTheme(theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === "dark" ? "light" : "dark"));
  }, []);

  return { theme, toggleTheme };
}
