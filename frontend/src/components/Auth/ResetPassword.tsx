// Import React hooks and Amplify authentication methods
import { useState } from "react";
import { resetPassword, confirmResetPassword } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";
import { passwordPolicy } from "../../aws-exports";

// Main component for the Reset Password page
export default function ResetPassword() {
  // Define state variables to store form data and messages
  const [email, setEmail] = useState(""); // User's email address
  const [code, setCode] = useState(""); // Confirmation code sent to email
  const [newPassword, setNewPassword] = useState(""); // New password input
  const [stage, setStage] = useState<"request" | "confirm">("request"); // Tracks form stage (request → confirm)
  const [error, setError] = useState(""); // Stores error messages
  const [message, setMessage] = useState(""); // Stores success/info messages

  const navigate = useNavigate(); // Used to navigate between pages

  // Handles the first form submission (requesting password reset)
  async function requestReset(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      await resetPassword({ username: email });
      setStage("confirm"); // Switch to confirmation stage
      setMessage("A confirmation code has been sent to your email.");
    } catch (err: any) {
      setError(err.message || "Failed to send reset code.");
    }
  }

  // Handles the second form submission (confirming new password)
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
      navigate("/login"); // Navigate back to the login page
    } catch (err: any) {
      setError(err.message || "Failed to reset password.");
    }
  }

  // JSX (UI) section
  return (
    // Outer container that gives the light blue full-screen background and centers everything
    <div
      style={{
        backgroundColor: "#add8e6", // Light blue background
        minHeight: "100vh", // Fill the full height of the page
        display: "flex", // Enable flexbox layout
        justifyContent: "center", // Center horizontally
        alignItems: "center", // Center vertically
      }}
    >
      {/* White box that holds the form content */}
      <div
        style={{
          backgroundColor: "white",
          padding: "2rem",
          borderRadius: "10px",
          boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)", // Soft drop shadow
          width: "320px", // Fixed width for consistent sizing
          display: "flex",
          flexDirection: "column", // Stack children vertically
          alignItems: "stretch",
        }}
      >
        {/* Conditionally render one of two forms based on the stage */}
        {stage === "request" ? (
          // === Stage 1: User enters email to request a reset code ===
          <form
            onSubmit={requestReset}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px", // Adds spacing between elements
            }}
          >
            <h2 style={{ textAlign: "center" }}>Reset Password</h2>

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

            {/* Display password policy for consistency with signup page */}
            <p style={{ color: "gray", fontSize: "14px" }}>
              Password must be at least {passwordPolicy.minLength} characters
              {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
              {passwordPolicy.requireNumbers ? ", include numbers" : ""}
              {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
            </p>

            {/* Submit button to send reset code */}
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
              Send Code
            </button>
          </form>
        ) : (
          // === Stage 2: User enters the code and new password ===
          <form
            onSubmit={confirmReset}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <h2 style={{ textAlign: "center" }}>Enter Code</h2>

            <label>Confirmation Code</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              style={{
                padding: "8px",
                borderRadius: "5px",
                border: "1px solid #ccc",
              }}
            />

            <label>New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              style={{
                padding: "8px",
                borderRadius: "5px",
                border: "1px solid #ccc",
              }}
            />

            {/* Show password policy for clarity */}
            <p style={{ color: "gray", fontSize: "14px" }}>
              Password must be at least {passwordPolicy.minLength} characters
              {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
              {passwordPolicy.requireNumbers ? ", include numbers" : ""}
              {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
            </p>

            {/* Submit button to confirm reset */}
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
              Reset Password
            </button>
          </form>
        )}

        {/* Display error or success messages */}
        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}
        {message && <p style={{ color: "green", textAlign: "center" }}>{message}</p>}

        {/* Navigation button back to Login page */}
        <button
          onClick={() => navigate("/login")}
          style={{
            marginTop: "15px",
            padding: "8px",
            backgroundColor: "transparent",
            border: "1px solid #1e90ff",
            borderRadius: "5px",
            color: "#1e90ff",
            cursor: "pointer",
          }}
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}
