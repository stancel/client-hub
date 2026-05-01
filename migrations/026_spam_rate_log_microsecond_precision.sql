-- Migration 026: spam_rate_log.occurred_at → microsecond precision
--
-- The rate-limit table's PK is (key_type, key_value, occurred_at). When
-- occurred_at was DATETIME (1-second precision), multiple submissions from
-- the same IP within a single wall-clock second collided on the PK, and
-- INSERT IGNORE silently dropped all but the first. That made the new
-- IP-key rate-limit (introduced alongside the spam-defense IP plumbing
-- fix) count at most 1 hit per second — defeating the burst-detection it
-- was meant to provide.
--
-- Bumping to DATETIME(6) gives us microsecond resolution, which is more
-- than enough to disambiguate hits from a real burst. Insertions in
-- spam_filter_service._record_rate_log now use NOW(6).
--
-- Existing rows survive this MODIFY: MariaDB widens DATETIME → DATETIME(6)
-- in place by appending six zero microsecond digits to each value.

ALTER TABLE spam_rate_log
  MODIFY COLUMN occurred_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);

-- Migration 026 complete.
