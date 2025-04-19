import { createContext, useContext, useState, useEffect } from "react";
import { setGlobalErrorHandler } from "@/app/service/axiosConfig";

const ErrorContext = createContext();

export function ErrorProvider({ children }) {
  const [error, setError] = useState(null);
  
  // Optionally, clear error after a timeout or on demand
  const clearError = () => setError(null);

  // When the provider mounts, register setError as the global error handler.
  useEffect(() => {
    setGlobalErrorHandler(setError);
  }, []);

  return (
    <ErrorContext.Provider value={{ error, setError, clearError }}>
      {children}
    </ErrorContext.Provider>
  );
}

export function useError() {
  return useContext(ErrorContext);
}
