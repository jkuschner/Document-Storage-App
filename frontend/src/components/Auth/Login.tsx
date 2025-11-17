import { useState, useEffect } from "react";
import { signIn, getCurrentUser } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Check if user is already logged in
  useEffect(() => {
    async function checkAuth() {
      try {
        await getCurrentUser();
        // Already logged in, redirect to files
        navigate("/files");
      } catch {
        // Not logged in, stay on login page
      }
    }
    checkAuth();
  }, [navigate]);

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
        backgroundColor: "#add8e6", 
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          padding: "2rem",
          borderRadius: "10px",
          boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
          width: "320px",
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
        }}
      >
        <form
          onSubmit={handleLogin}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          }}
        >
          <h2 style={{ textAlign: "center" }}>Login</h2>

          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />

          <button
            type="submit"
            style={{
              marginTop: "10px",
              padding: "8px",
              backgroundColor: "#1e90ff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
            }}
          >
            Login
          </button>
        </form>

        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

        {/* Navigation buttons */}
        <div
          style={{
            marginTop: "15px",
            display: "flex",
            flexDirection: "column",
            gap: "8px",
          }}
        >
          <button
            onClick={() => navigate("/signup")}
            style={{
              padding: "8px",
              backgroundColor: "transparent",
              border: "1px solid #1e90ff",
              borderRadius: "5px",
              color: "#1e90ff",
              cursor: "pointer",
            }}
          >
            Create an Account
          </button>

          <button
            onClick={() => navigate("/resetpassword")}
            style={{
              padding: "8px",
              backgroundColor: "transparent",
              border: "1px solid #1e90ff",
              borderRadius: "5px",
              color: "#1e90ff",
              cursor: "pointer",
            }}
          >
            Forgot Password?
          </button>
        </div>
      </div>
    </div>
  );
}
