-- Migration 018: Schema migrations tracking table
-- Used by bootstrap-migrations.sh to track which migrations have been applied.
-- This migration is special-cased by the runner (it creates the tracking table itself).

CREATE TABLE IF NOT EXISTS _schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
