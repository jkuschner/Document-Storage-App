import api, { uploadToS3 } from './api';
import { getCurrentUserId } from '../utils/auth';

// Type definitions matching backend DynamoDB schema
export interface FileMetadata {
  userId: string;
  fileId: string;
  fileName: string;
  s3Key: string;
  contentType: string;
  uploadDate: string;
  status: 'pending' | 'completed' | 'failed';
  size?: number;
  folder?: string;
}

export interface UploadFileResponse {
  uploadUrl: string;
  fileId: string;
  message: string;
}

export interface ListFilesResponse {
  files: FileMetadata[];
  count: number;
}

export interface DownloadFileResponse {
  downloadUrl: string;
  fileName: string;
  fileId: string;
}

export interface ShareFileResponse {
  shareUrl: string;
  shareToken: string;
  expiresAt: string;
  message: string;
}

export interface DeleteFileResponse {
  message: string;
  fileId: string;
}

/**
 * File Service - Handles all file-related API operations
 */
export class FileService {
  /**
   * Upload a file
   * 1. Request presigned URL from backend
   * 2. Upload file directly to S3
   * 3. Backend automatically updates DynamoDB status
   */
  static async uploadFile(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<string> {
    const userId = await getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    // Step 1: Get presigned URL from backend
    const response = await api.post<UploadFileResponse>('/files', {
      fileName: file.name,
      userId,
      contentType: file.type || 'application/octet-stream',
      size: file.size,
    });

    // Step 2: Upload file to S3 using presigned URL
    await uploadToS3(response.uploadUrl, file, file.type, onProgress);

    // Return the fileId for tracking
    return response.fileId;
  }

  /**
   * List all files for the current user
   */
  static async listFiles(userId?: string): Promise<FileMetadata[]> {
    const currentUserId = userId || (await getCurrentUserId());
    if (!currentUserId) {
      throw new Error('User not authenticated');
    }

    const response = await api.get<ListFilesResponse>(
      `/files?userId=${currentUserId}`
    );

    return response.files;
  }

  /**
   * Download a file
   * Returns a presigned URL that can be used to download the file
   */
  static async downloadFile(fileId: string): Promise<string> {
    const userId = await getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await api.get<DownloadFileResponse>(
      `/files/${fileId}?userId=${userId}`
    );

    return response.downloadUrl;
  }

  /**
   * Delete a file
   * Removes both S3 object and DynamoDB metadata
   */
  static async deleteFile(fileId: string): Promise<void> {
    const userId = await getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    await api.delete<DeleteFileResponse>(`/files/${fileId}?userId=${userId}`);
  }

  /**
   * Share a file
   * Creates a shareable link with optional expiration
   */
  static async shareFile(
    fileId: string,
    expirationHours: number = 24
  ): Promise<ShareFileResponse> {
    const userId = await getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await api.post<ShareFileResponse>(
      `/files/${fileId}/share?userId=${userId}`,
      { expirationHours }
    );

    return response;
  }

  /**
   * Helper: Trigger browser download from presigned URL
   */
  static triggerDownload(url: string, fileName: string): void {
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Helper: Format file size to human-readable format
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  /**
   * Helper: Format date to relative time (e.g., "2 days ago")
   */
  static formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24)
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString();
  }

  /**
   * Helper: Get file type icon/category
   */
  static getFileType(fileName: string, mimeType?: string): string {
    if (mimeType) {
      if (mimeType.startsWith('image/')) return 'Image';
      if (mimeType.startsWith('video/')) return 'Video';
      if (mimeType.startsWith('audio/')) return 'Audio';
      if (mimeType === 'application/pdf') return 'PDF';
      if (
        mimeType.includes('word') ||
        mimeType.includes('document')
      )
        return 'Document';
      if (
        mimeType.includes('sheet') ||
        mimeType.includes('excel')
      )
        return 'Spreadsheet';
      if (mimeType.includes('text/')) return 'Text';
    }

    // Fallback to extension
    const ext = fileName.split('.').pop()?.toLowerCase();
    if (!ext) return 'File';

    const extensionMap: Record<string, string> = {
      pdf: 'PDF',
      doc: 'Document',
      docx: 'Document',
      txt: 'Text',
      jpg: 'Image',
      jpeg: 'Image',
      png: 'Image',
      gif: 'Image',
      svg: 'Image',
      mp4: 'Video',
      avi: 'Video',
      mov: 'Video',
      mp3: 'Audio',
      wav: 'Audio',
      xls: 'Spreadsheet',
      xlsx: 'Spreadsheet',
      csv: 'Spreadsheet',
      zip: 'Archive',
      rar: 'Archive',
      json: 'Data',
      xml: 'Data',
    };

    return extensionMap[ext] || 'File';
  }
}

export default FileService;
