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
        backgroundColor: "#add8e6", // light blue background
        minHeight: "100vh",         // fill the full screen height
        display: "flex",            // use flexbox layout
        justifyContent: "center",   // center horizontally
        alignItems: "center",       // center vertically
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
        {stage === "signup" ? (
          <form
            onSubmit={handleSignup}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <h2 style={{ textAlign: "center" }}>Sign Up</h2>

            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <p style={{ color: "gray", fontSize: "14px" }}>
              Password must be at least {passwordPolicy.minLength} characters
              {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
              {passwordPolicy.requireNumbers ? ", include numbers" : ""}
              {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
            </p>

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
              Create Account
            </button>
          </form>
        ) : (
          <form
            onSubmit={handleConfirm}
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "10px",
            }}
          >
            <h2 style={{ textAlign: "center" }}>Confirm Code</h2>

            <label>Confirmation Code</label>
            <input
              type="text"
              value={confirmationCode}
              onChange={(e) => setConfirmationCode(e.target.value)}
              required
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
              Confirm
            </button>
          </form>
        )}

        {error && <p style={{ color: "red", textAlign: "center" }}>{error}</p>}

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
