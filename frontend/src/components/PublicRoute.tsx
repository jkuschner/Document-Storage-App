import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

/**
 * PublicRoute - For login/signup pages
 * Redirects to /files if user is already authenticated
 */
export default function PublicRoute({ children }: { children: React.ReactNode }) {
  const { authenticated, loading } = useAuth();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "#add8e6"
      }}>
        <div style={{
          border: "4px solid #f3f3f3",
          borderTop: "4px solid #1e90ff",
          borderRadius: "50%",
          width: "60px",
          height: "60px",
          animation: "spin 1s linear infinite"
        }} />
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Redirect to files if already authenticated
  if (authenticated) {
    return <Navigate to="/files" replace />;
  }

  // Render public content (login/signup)
  return <>{children}</>;
}
