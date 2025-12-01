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
        <h3 style={{
          margin: "0 0 20px 0",
          fontSize: "20px",
          fontWeight: "600",
          color: "#1e293b",
        }}>
          AI-generated summary
        </h3>

        {/* Loading State */}
        {loading && (
          <div style={{
            textAlign: "center",
            padding: "48px 24px",
          }}>
            <div style={{
              border: "4px solid #f3f3f3",
              borderTop: "4px solid #16a34a",
              borderRadius: "50%",
              width: "48px",
              height: "48px",
              animation: "spin 1s linear infinite",
              margin: "0 auto",
            }} />
            <p style={{
              marginTop: "20px",
              color: "#6b7280",
              fontSize: "14px",
            }}>
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
            background: "#fee",
            border: "1px solid #fcc",
            color: "#b91c1c",
            padding: "16px",
            borderRadius: "6px",
            marginBottom: "16px",
            fontSize: "14px",
          }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Success State */}
        {summary && !loading && !error && (
          <div style={{
            background: "#f9fafb",
            padding: "20px",
            borderRadius: "6px",
            marginBottom: "20px",
            maxHeight: "400px",
            overflowY: "auto",
            lineHeight: "1.6",
            fontSize: "14px",
            color: "#374151",
            border: "1px solid #e5e7eb",
          }}>
            {summary}
          </div>
        )}

        {/* No Summary Available */}
        {!summary && !loading && !error && (
          <div style={{
            textAlign: "center",
            padding: "48px 24px",
            color: "#9ca3af",
          }}>
            <p style={{ fontSize: "14px", margin: 0 }}>
              No summary available for this file.
            </p>
          </div>
        )}

        <button
          onClick={onClose}
          style={{
            width: "100%",
            padding: "12px",
            background: "#16a34a",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontWeight: "600",
            fontSize: "14px",
          }}
          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#15803d"}
          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#16a34a"}
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
  width: "560px",
  maxWidth: "90vw",
  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  maxHeight: "90vh",
  overflowY: "auto",
} as const;