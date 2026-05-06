-- Migration 031: seed SEO-outreach spam patterns
--
-- Driven by the v0.3.6 CDC breakthrough investigation (2026-05-06).
-- A SEO-pitch from "Davis Brown" (davisseowebexpert@gmail.com,
-- phone +12356895054 / India IP 106.219.155.100, body opening
-- "Re: Drop Traffic / Hello Good Morning, I have found some major
-- errors that correspond to a drop in website  traffic ...") slipped
-- through three existing defenses:
--
-- 1. The seeded ``seoexpert`` email_substring did not match
--    ``davisseowebexpert`` because of the ``web`` infix between
--    ``seo`` and ``expert``. New ``seowebexpert`` + ``webexpert``
--    substrings catch this category.
-- 2. The seeded phrase ``\bdrop in (website |)traffic\b`` uses a
--    literal space, which the body broke by inserting a double
--    space ("drop in website  traffic"). New patterns use ``\s+``
--    so any whitespace amount matches.
-- 3. ``Hello Good Morning,`` was the only existing phrase to graze
--    (single match → soft_signal, below the 2-match rejection
--    threshold). With these additions the same body now hits
--    ≥3 phrases → phrase_combo rejection.
--
-- Phone validation for the invalid NANP area code 235 is NOT a
-- pattern row — it is implemented as code in
-- app/services/phone_utils.py::is_valid_nanp_area_code and a new
-- evaluate_intake step that produces a 'phone_invalid_areacode'
-- spam_events row. See docs/Spam-Defense-Pattern.rst.

-- Email substring patterns (case-insensitive substring of full email)
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'email_substring', 'seowebexpert',     'davisseowebexpert@gmail.com style — SEO/traffic-drop outreach', 'migration_031'),
  (UUID(), 'email_substring', 'webexpert',        'broader catch — SEO vendor naming', 'migration_031'),
  (UUID(), 'email_substring', 'webexpertsolution','observed across SEO outreach mills', 'migration_031'),
  (UUID(), 'email_substring', 'seoanalyst',       'cold SEO-outreach naming pattern', 'migration_031'),
  (UUID(), 'email_substring', 'seospecialist',    'cold SEO-outreach naming pattern', 'migration_031');

-- Phrase regex patterns (case-insensitive; ≥2 matches in body for rejection).
-- Use \s+ for any whitespace run so a double-space cannot defeat the pattern.
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'phrase_regex', '\\bdrop\\s+in\\s+website\\s+traffic\\b',           'whitespace-tolerant variant of migration 023 phrase (defeated by double-space)', 'migration_031'),
  (UUID(), 'phrase_regex', '\\berrors\\s+and\\s+(the\\s+)?solutions\\b',       'SEO-mill body — "errors and the solutions to help you ..."', 'migration_031'),
  (UUID(), 'phrase_regex', '\\bimprove\\s+the\\s+performance\\s+and\\s+traffic\\b', 'SEO-mill body close', 'migration_031'),
  (UUID(), 'phrase_regex', '\\bdrop\\s+traffic\\b',                            'subject-line variant ("Re: Drop Traffic")', 'migration_031'),
  (UUID(), 'phrase_regex', '\\bmajor\\s+errors\\b',                            'SEO-mill body lead-in', 'migration_031'),
  (UUID(), 'phrase_regex', '\\bperformance\\s+and\\s+traffic\\s+of\\s+your\\s+website\\b', 'SEO-mill body close — high specificity', 'migration_031'),
  (UUID(), 'phrase_regex', '\\bcorrespond\\s+to\\s+a\\s+drop\\s+in\\b',        'SEO-mill body lead-in phrasing', 'migration_031');
