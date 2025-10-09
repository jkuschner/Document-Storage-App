
import React from "react";

const FileList: React.FC = () => {
  const files = [
    { name: "report.pdf", size: "2MB" },
    { name: "photo.png", size: "500KB" },
  ];

  return (
    <div>
      <h2>Your Files</h2>
      <ul>
        {files.map((f, i) => (
          <li key={i}>
            {f.name} — {f.size}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileList;
