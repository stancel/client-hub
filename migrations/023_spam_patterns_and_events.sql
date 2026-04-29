-- Migration 023: Spam-defense framework — patterns, events log, rate-limit log
--
-- Defense-in-depth spam filtering at the API ingestion layer. Every
-- public-ish entry point (web forms, webhooks, future integrations)
-- inherits the same filter via app/services/spam_filter_service.py
-- and rejects spam payloads with HTTP 422 before any DB write to
-- contacts / communications / etc.
--
-- Three tables:
--   spam_patterns   — operator-managed pattern library
--   spam_events     — every rejection logged for analytics + ETL
--   spam_rate_log   — sliding-window rate-limit state
--
-- See docs/Spam-Defense-Pattern.rst for the full design.

-- ============================================================
-- Pattern library
-- ============================================================
CREATE TABLE IF NOT EXISTS spam_patterns (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    pattern_kind ENUM(
        'email_substring',
        'full_email_block',
        'url_regex',
        'phrase_regex',
        'phone_country_block'
    ) NOT NULL,
    pattern VARCHAR(500) NOT NULL,
    notes VARCHAR(500) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    hit_count INT UNSIGNED NOT NULL DEFAULT 0,
    last_hit_at DATETIME NULL,
    false_positive_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) NULL,
    UNIQUE KEY ux_sp_uuid (uuid),
    KEY idx_sp_active_kind (is_active, pattern_kind)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Rejection log
