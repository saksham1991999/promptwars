/**
 * Error handling utilities
 */

/**
 * Format error for display to user
 */
export function formatError(err: unknown): string {
  if (err instanceof Error) {
    return err.message;
  }
  if (typeof err === 'string') {
    return err;
  }
  return 'An unexpected error occurred';
}

/**
 * Check if error is a network error
 */
export function isNetworkError(err: unknown): boolean {
  if (err instanceof Error) {
    return (
      err.message.includes('network') ||
      err.message.includes('fetch') ||
      err.message.includes('timeout')
    );
  }
  return false;
}
