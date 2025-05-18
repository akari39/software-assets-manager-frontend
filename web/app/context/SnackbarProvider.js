import { createContext, useContext, useState, useEffect } from "react";
import { setGlobalSnackbarHandler } from "../components/GlobalSnackbar";

const SnackbarContext = createContext();

export function SnackbarProvider({ children }) {
  const [snackbarTip, setSnackbarTip] = useState(null);
  
  // Optionally, clear error after a timeout or on demand
  const clearSnackbar = () => setSnackbarTip(null);

  // When the provider mounts, register setError as the global error handler.
  useEffect(() => {
    setGlobalSnackbarHandler(setSnackbarTip);
  }, []);

  return (
    <SnackbarContext.Provider value={{ snackbarTip, setSnackbarTip, clearSnackbar }}>
      {children}
    </SnackbarContext.Provider>
  );
}

export function useSnackbar() {
  return useContext(SnackbarContext);
}
