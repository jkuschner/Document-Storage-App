import { useState } from "react";
import { signUp, confirmSignUp } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";
import { passwordPolicy } from "../../aws-exports";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmationCode, setConfirmationCode] = useState("");
  const [stage, setStage] = useState<"signup" | "confirm">("signup");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await signUp({
        username: email,
        password,
      });
      setStage("confirm");
    } catch (err: any) {
      setError(err.message || "Signup failed");
    }
  }

  async function handleConfirm(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await confirmSignUp({
        username: email,
        confirmationCode,
      });
      navigate("/login");
    } catch (err: any) {
      setError(err.message || "Confirmation failed");
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
            {stage === "signup" ? "Create account" : "Confirm your email"}
          </h2>
        </div>

        {stage === "signup" ? (
          <form onSubmit={handleSignup}>
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
                }}
                onFocus={(e) => e.target.style.borderColor = "#16a34a"}
                onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
              />
            </div>

            <div style={{ marginBottom: "8px" }}>
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
                }}
                onFocus={(e) => e.target.style.borderColor = "#16a34a"}
                onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
              />
            </div>

            <p style={{ 
              color: "#6b7280", 
              fontSize: "12px",
              marginTop: "8px",
              marginBottom: "24px",
              lineHeight: "1.5",
            }}>
              Password must be at least {passwordPolicy.minLength} characters
              {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
              {passwordPolicy.requireNumbers ? ", include numbers" : ""}
              {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
            </p>

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
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#15803d"}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#16a34a"}
            >
              Create account
            </button>
          </form>
        ) : (
          <form onSubmit={handleConfirm}>
            <p style={{
              fontSize: "14px",
              color: "#6b7280",
              marginBottom: "24px",
              lineHeight: "1.5",
            }}>
              We sent a confirmation code to <strong>{email}</strong>. Enter it below to verify your account.
            </p>

            <div style={{ marginBottom: "24px" }}>
              <label style={{
                display: "block",
                marginBottom: "8px",
                fontSize: "14px",
                fontWeight: "500",
                color: "#374151",
              }}>
                Confirmation code
              </label>
              <input
                type="text"
                value={confirmationCode}
                onChange={(e) => setConfirmationCode(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "12px 14px",
                  borderRadius: "6px",
                  border: "1px solid #d1d5db",
                  fontSize: "15px",
                  boxSizing: "border-box",
                  outline: "none",
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
              }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#15803d"}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#16a34a"}
            >
              Verify email
            </button>
          </form>
        )}

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
          <span style={{ fontSize: "14px", color: "#6b7280" }}>
            Already have an account?{" "}
          </span>
          <button
            onClick={() => navigate("/login")}
            style={{
              background: "none",
              border: "none",
              color: "#16a34a",
              fontSize: "14px",
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}