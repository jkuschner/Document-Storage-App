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
        <h3>Delete File</h3>
        <p>Are you sure you want to delete <strong>{file.name}</strong>?</p>

        <div style={{ marginTop: "20px", textAlign: "right" }}>
          <button onClick={onCancel} style={cancelStyle}>Cancel</button>
          <button onClick={onConfirm} style={deleteStyle}>Delete</button>
        </div>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.4)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
} as const;

const modalStyle = {
  background: "white",
  padding: "20px",
  borderRadius: "8px",
  width: "350px",
  boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
} as const;

const cancelStyle = {
  padding: "8px 12px",
  marginRight: "10px",
  background: "#ddd",
  border: "none",
  borderRadius: "5px",
} as const;

const deleteStyle = {
  padding: "8px 12px",
  background: "red",
  color: "white",
  border: "none",
  borderRadius: "5px",
} as const;
