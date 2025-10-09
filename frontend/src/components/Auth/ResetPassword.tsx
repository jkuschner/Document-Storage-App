import { useState } from "react";
import { resetPassword, confirmResetPassword } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";

export default function ResetPassword() {
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [stage, setStage] = useState<"request" | "confirm">("request");
  const navigate = useNavigate();

  async function requestReset(e: React.FormEvent) {
    e.preventDefault();
    try {
      await resetPassword({ username: email });
      setStage("confirm");
    } catch (err: any) {
      console.error(err);
    }
  }

  async function confirmReset(e: React.FormEvent) {
    e.preventDefault();
    try {
      await confirmResetPassword({
        username: email,
        confirmationCode: code,
        newPassword,
      });
      navigate("/login");
    } catch (err: any) {
      console.error(err);
    }
  }

  return (
    <div>
      {stage === "request" ? (
        <form onSubmit={requestReset}>
          <h2>Reset Password</h2>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <button type="submit">Send Code</button>
        </form>
      ) : (
        <form onSubmit={confirmReset}>
          <h2>Enter Code</h2>
          <input type="text" value={code} onChange={(e) => setCode(e.target.value)} />
          <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          <button type="submit">Reset Password</button>
        </form>
      )}
    </div>
  );
}
