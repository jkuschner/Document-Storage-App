import { useState } from "react";

export default function FileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);

  async function handleUpload() {
    if (!selectedFile) return;

    // Mock upload progress animation
    for (let i = 0; i <= 100; i += 10) {
      setTimeout(() => setProgress(i), i * 20);
    }
  }

  return (
    <div
      style={{
        background: "#f8f8f8",
        padding: "1rem",
        borderRadius: "8px",
        marginBottom: "20px",
        border: "1px solid #ddd",
      }}
    >
      <h3 style={{ fontSize: "18px", fontWeight: "600", marginBottom: "10px" }}>
        Upload File
      </h3>

      <input
        type="file"
        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
      />

      <button
        onClick={handleUpload}
        disabled={!selectedFile}
        style={{
          marginLeft: "10px",
          backgroundColor: "#1e90ff",
          color: "white",
          border: "none",
          padding: "6px 12px",
          borderRadius: "5px",
          cursor: "pointer",
          opacity: selectedFile ? 1 : 0.5,
        }}
      >
        Upload
      </button>

      {progress > 0 && (
        <div
          style={{
            marginTop: "10px",
            width: "250px",
            background: "#ddd",
            height: "8px",
            borderRadius: "4px",
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              height: "8px",
              background: "#1e90ff",
              borderRadius: "4px",
              transition: "width 0.3s",
            }}
          />
        </div>
      )}
    </div>
  );
}
