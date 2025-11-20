import { useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUpload from "./FileUpload";
import SummaryModal from "./SummaryModal";
import DeleteModal from "./DeleteModal";
import ShareModal from "./ShareModal";
import { useFileList, useFileDownload, useFileDelete } from "../hooks/useFiles";
import { useAuth } from "../hooks/useAuth";
import FileService from "../services/fileService";

interface FileItem {
  id: string;
  name: string;
  size: string;
  date: string;
  type: string;
  folder?: string;
}

export default function FileList() {
  const navigate = useNavigate();

  // Use the file list hook
  const { files: fileMetadata, loading, error, refetch } = useFileList();

  // Use the download hook
  const { downloadFile } = useFileDownload();

  // Use the delete hook
  const { deleteFile } = useFileDelete();

  // Use the auth hook
  const { signOut, user } = useAuth();

  // Map FileMetadata to FileItem for display
  const files: FileItem[] = fileMetadata.map((file) => ({
    id: file.fileId,
    name: file.fileName,
    size: file.size ? FileService.formatFileSize(file.size) : 'Unknown',
    date: FileService.formatRelativeTime(file.uploadDate),
    type: FileService.getFileType(file.fileName, file.contentType),
    folder: file.folder || "root",
  }));

  const [currentFolder, setCurrentFolder] = useState("root");
  const [summaryFileId, setSummaryFileId] = useState<string | null>(null);
  const [deleteFileId, setDeleteFileId] = useState<string | null>(null);
  const [shareFileId, setShareFileId] = useState<string | null>(null);

  const visibleFiles = files.filter((f) => f.folder === currentFolder);

  function handleSummarize(fileId: string) {
    setSummaryFileId(fileId);
  }

  function handleDelete(fileId: string) {
    setDeleteFileId(fileId);
  }

  function handleShare(fileId: string) {
    setShareFileId(fileId);
  }

  async function confirmDelete() {
    if (!deleteFileId) return;

    const success = await deleteFile(deleteFileId);

    if (success) {
      // Close the modal
      setDeleteFileId(null);
      // Refresh the file list
      await refetch();
    }
  }

  function cancelDelete() {
    setDeleteFileId(null);
  }

  async function handleDownload(id: string, name: string) {
    await downloadFile(id, name);
  }

  async function handleLogout() {
    await signOut();
    navigate("/login");
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "24px", fontWeight: "bold", margin: 0 }}>My Files</h2>
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            {user && (
              <span style={{ color: "#666", fontSize: "14px" }}>
                {user.email}
              </span>
            )}
            <button
              onClick={handleLogout}
              style={{
                padding: "8px 16px",
                background: "#dc3545",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: "pointer",
                fontWeight: "500",
                fontSize: "14px",
              }}
            >
              Logout
            </button>
          </div>
        </div>

        <FileUpload onUploadSuccess={refetch} />

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
          <SummaryModal
            fileId={summaryFileId}
            fileName={files.find((x) => x.id === summaryFileId)?.name || ''}
            onClose={() => setSummaryFileId(null)}
          />
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