import { useState } from "react";

export default function FileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);

  async function handleUpload() {
    if (!selectedFile) return;

    for (let i = 0; i <= 100; i += 10) {
      setTimeout(() => setProgress(i), i * 20);
    }
  }

  return (
    <div
      style={{
        background: "white",
        padding: "20px",
        borderRadius: "8px",
        marginBottom: "24px",
        border: "1px solid #e5e7eb",
      }}
    >
      <h3 style={{
        fontSize: "16px",
        fontWeight: "600",
        marginBottom: "16px",
        color: "#1e293b",
        margin: "0 0 16px 0",
      }}>
        Upload File
      </h3>

      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <input
          type="file"
          onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          style={{
            fontSize: "14px",
            color: "#6b7280",
          }}
        />

        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          style={{
            backgroundColor: selectedFile ? "#16a34a" : "#d1d5db",
            color: "white",
            border: "none",
            padding: "10px 20px",
            borderRadius: "6px",
            cursor: selectedFile ? "pointer" : "not-allowed",
            fontSize: "14px",
            fontWeight: "600",
            transition: "background-color 0.2s",
          }}
          onMouseEnter={(e) => {
            if (selectedFile) e.currentTarget.style.backgroundColor = "#15803d";
          }}
          onMouseLeave={(e) => {
            if (selectedFile) e.currentTarget.style.backgroundColor = "#16a34a";
          }}
        >
          Upload
        </button>
      </div>

      {progress > 0 && (
        <div style={{ marginTop: "16px" }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "8px",
            fontSize: "14px",
            color: "#6b7280",
          }}>
            <span>Uploading {selectedFile?.name}...</span>
            <span>{progress}%</span>
          </div>
          <div
            style={{
              width: "100%",
              background: "#e5e7eb",
              height: "8px",
              borderRadius: "4px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: "8px",
                background: "#16a34a",
                borderRadius: "4px",
                transition: "width 0.3s ease",
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}