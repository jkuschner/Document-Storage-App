import { useState, useEffect } from "react";
import { useFileShare } from "../hooks/useFiles";

export default function ShareModal({
  file,
  onClose,
}: {
  file: { id: string; name: string };
  onClose: () => void;
}) {
  const { shareFile, sharing, shareUrl, error } = useFileShare();
  const [linkCopied, setLinkCopied] = useState(false);
  const [expirationHours, setExpirationHours] = useState(24);

  // Generate share link when modal opens
  useEffect(() => {
    shareFile(file.id, expirationHours);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [file.id]); // Only run once when modal opens

  async function handleGenerateLink() {
    await shareFile(file.id, expirationHours);
  }

  function copyLink() {
    if (shareUrl) {
      navigator.clipboard.writeText(shareUrl);
      setLinkCopied(true);
      setTimeout(() => setLinkCopied(false), 2000);
    }
  }

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3 style={{ marginTop: 0 }}>Share File</h3>
        <p style={{ color: "#666", marginBottom: "20px" }}>
          <strong>{file.name}</strong>
        </p>

        {/* Expiration Time Selector */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Link Expiration
          </label>
          <select
            value={expirationHours}
            onChange={(e) => setExpirationHours(Number(e.target.value))}
            style={{
              width: "100%",
              padding: "8px",
              borderRadius: "5px",
              border: "1px solid #ccc",
              marginBottom: "10px",
            }}
          >
            <option value={1}>1 hour</option>
            <option value={6}>6 hours</option>
            <option value={24}>24 hours</option>
            <option value={72}>3 days</option>
            <option value={168}>7 days</option>
          </select>

          <button
            onClick={handleGenerateLink}
            disabled={sharing}
            style={{
              width: "100%",
              padding: "10px",
              background: sharing ? "#ccc" : "#28a745",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: sharing ? "not-allowed" : "pointer",
              fontWeight: "500",
            }}
          >
            {sharing ? "Generating..." : "Generate Share Link"}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            background: "#f8d7da",
            border: "1px solid #f5c6cb",
            color: "#721c24",
            padding: "10px",
            borderRadius: "5px",
            marginBottom: "15px",
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Share Link Section */}
        {shareUrl && (
          <div style={{
            borderTop: "1px solid #ddd",
            paddingTop: "15px",
            marginBottom: "15px",
          }}>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
              Share Link
            </label>
            <div style={{ display: "flex", gap: "10px" }}>
              <input
                type="text"
                value={shareUrl}
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
            <p style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}>
              This link will expire in {expirationHours} hour{expirationHours > 1 ? 's' : ''}
            </p>
          </div>
        )}

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