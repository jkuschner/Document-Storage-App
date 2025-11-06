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
    <div>
      {stage === "signup" ? (
        <form onSubmit={handleSignup}>
          <h2>Sign Up</h2>
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
          <p style={{ color: "gray" }}>
          Password must be at least {passwordPolicy.minLength} characters
          {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
          {passwordPolicy.requireNumbers ? ", include numbers" : ""}
          {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
          </p>
        </form>
      ) : (
        <form onSubmit={handleConfirm}>
          <h2>Confirm Code</h2>
          <label>Confirmation Code</label>
          <input
            type="text"
            value={confirmationCode}
            onChange={(e) => setConfirmationCode(e.target.value)}
            required
          />
          <button type="submit">Confirm</button>
        </form>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      <div style={{ marginTop: "10px" }}>
        <button onClick={() => navigate("/login")}>Back to Login</button>
      </div>
    </div>
  );
}
