import { useState } from "react";
import FileUpload from "./FileUpload";

interface FileItem {
  id: number;
  name: string;
  size: string;
  date: string;
  type: string;
  folder?: string;
}

export default function FileList() {
  const [files, setFiles] = useState<FileItem[]>([
    { id: 1, name: "report.pdf", size: "1.2 MB", date: "2025-10-14", type: "PDF", folder: "root" },
    { id: 2, name: "photo.png", size: "3.4 MB", date: "2025-10-12", type: "Image", folder: "Photos" },
    { id: 3, name: "notes.txt", size: "15 KB", date: "2025-10-10", type: "Text", folder: "root" },
  ]);

  const [currentFolder, setCurrentFolder] = useState<string>("root");

  const visibleFiles = files.filter((file) => file.folder === currentFolder);

  function handleDelete(id: number) {
    setFiles((prev) => prev.filter((file) => file.id !== id));
  }

  function handleDownload(fileName: string) {
    alert(`Downloading ${fileName}...`);
  }

  function navigateTo(folder: string) {
    setCurrentFolder(folder);
  }

  const folders = Array.from(new Set(files.map((f) => f.folder))).filter((f) => f !== currentFolder);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">My Files</h2>

      {/* Upload Section */}
      <FileUpload />

      {/* Folder Navigation */}
      <div className="my-4">
        <p className="font-semibold">Current Folder: {currentFolder}</p>
        {currentFolder !== "root" && (
          <button
            onClick={() => navigateTo("root")}
            className="text-blue-500 hover:underline mr-2"
          >
            Back to Root
          </button>
        )}
        {folders.map((f) => (
          <button
            key={f}
            onClick={() => navigateTo(f)}
            className="text-blue-500 hover:underline mr-2"
          >
            Open {f}
          </button>
        ))}
      </div>

      {/* File Table */}
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b">
            <th className="text-left p-2">Name</th>
            <th className="text-left p-2">Type</th>
            <th className="text-left p-2">Size</th>
            <th className="text-left p-2">Date</th>
            <th className="text-left p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {visibleFiles.map((file) => (
            <tr key={file.id} className="border-b hover:bg-gray-50">
              <td className="p-2">{file.name}</td>
              <td className="p-2">{file.type}</td>
              <td className="p-2">{file.size}</td>
              <td className="p-2">{file.date}</td>
              <td className="p-2 space-x-2">
                <button
                  onClick={() => handleDownload(file.name)}
                  className="text-blue-500 hover:underline"
                >
                  Download
                </button>
                <button
                  onClick={() => handleDelete(file.id)}
                  className="text-red-500 hover:underline"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
