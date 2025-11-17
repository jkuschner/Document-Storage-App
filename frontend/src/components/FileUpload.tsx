import { useState } from "react";
import { useFileUpload } from "../hooks/useFiles";

export default function FileUpload({ onUploadSuccess }: { onUploadSuccess?: () => void }) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { uploadFile, uploading, progress, error } = useFileUpload();

  async function handleUpload() {
    if (!selectedFile) return;

    const fileId = await uploadFile(selectedFile);

    if (fileId) {
      // Upload successful
      setSelectedFile(null);
      // Reset the file input
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      // Trigger callback to refresh file list
      if (onUploadSuccess) {
        onUploadSuccess();
      }
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
        disabled={!selectedFile || uploading}
        style={{
          marginLeft: "10px",
          backgroundColor: "#1e90ff",
          color: "white",
          border: "none",
          padding: "6px 12px",
          borderRadius: "5px",
          cursor: selectedFile && !uploading ? "pointer" : "not-allowed",
          opacity: selectedFile && !uploading ? 1 : 0.5,
        }}
      >
        {uploading ? "Uploading..." : "Upload"}
      </button>

      {/* Error Message */}
      {error && (
        <div style={{
          marginTop: "10px",
          background: "#fee",
          border: "1px solid #fcc",
          borderRadius: "5px",
          padding: "8px",
          color: "#c33",
          fontSize: "14px",
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Progress Bar */}
      {uploading && progress > 0 && (
        <div style={{ marginTop: "10px" }}>
          <div
            style={{
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
          <p style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}>
            {progress}% uploaded
          </p>
        </div>
      )}
    </div>
  );
}
