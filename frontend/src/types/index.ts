/**
 * Shared TypeScript type definitions
 */

// Re-export types from services
export type { FileMetadata } from '../services/fileService';
export type { UserInfo } from '../utils/auth';
export type { ApiError } from '../services/api';

// Additional shared types can be added here
export interface LoadingState {
  loading: boolean;
  error: string | null;
}

export interface ProgressState extends LoadingState {
  progress: number;
}
