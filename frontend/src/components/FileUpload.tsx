import { useState } from "react";

export default function FileUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);

  async function handleUpload() {
    if (!selectedFile) return;
    // Mock upload progress
    for (let i = 0; i <= 100; i += 10) {
      setTimeout(() => setProgress(i), i * 20);
    }
  }

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-2">Upload File</h3>
      <input
        type="file"
        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
      />
      <button
        onClick={handleUpload}
        disabled={!selectedFile}
        className="ml-2 bg-blue-500 text-white px-3 py-1 rounded"
      >
        Upload
      </button>
      {progress > 0 && (
        <div className="mt-2 w-64 bg-gray-200 rounded">
          <div
            className="bg-blue-600 h-2 rounded"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  );
}
