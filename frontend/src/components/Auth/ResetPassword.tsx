import { useState } from "react";
import { resetPassword, confirmResetPassword } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";
import { passwordPolicy } from "../../aws-exports";

export default function ResetPassword() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [stage, setStage] = useState<"request" | "confirm">("request");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const navigate = useNavigate();

  async function requestReset(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      await resetPassword({ username: email });
      setStage("confirm");
      setMessage("A confirmation code has been sent to your email.");
    } catch (err: any) {
      setError(err.message || "Failed to send reset code.");
    }
  }

  async function confirmReset(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      await confirmResetPassword({
        username: email,
        confirmationCode: code,
        newPassword,
      });
      setMessage("Password successfully reset. You can now log in.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err: any) {
      setError(err.message || "Failed to reset password.");
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
            {stage === "request" ? "Reset password" : "Enter code"}
          </h2>
        </div>

        {stage === "request" ? (
          <form onSubmit={requestReset}>
            <p style={{
              fontSize: "14px",
              color: "#6b7280",
              marginBottom: "24px",
              lineHeight: "1.5",
            }}>
              Enter your email address and we'll send you a code to reset your password.
            </p>

            <div style={{ marginBottom: "24px" }}>
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
              Send code
            </button>
          </form>
        ) : (
          <form onSubmit={confirmReset}>
            <p style={{
              fontSize: "14px",
              color: "#6b7280",
              marginBottom: "24px",
              lineHeight: "1.5",
            }}>
              We sent a code to <strong>{email}</strong>. Enter it below along with your new password.
            </p>

            <div style={{ marginBottom: "16px" }}>
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
                value={code}
                onChange={(e) => setCode(e.target.value)}
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
                New password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
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
              Reset password
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

        {message && (
          <div style={{
            marginTop: "16px",
            padding: "12px",
            backgroundColor: "#dcfce7",
            border: "1px solid #bbf7d0",
            borderRadius: "6px",
            color: "#15803d",
            fontSize: "14px",
          }}>
            {message}
          </div>
        )}

        <div style={{
          marginTop: "24px",
          paddingTop: "24px",
          borderTop: "1px solid #e5e7eb",
          textAlign: "center",
        }}>
          <span style={{ fontSize: "14px", color: "#6b7280" }}>
            Remember your password?{" "}
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