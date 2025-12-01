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
        <h3 style={{
          margin: "0 0 8px 0",
          fontSize: "20px",
          fontWeight: "600",
          color: "#1e293b",
        }}>
          Share file
        </h3>
        
        <p style={{
          margin: "0 0 24px 0",
          fontSize: "14px",
          color: "#6b7280",
        }}>
          <strong style={{ color: "#1e293b" }}>{file.name}</strong>
        </p>

        {/* Share via Email */}
        <form onSubmit={handleShare} style={{ marginBottom: "24px" }}>
          <label style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "14px",
            fontWeight: "500",
            color: "#374151",
          }}>
            Share with email
          </label>
          <input
            type="email"
            placeholder="colleague@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "6px",
              border: "1px solid #d1d5db",
              fontSize: "14px",
              marginBottom: "12px",
              boxSizing: "border-box",
              outline: "none",
            }}
            onFocus={(e) => e.target.style.borderColor = "#16a34a"}
            onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
          />

          <label style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "14px",
            fontWeight: "500",
            color: "#374151",
          }}>
            Permission
          </label>
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value as "view" | "edit")}
            style={{
              width: "100%",
              padding: "10px 12px",
              borderRadius: "6px",
              border: "1px solid #d1d5db",
              fontSize: "14px",
              marginBottom: "16px",
              boxSizing: "border-box",
              outline: "none",
              cursor: "pointer",
            }}
            onFocus={(e) => e.target.style.borderColor = "#16a34a"}
            onBlur={(e) => e.target.style.borderColor = "#d1d5db"}
          >
            <option value="view">Can view</option>
            <option value="edit">Can edit</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              background: loading ? "#d1d5db" : "#16a34a",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "600",
              fontSize: "14px",
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = "#15803d";
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = "#16a34a";
            }}
          >
            {loading ? "Sharing..." : "Share"}
          </button>
        </form>

        {/* Success/Error Messages */}
        {message && (
          <div style={{
            background: "#dcfce7",
            border: "1px solid #bbf7d0",
            color: "#15803d",
            padding: "12px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
          }}>
            {message}
          </div>
        )}

        {error && (
          <div style={{
            background: "#fee",
            border: "1px solid #fcc",
            color: "#b91c1c",
            padding: "12px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
          }}>
            {error}
          </div>
        )}

        {/* Copy Link Section */}
        <div style={{
          borderTop: "1px solid #e5e7eb",
          paddingTop: "20px",
          marginTop: "20px",
        }}>
          <label style={{
            display: "block",
            marginBottom: "8px",
            fontSize: "14px",
            fontWeight: "500",
            color: "#374151",
          }}>
            Or copy link
          </label>
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              type="text"
              value={shareLink}
              readOnly
              style={{
                flex: 1,
                padding: "10px 12px",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
                background: "#f9fafb",
                fontSize: "14px",
                color: "#6b7280",
              }}
            />
            <button
              onClick={copyLink}
              style={{
                padding: "10px 16px",
                background: linkCopied ? "#16a34a" : "white",
                color: linkCopied ? "white" : "#374151",
                border: linkCopied ? "none" : "1px solid #d1d5db",
                borderRadius: "6px",
                cursor: "pointer",
                fontWeight: "600",
                minWidth: "80px",
                fontSize: "14px",
              }}
              onMouseEnter={(e) => {
                if (!linkCopied) e.currentTarget.style.backgroundColor = "#f9fafb";
              }}
              onMouseLeave={(e) => {
                if (!linkCopied) e.currentTarget.style.backgroundColor = "white";
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
            padding: "12px",
            background: "#6b7280",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "14px",
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#4b5563"}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#6b7280"}
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
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
} as const;

const modalStyle = {
  background: "white",
  padding: "28px",
  borderRadius: "8px",
  width: "480px",
  maxWidth: "90vw",
  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  maxHeight: "90vh",
  overflowY: "auto",
} as const;