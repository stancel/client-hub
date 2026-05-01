-- Migration 025: Spam-log forensics columns + per-source rate-limit scoping
--
-- Two additions:
--
-- 1) spam_rate_log gets ``source_id`` and ``user_agent`` so the rate-limit
--    can be scoped per-source in future (CDC's traffic shouldn't be rate-
--    limited against Clever Orchid's traffic) and so post-mortem analysis
--    has the UA string a spammer used. Indexed by (source_id, occurred_at).
--
-- 2) spam_events gets ``user_agent`` for the same forensic reason.
--
-- All new columns are nullable — existing rows are unaffected.

ALTER TABLE spam_rate_log
  ADD COLUMN source_id BIGINT UNSIGNED NULL AFTER key_value,
  ADD COLUMN user_agent VARCHAR(255) NULL AFTER source_id,
  ADD KEY idx_srl_source (source_id, occurred_at);

ALTER TABLE spam_events
  ADD COLUMN user_agent VARCHAR(255) NULL AFTER remote_ip;

-- Migration 025 complete.
