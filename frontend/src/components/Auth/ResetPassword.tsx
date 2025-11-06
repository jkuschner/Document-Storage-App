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
      navigate("/login");
    } catch (err: any) {
      setError(err.message || "Failed to reset password.");
    }
  }

  return (
    <div>
      {stage === "request" ? (
        <form onSubmit={requestReset}>
          <h2>Reset Password</h2>

          <label>Email</label>

          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <p style={{ color: "gray" }}>
                    Password must be at least {passwordPolicy.minLength} characters
                    {passwordPolicy.requireUppercase ? ", include uppercase letters" : ""}
                    {passwordPolicy.requireNumbers ? ", include numbers" : ""}
                    {passwordPolicy.requireSymbols ? ", include symbols" : ""}.
                    </p>

          <button type="submit">Send Code</button>

        </form>
      ) : (
        <form onSubmit={confirmReset}>
          
          <h2>Enter Code</h2>

          <label>Confirmation Code</label>

          <input
            type="text"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            required
          />

          <label>New Password</label>

          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />

          <button type="submit">Reset Password</button>

        </form>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}
      {message && <p style={{ color: "green" }}>{message}</p>}

      <div style={{ marginTop: "10px" }}>
        <button onClick={() => navigate("/login")}>Back to Login</button>
      </div>
    </div>
  );
}
