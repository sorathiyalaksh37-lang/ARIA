/**
 * Centralized Error Handling Utility
 * Handles all types of errors with appropriate user feedback
 */
import { toast } from 'react-toastify';
import { AxiosError } from 'axios';

// ============================================================================
// ERROR TYPES
// ============================================================================

export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  NOT_FOUND = 'NOT_FOUND',
  SERVER = 'SERVER',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN',
}

export interface APIError {
  type: ErrorType;
  message: string;
  code?: string;
  field?: string;
  details?: any;
}

// ============================================================================
// ERROR HANDLER CLASS
// ============================================================================

class ErrorHandler {
  /**
   * Handle any type of error
   */
  handle(error: any, customMessage?: string): APIError {
    // Axios errors
    if (error.isAxiosError) {
      return this.handleAxiosError(error, customMessage);
    }

    // Custom API errors
    if (error.type && Object.values(ErrorType).includes(error.type)) {
      this.showToast(error.message);
      return error;
    }

    // Generic errors
    return this.handleGenericError(error, customMessage);
  }

  /**
   * Handle Axios errors
   */
  private handleAxiosError(error: AxiosError, customMessage?: string): APIError {
    if (!error.response) {
      // Network error
      return this.createError(
        ErrorType.NETWORK,
        customMessage || 'Unable to connect to server. Please check your internet connection.'
      );
    }

    const status = error.response.status;
    const data: any = error.response.data;

    switch (status) {
      case 400:
        return this.createError(
          ErrorType.VALIDATION,
          customMessage || data.message || 'Invalid request'
        );

      case 401:
        return this.createError(
          ErrorType.AUTHENTICATION,
          customMessage || 'Please login to continue',
          '401'
        );

      case 403:
        return this.createError(
          ErrorType.AUTHORIZATION,
          customMessage || 'You do not have permission to perform this action',
          '403'
        );

      case 404:
        return this.createError(
          ErrorType.NOT_FOUND,
          customMessage || 'The requested resource was not found',
          '404'
        );

      case 422:
        // Validation errors
        if (data.errors && Array.isArray(data.errors)) {
          const firstError = data.errors[0];
          return this.createError(
            ErrorType.VALIDATION,
            customMessage || firstError.message,
            '422',
            firstError.field
          );
        }
        return this.createError(
          ErrorType.VALIDATION,
          customMessage || data.message || 'Validation failed'
        );

      case 429:
        return this.createError(
          ErrorType.SERVER,
          customMessage || 'Too many requests. Please wait a moment.'
        );

      case 500:
        return this.createError(
          ErrorType.SERVER,
          customMessage || 'Server error. Our team has been notified.',
          '500'
        );

      case 503:
        return this.createError(
          ErrorType.SERVER,
          customMessage || 'Service temporarily unavailable. Please try again later.',
          '503'
        );

      default:
        return this.createError(
          ErrorType.UNKNOWN,
          customMessage || data.message || 'An unexpected error occurred'
        );
    }
  }

  /**
   * Handle generic JavaScript errors
   */
  private handleGenericError(error: any, customMessage?: string): APIError {
    const message = customMessage || error.message || 'An unexpected error occurred';
    
    return this.createError(ErrorType.UNKNOWN, message);
  }

  /**
   * Create standardized error object
   */
  private createError(
    type: ErrorType,
    message: string,
    code?: string,
    field?: string
  ): APIError {
    const error: APIError = { type, message, code, field };
    
    // Show toast notification
    this.showToast(message, type);
    
    // Log error in development
    if (process.env.REACT_APP_DEBUG === 'true') {
      console.error('[ErrorHandler]', error);
    }
    
    return error;
  }

  /**
   * Show toast notification based on error type
   */
  private showToast(message: string, type: ErrorType = ErrorType.UNKNOWN): void {
    switch (type) {
      case ErrorType.NETWORK:
        toast.error(message, { icon: '📡' });
        break;
      case ErrorType.AUTHENTICATION:
        toast.warning(message, { icon: '🔐' });
        break;
      case ErrorType.AUTHORIZATION:
        toast.warning(message, { icon: '⛔' });
        break;
      case ErrorType.VALIDATION:
        toast.warning(message, { icon: '⚠️' });
        break;
      case ErrorType.NOT_FOUND:
        toast.info(message, { icon: '🔍' });
        break;
      case ErrorType.SERVER:
        toast.error(message, { icon: '🔥' });
        break;
      default:
        toast.error(message);
    }
  }

  /**
   * Handle validation errors (multiple fields)
   */
  handleValidationErrors(errors: Array<{ field: string; message: string }>): void {
    errors.forEach((error) => {
      toast.warning(`${error.field}: ${error.message}`, { autoClose: 5000 });
    });
  }

  /**
   * Log error to monitoring service (e.g., Sentry)
   */
  logError(error: any, context?: any): void {
    if (process.env.NODE_ENV === 'production') {
      // TODO: Integrate with error monitoring service
      // Sentry.captureException(error, { extra: context });
      console.error('[Error Logged]', error, context);
    }
  }

  /**
   * Check if error is retriable
   */
  isRetriable(error: APIError): boolean {
    return [
      ErrorType.NETWORK,
      ErrorType.TIMEOUT,
      ErrorType.SERVER,
    ].includes(error.type);
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(error: APIError): string {
    const retryMessage = this.isRetriable(error)
      ? ' Please try again.'
      : ' Please contact support if the problem persists.';
    
    return error.message + retryMessage;
  }
}

// ============================================================================
// EXPORT SINGLETON
// ============================================================================

export const errorHandler = new ErrorHandler();
export default errorHandler;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Safe async function wrapper with error handling
 */
export async function safeAsync<T>(
  fn: () => Promise<T>,
  errorMessage?: string
): Promise<[T | null, APIError | null]> {
  try {
    const result = await fn();
    return [result, null];
  } catch (error) {
    const apiError = errorHandler.handle(error, errorMessage);
    return [null, apiError];
  }
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      const apiError = errorHandler.handle(error);
      
      if (!errorHandler.isRetriable(apiError) || i === maxRetries - 1) {
        throw error;
      }
      
      // Exponential backoff
      const delay = initialDelay * Math.pow(2, i);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}
