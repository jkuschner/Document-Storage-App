import { useState } from "react";
import { signUp, confirmSignUp } from "@aws-amplify/auth";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmationCode, setConfirmationCode] = useState("");
  const [stage, setStage] = useState<"signup" | "confirm">("signup");
  const navigate = useNavigate();

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    try {
      await signUp({
        username: email,
        password,
      });
      setStage("confirm");
    } catch (err: any) {
      console.error(err);
    }
  }

  async function handleConfirm(e: React.FormEvent) {
    e.preventDefault();
    try {
      await confirmSignUp({
        username: email,
        confirmationCode,
      });
      navigate("/login");
    } catch (err: any) {
      console.error(err);
    }
  }

  return (
    <div>
      {stage === "signup" ? (
        <form onSubmit={handleSignup}>
          <h2>Sign Up</h2>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button type="submit">Create Account</button>
        </form>
      ) : (
        <form onSubmit={handleConfirm}>
          <h2>Confirm Code</h2>
          <input type="text" value={confirmationCode} onChange={(e) => setConfirmationCode(e.target.value)} />
          <button type="submit">Confirm</button>
        </form>
      )}
    </div>
  );
}
