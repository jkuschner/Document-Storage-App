import { useState, useEffect } from "react";
import FileUpload from "./FileUpload";
import SummaryModal from "./SummaryModal";
import DeleteModal from "./DeleteModal";
import ShareModal from "./ShareModal";

interface FileItem {
  id: number;
  name: string;
  size: string;
  date: string;
  type: string;
  folder?: string;
}

export default function FileList() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [currentFolder, setCurrentFolder] = useState("root");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [summaryFileId, setSummaryFileId] = useState<number | null>(null);
  const [deleteFileId, setDeleteFileId] = useState<number | null>(null);
  const [shareFileId, setShareFileId] = useState<number | null>(null);

  // Load files
  useEffect(() => {
  async function fetchFiles() {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch("/files");
      
      console.log("Response status:", res.status);
      console.log("Response headers:", res.headers);
      
      if (!res.ok) {
        throw new Error(`Failed to fetch files: ${res.status}`);
      }
      
      const text = await res.text();
      console.log("Response text:", text); // See what we got
      
      try {
        const data = JSON.parse(text);
        console.log("Parsed data:", data); // See parsed result
        setFiles(data);
      } catch (parseError) {
        console.error("❌ /files returned non-JSON:", text);
        throw new Error("Invalid response format from server");
      }
    } catch (err: any) {
      setError(err.message || "Failed to load files");
      setFiles([]);
    } finally {
      setLoading(false);
    }
  }

  fetchFiles();
}, []);

  const visibleFiles = files.filter((f) => f.folder === currentFolder);

  function handleSummarize(fileId: number) {
    setSummaryFileId(fileId);
  }

  function handleDelete(fileId: number) {
    setDeleteFileId(fileId);
  }

  function handleShare(fileId: number) {
    setShareFileId(fileId);
  }

  async function confirmDelete() {
    if (!deleteFileId) return;

    try {
      const res = await fetch(`/files/${deleteFileId}`, { method: "DELETE" });
      
      if (!res.ok) {
        throw new Error("Failed to delete file");
      }

      setFiles((prev) => prev.filter((f) => f.id !== deleteFileId));
      setDeleteFileId(null);
    } catch (err: any) {
      alert(err.message || "Failed to delete file");
    }
  }

  function cancelDelete() {
    setDeleteFileId(null);
  }

  function handleDownload(id: number, name: string) {
    try {
      const link = document.createElement("a");
      link.href = `/download/${id}`;
      link.download = name;
      link.click();
    } catch (err) {
      alert("Failed to download file");
    }
  }

  const folders = Array.from(
    new Set(
      files
        .map((f) => f.folder)
        .filter((folder): folder is string => typeof folder === "string")
    )
  ).filter((f) => f !== currentFolder);

  return (
    <div style={{ background: "#add8e6", minHeight: "100vh", padding: "2rem" }}>
      <div
        style={{
          background: "white",
          padding: "2rem",
          borderRadius: "10px",
          boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
          width: "800px",
          margin: "auto",
        }}
      >
        <h2 style={{ fontSize: "24px", fontWeight: "bold" }}>My Files</h2>

        <FileUpload />

        <div style={{ margin: "20px 0" }}>
          <strong>Current Folder:</strong> {currentFolder}

          {currentFolder !== "root" && (
            <button
              onClick={() => setCurrentFolder("root")}
              style={{ color: "#1e90ff", marginLeft: "10px", background: "none", border: "none", cursor: "pointer" }}
            >
              ⬅️ Back to Root
            </button>
          )}

          {folders.map((f) => (
            <button
              key={f}
              onClick={() => setCurrentFolder(f)}
              style={{ color: "#1e90ff", marginLeft: "10px", background: "none", border: "none", cursor: "pointer" }}
            >
              📁 Open {f}
            </button>
          ))}
        </div>

        {/* Loading Spinner */}
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
            <p style={{ marginTop: "10px", color: "#666" }}>Loading files...</p>
            <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
          </div>
        )}

        {/* Error Message */}
        {error && !loading && (
          <div style={{
            background: "#fee",
            border: "1px solid #fcc",
            borderRadius: "8px",
            padding: "1rem",
            marginBottom: "1rem",
            color: "#c33"
          }}>
            <strong>Error:</strong> {error}
            <button
              onClick={() => window.location.reload()}
              style={{
                marginLeft: "10px",
                padding: "4px 8px",
                background: "#c33",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            >
              Retry
            </button>
          </div>
        )}

        {/* Files Table */}
        {!loading && !error && (
          <>
            {visibleFiles.length === 0 ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "#666" }}>
                <p>No files in this folder</p>
              </div>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #ddd" }}>
                    <th style={{ textAlign: "left", padding: "10px" }}>Name</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Type</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Size</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Date</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {visibleFiles.map((file) => (
                    <tr key={file.id} style={{ borderBottom: "1px solid #eee" }}>
                      <td style={{ padding: "10px" }}>{file.name}</td>
                      <td style={{ padding: "10px" }}>{file.type}</td>
                      <td style={{ padding: "10px" }}>{file.size}</td>
                      <td style={{ padding: "10px" }}>{file.date}</td>
                      <td style={{ padding: "10px" }}>
                        <button
                          onClick={() => handleDownload(file.id, file.name)}
                          style={{ color: "#1e90ff", background: "none", border: "none", marginRight: "8px", cursor: "pointer" }}
                          title="Download file"
                        >
                          Download
                        </button>

                        <button
                          onClick={() => handleSummarize(file.id)}
                          style={{ color: "purple", background: "none", border: "none", marginRight: "8px", cursor: "pointer" }}
                          title="AI Summary"
                        >
                          Summarize
                        </button>

                        <button
                          onClick={() => handleShare(file.id)}
                          style={{ color: "green", background: "none", border: "none", marginRight: "8px", cursor: "pointer" }}
                          title="Share file"
                        >
                          Share
                        </button>

                        <button
                          onClick={() => handleDelete(file.id)}
                          style={{ color: "red", background: "none", border: "none", cursor: "pointer" }}
                          title="Delete file"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}

        {/* Modals */}
        {summaryFileId !== null && (
          <SummaryModal fileId={summaryFileId} onClose={() => setSummaryFileId(null)} />
        )}

        {deleteFileId !== null && (
          <DeleteModal
            file={files.find((x) => x.id === deleteFileId)!}
            onCancel={cancelDelete}
            onConfirm={confirmDelete}
          />
        )}

        {shareFileId !== null && (
          <ShareModal
            file={files.find((x) => x.id === shareFileId)!}
            onClose={() => setShareFileId(null)}
          />
        )}
      </div>
    </div>
  );
}