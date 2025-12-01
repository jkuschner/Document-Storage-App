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

  useEffect(() => {
    async function fetchFiles() {
      setLoading(true);
      setError(null);
      
      try {
        const res = await fetch("/files");
        
        if (!res.ok) {
          throw new Error(`Failed to fetch files: ${res.status}`);
        }
        
        const text = await res.text();
        
        try {
          const data = JSON.parse(text);
          setFiles(data);
        } catch (parseError) {
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
    <div style={{ 
      background: "#f7f9fa", 
      minHeight: "100vh",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    }}>
      {/* Header Bar */}
      <div style={{
        background: "white",
        borderBottom: "1px solid #e5e7eb",
        padding: "16px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <h1 style={{ 
          margin: 0, 
          fontSize: "20px", 
          fontWeight: "600",
          color: "#1e293b",
        }}>
          My Files
        </h1>
      </div>

      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "32px 24px" }}>
        <FileUpload />

        {/* Breadcrumb Navigation */}
        <div style={{ 
          marginBottom: "24px",
          padding: "12px 16px",
          background: "white",
          borderRadius: "8px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          fontSize: "14px",
        }}>
          <button
            onClick={() => setCurrentFolder("root")}
            style={{
              background: "none",
              border: "none",
              color: currentFolder === "root" ? "#1e293b" : "#16a34a",
              cursor: currentFolder === "root" ? "default" : "pointer",
              fontSize: "14px",
              fontWeight: currentFolder === "root" ? "600" : "500",
              padding: "4px 8px",
              borderRadius: "4px",
            }}
            onMouseEnter={(e) => {
              if (currentFolder !== "root") e.currentTarget.style.backgroundColor = "#f0fdf4";
            }}
            onMouseLeave={(e) => {
              if (currentFolder !== "root") e.currentTarget.style.backgroundColor = "transparent";
            }}
          >
            Home
          </button>

          {currentFolder !== "root" && (
            <>
              <span style={{ color: "#9ca3af" }}>/</span>
              <span style={{ color: "#1e293b", fontWeight: "600" }}>{currentFolder}</span>
            </>
          )}

          {folders.length > 0 && (
            <div style={{ marginLeft: "auto", display: "flex", gap: "8px" }}>
              {folders.map((f) => (
                <button
                  key={f}
                  onClick={() => setCurrentFolder(f)}
                  style={{
                    background: "#f0fdf4",
                    border: "1px solid #bbf7d0",
                    color: "#15803d",
                    cursor: "pointer",
                    fontSize: "13px",
                    fontWeight: "500",
                    padding: "6px 12px",
                    borderRadius: "6px",
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#dcfce7"}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#f0fdf4"}
                >
                  {f}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div style={{
            background: "white",
            borderRadius: "8px",
            padding: "64px",
            textAlign: "center",
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
            <p style={{ marginTop: "16px", color: "#6b7280", fontSize: "14px" }}>
              Loading files...
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
            background: "white",
            borderRadius: "8px",
            padding: "24px",
            border: "1px solid #fecaca",
          }}>
            <div style={{
              color: "#b91c1c",
              fontSize: "14px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
            }}>
              <div>
                <strong>Error:</strong> {error}
              </div>
            </div>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: "16px",
                padding: "8px 16px",
                background: "#dc2626",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "500",
              }}
            >
              Retry
            </button>
          </div>
        )}

        {/* Files Table */}
        {!loading && !error && (
          <div style={{
            background: "white",
            borderRadius: "8px",
            overflow: "hidden",
            border: "1px solid #e5e7eb",
          }}>
            {visibleFiles.length === 0 ? (
              <div style={{
                textAlign: "center",
                padding: "64px 24px",
                color: "#9ca3af",
              }}>
                <p style={{ fontSize: "16px", margin: 0 }}>No files in this folder</p>
              </div>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{
                    background: "#f9fafb",
                    borderBottom: "1px solid #e5e7eb",
                  }}>
                    <th style={{
                      textAlign: "left",
                      padding: "14px 16px",
                      fontSize: "12px",
                      fontWeight: "600",
                      color: "#6b7280",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      Name
                    </th>
                    <th style={{
                      textAlign: "left",
                      padding: "14px 16px",
                      fontSize: "12px",
                      fontWeight: "600",
                      color: "#6b7280",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      Type
                    </th>
                    <th style={{
                      textAlign: "left",
                      padding: "14px 16px",
                      fontSize: "12px",
                      fontWeight: "600",
                      color: "#6b7280",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      Size
                    </th>
                    <th style={{
                      textAlign: "left",
                      padding: "14px 16px",
                      fontSize: "12px",
                      fontWeight: "600",
                      color: "#6b7280",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      Modified
                    </th>
                    <th style={{
                      textAlign: "right",
                      padding: "14px 16px",
                      fontSize: "12px",
                      fontWeight: "600",
                      color: "#6b7280",
                      textTransform: "uppercase",
                      letterSpacing: "0.05em",
                    }}>
                      Actions
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {visibleFiles.map((file, index) => (
                    <tr
                      key={file.id}
                      style={{
                        borderBottom: index < visibleFiles.length - 1 ? "1px solid #f3f4f6" : "none",
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f9fafb"}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "white"}
                    >
                      <td style={{
                        padding: "14px 16px",
                        fontSize: "14px",
                        color: "#1e293b",
                        fontWeight: "500",
                      }}>
                        {file.name}
                      </td>
                      <td style={{
                        padding: "14px 16px",
                        fontSize: "14px",
                        color: "#6b7280",
                      }}>
                        {file.type}
                      </td>
                      <td style={{
                        padding: "14px 16px",
                        fontSize: "14px",
                        color: "#6b7280",
                      }}>
                        {file.size}
                      </td>
                      <td style={{
                        padding: "14px 16px",
                        fontSize: "14px",
                        color: "#6b7280",
                      }}>
                        {file.date}
                      </td>
                      <td style={{
                        padding: "14px 16px",
                        textAlign: "right",
                      }}>
                        <div style={{ display: "flex", gap: "4px", justifyContent: "flex-end" }}>
                          <button
                            onClick={() => handleDownload(file.id, file.name)}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#16a34a",
                              fontSize: "13px",
                              fontWeight: "500",
                              cursor: "pointer",
                              padding: "6px 10px",
                              borderRadius: "4px",
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0fdf4"}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                            title="Download"
                          >
                            Download
                          </button>

                          <button
                            onClick={() => handleSummarize(file.id)}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#8b5cf6",
                              fontSize: "13px",
                              fontWeight: "500",
                              cursor: "pointer",
                              padding: "6px 10px",
                              borderRadius: "4px",
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#faf5ff"}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                            title="AI Summary"
                          >
                            Summarize
                          </button>

                          <button
                            onClick={() => handleShare(file.id)}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#16a34a",
                              fontSize: "13px",
                              fontWeight: "500",
                              cursor: "pointer",
                              padding: "6px 10px",
                              borderRadius: "4px",
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f0fdf4"}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                            title="Share"
                          >
                            Share
                          </button>

                          <button
                            onClick={() => handleDelete(file.id)}
                            style={{
                              background: "none",
                              border: "none",
                              color: "#dc2626",
                              fontSize: "13px",
                              fontWeight: "500",
                              cursor: "pointer",
                              padding: "6px 10px",
                              borderRadius: "4px",
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#fee"}
                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
                            title="Delete"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
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