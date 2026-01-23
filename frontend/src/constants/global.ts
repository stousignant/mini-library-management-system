/**
 * Application-wide constants and configuration values.
 *
 * This module centralizes all static values, magic numbers, and configuration
 * to maintain a single source of truth and prevent hardcoded values throughout
 * the codebase.
 */

// API Configuration
export const DEFAULT_API_PROTOCOL = 'http'
export const DEFAULT_API_HOST = 'localhost'
export const DEFAULT_API_PORT = 8000
export const DEFAULT_API_URL = `${DEFAULT_API_PROTOCOL}://${DEFAULT_API_HOST}:${DEFAULT_API_PORT}`

// HTTP Headers
export const CONTENT_TYPE_JSON = 'application/json'

// Polling Intervals (milliseconds)
export const STATS_POLLING_INTERVAL_MS = 10000

// Book Summary Validation
export const BOOK_SUMMARY_MAX_LENGTH = 5000
export const BOOK_SUMMARY_WARNING_THRESHOLD = 4500