-- ============================================================
CREATE TABLE IF NOT EXISTS spam_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    uuid CHAR(36) NOT NULL,
    source_id BIGINT UNSIGNED NULL,
    endpoint VARCHAR(100) NOT NULL,
    integration_kind ENUM(
        'web_form',
        'webhook',
        'mcp',
        'direct_api',
        'other'
    ) NOT NULL DEFAULT 'other',
    remote_ip VARCHAR(45) NULL,
    submitted_email VARCHAR(255) NULL,
    submitted_phone VARCHAR(20) NULL,
    submitted_body_hash CHAR(16) NULL,
    matched_pattern_id BIGINT UNSIGNED NULL,
    matched_pattern_text VARCHAR(500) NULL,
    rejection_reason VARCHAR(64) NOT NULL,
    payload_json JSON NULL,
    was_false_positive BOOLEAN NOT NULL DEFAULT FALSE,
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY ux_se_uuid (uuid),
    KEY idx_se_occurred (occurred_at),
    KEY idx_se_source (source_id, occurred_at),
    KEY idx_se_endpoint (endpoint, occurred_at),
    KEY idx_se_email (submitted_email),
    KEY idx_se_pattern (matched_pattern_id),
    CONSTRAINT fk_se_source FOREIGN KEY (source_id)
        REFERENCES sources(id) ON DELETE SET NULL,
    CONSTRAINT fk_se_pattern FOREIGN KEY (matched_pattern_id)
        REFERENCES spam_patterns(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Rate-limit log (sliding window, 10-min for "rate limited")
-- ============================================================
CREATE TABLE IF NOT EXISTS spam_rate_log (
    key_type ENUM('ip', 'email', 'email_body_hash') NOT NULL,
    key_value VARCHAR(255) NOT NULL,
    occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (key_type, key_value, occurred_at),
    KEY idx_srl_prune (occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- Seed default patterns from the consumer-site filter lists
-- (Complete Dental Care + Clever Orchid websites, 2026-04-28).
-- INSERT IGNORE on uuid means re-running this migration is a no-op.
-- ============================================================

-- Email substring patterns (case-insensitive substring match)
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'email_substring', 'webdigital',     'ezrawebdigital@gmail.com — SEO/AI-ranking outreach mill (Cameroon, +235 phone)', 'migration_023'),
  (UUID(), 'email_substring', 'websolution',    'mattwebsolution@gmail.com — same operator as ezrawebdigital (shared phone 2356895054)', 'migration_023'),
  (UUID(), 'email_substring', 'coachvas',       'businesscoachvas.com — Virtual Assistant Services pitches', 'migration_023'),
  (UUID(), 'email_substring', 'sendproud',      'sendproud.com — Calendly lead-gen pitch with 100M-contacts claim', 'migration_023'),
  (UUID(), 'email_substring', 'seoexpert',      'generic SEO-vendor marker', 'migration_023'),
  (UUID(), 'email_substring', 'leadgen',        'generic lead-gen vendor marker', 'migration_023'),
  (UUID(), 'email_substring', 'leadsby',        'lead-vendor naming pattern', 'migration_023'),
  (UUID(), 'email_substring', 'outreach',       'cold-outreach vendor marker', 'migration_023'),
  (UUID(), 'email_substring', 'growthhack',     'growth-hacking vendor marker', 'migration_023'),
  (UUID(), 'email_substring', 'growthmar',      'growthmarketer / growthmark — variants', 'migration_023'),
  (UUID(), 'email_substring', 'virtualassist',  'virtual assistant vendor marker', 'migration_023'),
  (UUID(), 'email_substring', 'marketingagency','marketingagency vendor pattern', 'migration_023'),
  (UUID(), 'email_substring', 'digitalagency',  'digitalagency vendor pattern', 'migration_023');

-- URL regex patterns (case-insensitive Python regex against body)
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'url_regex', 'calendly\\.com',                  'no booking links in inbound forms', 'migration_023'),
  (UUID(), 'url_regex', 'cal\\.com\\/',                    'no booking links', 'migration_023'),
  (UUID(), 'url_regex', 'meetings\\.hubspot\\.com',        'no booking links', 'migration_023'),
  (UUID(), 'url_regex', 'tidycal\\.com',                   'no booking links', 'migration_023'),
  (UUID(), 'url_regex', 'savvycal\\.com',                  'no booking links', 'migration_023'),
  (UUID(), 'url_regex', 'outlook\\.office\\.com\\/bookwithme', 'no booking links', 'migration_023'),
  (UUID(), 'url_regex', 'book\\.zoom\\.us',                'no booking links', 'migration_023');

-- Phrase regex patterns (case-insensitive; need ≥2 matches in body for rejection)
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'phrase_regex', '\\bI help businesses\\b',                                  'B2B vendor pitch language', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bI''d love to show you\\b',                              'B2B pitch close', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bI work with [A-Za-z]+ businesses\\b',                   'B2B vendor pitch lead', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bschedule a (quick |short |brief |)(call|meeting|chat)\\b', 'B2B pitch close', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bbook a (quick |short |brief |)(call|meeting|chat|time)\\b', 'B2B pitch close', 'migration_023'),
  (UUID(), 'phrase_regex', '\\b(15|30) minute (call|chat|conversation)\\b',            'B2B vendor pitch duration phrasing', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bMissing from AI Results\\b',                            'literal SEO-mill subject phrase', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bdrop in (website |)traffic\\b',                         'SEO-mill traffic-drop pitch phrase', 'migration_023'),
  (UUID(), 'phrase_regex', '\\b100 million contacts\\b',                               'sendproud / outreach pitch claim', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bvirtual assistant services\\b',                         'VA-vendor pitch', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bquick analysis\\b',                                     'SEO-mill pitch close', 'migration_023'),
  (UUID(), 'phrase_regex', '\\bThanks & Best Regards\\b',                              'SEO-mill outreach signoff (oddly specific, high signal)', 'migration_023'),
  (UUID(), 'phrase_regex', 'Hello Good Morning,',                                      'literal capitalization+comma — SEO-mill outreach opener', 'migration_023');

-- Phone country-code blocks (raw substring against the submitted phone)
-- Note: '+' alone would block any internationally-formatted number,
-- including +1 (US). We add '+' as the broad rule but rely on the
-- separate phone_invalid digit-count check for nuance: +1 12-digit
-- numbers normalize to 10/11 and pass; +44, +91, +235 etc. don't.
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'phone_country_block', '+235', 'Cameroon — confirmed SEO-mill origin', 'migration_023'),
  (UUID(), 'phone_country_block', '+234', 'Nigeria — common scam-call origin', 'migration_023'),
  (UUID(), 'phone_country_block', '+91',  'India — common offshore-vendor origin', 'migration_023'),
  (UUID(), 'phone_country_block', '+92',  'Pakistan — common offshore-vendor origin', 'migration_023'),
  (UUID(), 'phone_country_block', '+880', 'Bangladesh — common offshore-vendor origin', 'migration_023'),
  (UUID(), 'phone_country_block', '+62',  'Indonesia — common offshore-vendor origin', 'migration_023');
