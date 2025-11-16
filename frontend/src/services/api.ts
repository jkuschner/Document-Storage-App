import { fetchAuthSession } from '@aws-amplify/auth';

const API_URL = process.env.REACT_APP_API_URL || '';

if (!API_URL || API_URL.includes('your-api-gateway-id')) {
  console.warn(
    '⚠️  API_URL not configured. Please set REACT_APP_API_URL in your .env file.\n' +
    'Get the URL from CloudFormation outputs:\n' +
    'aws cloudformation describe-stacks --stack-name file-storage-dev-backend --query "Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue" --output text --region us-west-2'
  );
}

export interface ApiError {
  message: string;
  status?: number;
  code?: string;
}

export class ApiClientError extends Error {
  status?: number;
  code?: string;

  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
  }
}

/**
 * Gets the current authentication token from Amplify
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    return token || null;
  } catch (error) {
    console.error('Failed to get auth token:', error);
    return null;
  }
}

/**
 * Base API client with authentication
 */
async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get auth token
  const token = await getAuthToken();

  // Build headers
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Merge with options headers if provided
  if (options.headers) {
    const optHeaders = new Headers(options.headers);
    optHeaders.forEach((value, key) => {
      headers[key] = value;
    });
  }

  // Build full URL
  const url = `${API_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle non-2xx responses
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorBody: any = null;

      try {
        errorBody = await response.json();
        errorMessage = errorBody.error || errorBody.message || errorMessage;
      } catch {
        // Response body is not JSON
      }

      throw new ApiClientError(errorMessage, response.status, errorBody?.code);
    }

    // Parse JSON response
    const data = await response.json();
    return data as T;
  } catch (error) {
    // Re-throw ApiClientError
    if (error instanceof ApiClientError) {
      throw error;
    }

    // Wrap other errors
    if (error instanceof Error) {
      throw new ApiClientError(
        error.message || 'Network error occurred',
        undefined,
        'NETWORK_ERROR'
      );
    }

    throw new ApiClientError('Unknown error occurred');
  }
}

/**
 * HTTP Methods
 */
export const api = {
  get: <T>(endpoint: string, options?: RequestInit): Promise<T> => {
    return apiClient<T>(endpoint, { ...options, method: 'GET' });
  },

  post: <T>(
    endpoint: string,
    body?: any,
    options?: RequestInit
  ): Promise<T> => {
    return apiClient<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put: <T>(endpoint: string, body?: any, options?: RequestInit): Promise<T> => {
    return apiClient<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete: <T>(endpoint: string, options?: RequestInit): Promise<T> => {
    return apiClient<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

/**
 * Upload file to S3 using presigned URL (no auth headers needed for S3)
 */
export async function uploadToS3(
  presignedUrl: string,
  file: File,
  contentType: string,
  onProgress?: (progress: number) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          onProgress(progress);
        }
      });
    }

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else {
        reject(
          new ApiClientError(
            `S3 upload failed: ${xhr.statusText}`,
            xhr.status
          )
        );
      }
    });

    xhr.addEventListener('error', () => {
      reject(new ApiClientError('S3 upload failed: Network error'));
    });

    xhr.addEventListener('abort', () => {
      reject(new ApiClientError('S3 upload aborted'));
    });

    xhr.open('PUT', presignedUrl);
    xhr.setRequestHeader('Content-Type', contentType);
    xhr.send(file);
  });
}

export default api;
