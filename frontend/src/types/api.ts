/**
 * Standard wrappers for API Requests and Responses
 */

/**
 * Standard generic response from the API.
 */
export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
  errors?: Record<string, string[]>;
}

/**
 * Standard paginated response.
 */
export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
