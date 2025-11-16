import { useState, useEffect, useCallback } from 'react';
import FileService, { FileMetadata } from '../services/fileService';
import { ApiClientError } from '../services/api';

/**
 * Hook to manage file list with loading and error states
 */
export function useFileList() {
  const [files, setFiles] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadFiles = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const filesData = await FileService.listFiles();
      setFiles(filesData);
    } catch (err) {
      const errorMessage =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to load files';
      setError(errorMessage);
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFiles();
  }, [loadFiles]);

  return {
    files,
    loading,
    error,
    refetch: loadFiles,
  };
}

/**
 * Hook to handle file upload with progress tracking
 */
export function useFileUpload() {
  const [uploading, setUploading] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = useCallback(async (file: File): Promise<string | null> => {
    try {
      setUploading(true);
      setProgress(0);
      setError(null);

      const fileId = await FileService.uploadFile(file, (prog) => {
        setProgress(prog);
      });

      return fileId;
    } catch (err) {
      const errorMessage =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to upload file';
      setError(errorMessage);
      console.error('Error uploading file:', err);
      return null;
    } finally {
      setUploading(false);
      setProgress(0);
    }
  }, []);

  const reset = useCallback(() => {
    setUploading(false);
    setProgress(0);
    setError(null);
  }, []);

  return {
    uploadFile,
    uploading,
    progress,
    error,
    reset,
  };
}

/**
 * Hook to handle file download
 */
export function useFileDownload() {
  const [downloading, setDownloading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const downloadFile = useCallback(
    async (fileId: string, fileName: string): Promise<boolean> => {
      try {
        setDownloading(true);
        setError(null);

        const downloadUrl = await FileService.downloadFile(fileId);
        FileService.triggerDownload(downloadUrl, fileName);

        return true;
      } catch (err) {
        const errorMessage =
          err instanceof ApiClientError
            ? err.message
            : 'Failed to download file';
        setError(errorMessage);
        console.error('Error downloading file:', err);
        return false;
      } finally {
        setDownloading(false);
      }
    },
    []
  );

  return {
    downloadFile,
    downloading,
    error,
  };
}

/**
 * Hook to handle file deletion
 */
export function useFileDelete() {
  const [deleting, setDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const deleteFile = useCallback(async (fileId: string): Promise<boolean> => {
    try {
      setDeleting(true);
      setError(null);

      await FileService.deleteFile(fileId);

      return true;
    } catch (err) {
      const errorMessage =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to delete file';
      setError(errorMessage);
      console.error('Error deleting file:', err);
      return false;
    } finally {
      setDeleting(false);
    }
  }, []);

  return {
    deleteFile,
    deleting,
    error,
  };
}

/**
 * Hook to handle file sharing
 */
export function useFileShare() {
  const [sharing, setSharing] = useState<boolean>(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const shareFile = useCallback(
    async (fileId: string, expirationHours: number = 24): Promise<string | null> => {
      try {
        setSharing(true);
        setError(null);
        setShareUrl(null);

        const response = await FileService.shareFile(fileId, expirationHours);
        setShareUrl(response.shareUrl);

        return response.shareUrl;
      } catch (err) {
        const errorMessage =
          err instanceof ApiClientError
            ? err.message
            : 'Failed to share file';
        setError(errorMessage);
        console.error('Error sharing file:', err);
        return null;
      } finally {
        setSharing(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setShareUrl(null);
    setError(null);
  }, []);

  return {
    shareFile,
    sharing,
    shareUrl,
    error,
    reset,
  };
}

/**
 * Combined hook for all file operations
 * Useful for components that need multiple operations
 */
export function useFileOperations() {
  const fileList = useFileList();
  const upload = useFileUpload();
  const download = useFileDownload();
  const deleteOp = useFileDelete();
  const share = useFileShare();

  const handleUpload = useCallback(
    async (file: File) => {
      const fileId = await upload.uploadFile(file);
      if (fileId) {
        // Refresh file list after successful upload
        await fileList.refetch();
      }
      return fileId;
    },
    [upload, fileList]
  );

  const handleDelete = useCallback(
    async (fileId: string) => {
      const success = await deleteOp.deleteFile(fileId);
      if (success) {
        // Refresh file list after successful delete
        await fileList.refetch();
      }
      return success;
    },
    [deleteOp, fileList]
  );

  return {
    // File list
    files: fileList.files,
    loading: fileList.loading,
    error: fileList.error,
    refetch: fileList.refetch,

    // Upload
    uploadFile: handleUpload,
    uploading: upload.uploading,
    uploadProgress: upload.progress,
    uploadError: upload.error,

    // Download
    downloadFile: download.downloadFile,
    downloading: download.downloading,
    downloadError: download.error,

    // Delete
    deleteFile: handleDelete,
    deleting: deleteOp.deleting,
    deleteError: deleteOp.error,

    // Share
    shareFile: share.shareFile,
    sharing: share.sharing,
    shareUrl: share.shareUrl,
    shareError: share.error,
  };
}
