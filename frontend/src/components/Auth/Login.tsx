import { useState, useEffect } from "react";
import { signIn, signOut, getCurrentUser } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function ensureLoggedOut() {
      try {
        await getCurrentUser();
        await signOut();        
      } catch {
      }
    }
    ensureLoggedOut();
  }, []);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await signIn({ username: email, password });
      navigate("/files");
    } catch (err: any) {
      setError(err.message || "Login failed");
    }
  }

  return (
    <div
      style={{
        backgroundColor: "#f7f9fa",
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          padding: "48px 40px",
          borderRadius: "8px",
          boxShadow: "0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)",
          width: "400px",
          maxWidth: "90vw",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <h2 style={{ 
            margin: 0,
            fontSize: "24px",
            fontWeight: "500",
            color: "#1e293b",
          }}>
            Sign in
          </h2>
        </div>

        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: "16px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontSize: "14px",
              fontWeight: "500",
              color: "#374151",
            }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
                fontSize: "15px",
                boxSizing: "border-box",
                outline: "none",
                transition: "border-color 0.15s",
              }}
              onFocus={(e) => e.target.style.borderColor = "#16a34a"}
              onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
            />
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontSize: "14px",
              fontWeight: "500",
              color: "#374151",
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
                fontSize: "15px",
                boxSizing: "border-box",
                outline: "none",
                transition: "border-color 0.15s",
              }}
              onFocus={(e) => e.target.style.borderColor = "#16a34a"}
              onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
            />
          </div>

          <button
            type="submit"
            style={{
              width: "100%",
              padding: "14px",
              backgroundColor: "#16a34a",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontSize: "15px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "background-color 0.2s",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#15803d"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#16a34a"}
          >
            Sign in
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#fee",
            border: "1px solid #fcc",
            borderRadius: "6px",
            color: "#b91c1c",
            fontSize: "14px",
          }}>
            {error}
          </div>
        )}

        <div style={{
          marginTop: "24px",
          paddingTop: "24px",
          borderTop: "1px solid #e5e7eb",
          textAlign: "center",
        }}>
          <button
            onClick={() => navigate("/signup")}
            style={{
              background: "none",
              border: "none",
              color: "#16a34a",
              fontSize: "14px",
              fontWeight: "500",
              cursor: "pointer",
              marginBottom: "12px",
            }}
          >
            Create an account
          </button>
          <div style={{ fontSize: "14px", color: "#6b7280" }}>or</div>
          <button
            onClick={() => navigate("/resetpassword")}
            style={{
              background: "none",
              border: "none",
              color: "#16a34a",
              fontSize: "14px",
              fontWeight: "500",
              cursor: "pointer",
              marginTop: "12px",
            }}
          >
            Forgot password?
          </button>
        </div>
      </div>
    </div>
  );
}