import { useState } from "react";

export default function ShareModal({
  file,
  onClose,
}: {
  file: { id: number; name: string };
  onClose: () => void;
}) {
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<"view" | "edit">("view");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const shareLink = `${window.location.origin}/shared/${file.id}`;
  const [linkCopied, setLinkCopied] = useState(false);

  async function handleShare(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const res = await fetch("/share", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileId: file.id,
          email,
          permission,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to share file");
      }

      setMessage(`File shared successfully with ${email}!`);
      setEmail("");
    } catch (err: any) {
      setError(err.message || "Failed to share file");
    } finally {
      setLoading(false);
    }
  }

  function copyLink() {
    navigator.clipboard.writeText(shareLink);
    setLinkCopied(true);
    setTimeout(() => setLinkCopied(false), 2000);
  }

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3 style={{ marginTop: 0 }}>Share File</h3>
        <p style={{ color: "#666", marginBottom: "20px" }}>
          <strong>{file.name}</strong>
        </p>

        {/* Share via Email */}
        <form onSubmit={handleShare} style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Share with Email
          </label>
          <input
            type="email"
            placeholder="colleague@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              marginBottom: "10px",
            }}
          />

          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Permission
          </label>
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value as "view" | "edit")}
            style={{
              width: "100%",
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              marginBottom: "15px",
            }}
          >
            <option value="view">View Only</option>
            <option value="edit">Can Edit</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "10px",
              background: loading ? "#ccc" : "#28a745",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "500",
            }}
          >
            {loading ? "Sharing..." : "Share"}
          </button>
        </form>

        {/* Success/Error Messages */}
        {message && (
          <div style={{
            background: "#d4edda",
            border: "1px solid #c3e6cb",
            color: "#155724",
            padding: "10px",
            borderRadius: "5px",
            marginBottom: "15px",
          }}>
            {message}
          </div>
        )}

        {error && (
          <div style={{
            background: "#f8d7da",
            border: "1px solid #f5c6cb",
            color: "#721c24",
            padding: "10px",
            borderRadius: "5px",
            marginBottom: "15px",
          }}>
            {error}
          </div>
        )}

        {/* Copy Link Section */}
        <div style={{
          borderTop: "1px solid #ddd",
          paddingTop: "15px",
          marginTop: "15px",
        }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Or copy share link
          </label>
          <div style={{ display: "flex", gap: "10px" }}>
            <input
              type="text"
              value={shareLink}
              readOnly
              style={{
                flex: 1,
                padding: "8px",
                borderRadius: "5px",
                border: "1px solid #ccc",
                background: "#f8f8f8",
              }}
            />
            <button
              onClick={copyLink}
              style={{
                padding: "8px 16px",
                background: linkCopied ? "#28a745" : "#1e90ff",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                fontWeight: "500",
                minWidth: "80px",
              }}
            >
              {linkCopied ? "✓ Copied" : "Copy"}
            </button>
          </div>
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            marginTop: "20px",
            width: "100%",
            padding: "10px",
            background: "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontWeight: "500",
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
} as const;

const modalStyle = {
  background: "white",
  padding: "25px",
  borderRadius: "10px",
  width: "450px",
  maxWidth: "90vw",
  boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
  maxHeight: "90vh",
  overflowY: "auto",
} as const;