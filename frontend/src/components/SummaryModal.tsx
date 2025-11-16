import { useEffect, useState } from "react";
import { SafeResponse } from "../utils/SafeResponse";

export default function SummaryModal({
  fileId,
  onClose,
}: {
  fileId: number;
  onClose: () => void;
}) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchSummary() {
      setLoading(true);
      setError("");
      
      try {
        const res = await fetch("/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fileId }),
        });

        if (!res.ok) {
          throw new Error(`Failed to generate summary: ${res.status}`);
        }

        const data = await SafeResponse(res);

        if (typeof data === "object" && data !== null && "summary" in data) {
          setSummary(data.summary);
        } else if (typeof data === "string") {
          setSummary(data);
        } else {
          throw new Error("Invalid response format");
        }
      } catch (err: any) {
        setError(err.message || "Failed to generate summary");
        setSummary("");
      } finally {
        setLoading(false);
      }
    }

    fetchSummary();
  }, [fileId]);

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3 style={{ marginTop: 0 }}>AI-Generated File Summary</h3>

        {/* Loading State */}
        {loading && (
          <div style={{ textAlign: "center", padding: "2rem" }}>
            <div style={{
              border: "4px solid #f3f3f3",
              borderTop: "4px solid #1e90ff",
              borderRadius: "50%",
              width: "40px",
              height: "40px",
              animation: "spin 1s linear infinite",
              margin: "0 auto"
            }} />
            <p style={{ marginTop: "15px", color: "#666" }}>
              Generating AI summary...
            </p>
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div style={{
            background: "#f8d7da",
            border: "1px solid #f5c6cb",
            color: "#721c24",
            padding: "15px",
            borderRadius: "5px",
            marginBottom: "15px",
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Success State */}
        {summary && !loading && !error && (
          <div style={{
            background: "#f8f9fa",
            padding: "15px",
            borderRadius: "5px",
            marginBottom: "15px",
            maxHeight: "400px",
            overflowY: "auto",
            lineHeight: "1.6",
          }}>
            {summary}
          </div>
        )}

        {/* No Summary Available */}
        {!summary && !loading && !error && (
          <p style={{ color: "#666", textAlign: "center", padding: "20px" }}>
            No summary available for this file.
          </p>
        )}

        <button onClick={onClose} style={buttonStyle}>Close</button>
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
  width: "500px",
  maxWidth: "90vw",
  boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
  maxHeight: "90vh",
  overflowY: "auto",
} as const;

const buttonStyle = {
  marginTop: "10px",
  width: "100%",
  padding: "10px",
  background: "#1e90ff",
  color: "white",
  border: "none",
  borderRadius: "6px",
  cursor: "pointer",
  fontWeight: "500",
} as const;