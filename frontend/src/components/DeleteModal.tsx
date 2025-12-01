export default function DeleteModal({
  file,
  onConfirm,
  onCancel,
}: {
  file: { id: number; name: string };
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <h3 style={{
          margin: "0 0 16px 0",
          fontSize: "20px",
          fontWeight: "600",
          color: "#1e293b",
        }}>
          Delete file?
        </h3>
        
        <p style={{
          margin: "0 0 24px 0",
          fontSize: "14px",
          color: "#6b7280",
          lineHeight: "1.5",
        }}>
          Are you sure you want to delete <strong style={{ color: "#1e293b" }}>{file.name}</strong>? This action cannot be undone.
        </p>

        <div style={{
          display: "flex",
          gap: "12px",
          justifyContent: "flex-end",
        }}>
          <button
            onClick={onCancel}
            style={{
              padding: "10px 20px",
              background: "white",
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              fontSize: "14px",
              fontWeight: "600",
              color: "#374151",
              cursor: "pointer",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#f9fafb"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "white"}
          >
            Cancel
          </button>
          
          <button
            onClick={onConfirm}
            style={{
              padding: "10px 20px",
              background: "#dc2626",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontSize: "14px",
              fontWeight: "600",
              cursor: "pointer",
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#b91c1c"}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "#dc2626"}
          >
            Delete
          </button>
        </div>
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
  padding: "24px",
  borderRadius: "8px",
  width: "420px",
  maxWidth: "90vw",
  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
} as const;