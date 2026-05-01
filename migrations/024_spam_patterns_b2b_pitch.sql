-- Migration 024: Spam-defense pattern expansion — B2B cold-pitch coverage
--
-- Triggered by a real miss on Complete Dental Care (2026-04-30): a Hoff &
-- Mazor mobile-app cold pitch produced ZERO matches against the seeded
-- 13 phrase_regex patterns. The pitch said "We help businesses" (not "I"),
-- "10-minute chat" (not 15/30), "Best regards" (not "Thanks & Best Regards"),
-- "Open to a quick chat" (not "schedule a"). It also used a domain
-- (hoffandmazoor.com) that wasn't in our email_substring list.
--
-- All patterns below were hand-checked against the captured body for
-- communications.id=31 on the CDC instance. With phrase_combo threshold ≥ 2,
-- this set produces ≥ 3 matches on that exact body, and is broad enough to
-- catch the next variant of the same pitch.
--
-- See docs/Spam-Defense-Pattern.rst for the inheritance pattern.

-- ============================================================
-- Phrase regex (need ≥ PHRASE_MATCHES_REQUIRED_FOR_REJECTION matches)
-- ============================================================
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'phrase_regex', '\\bWe help (businesses|companies|brands|teams)\\b', 'Hoff & Mazor pitch + variants', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(launch fast|launch your (app|website|product))\\b', 'app/web dev cold-pitch tell', 'migration_024'),
  (UUID(), 'phrase_regex', '\\bsimple and stress[- ]free\\b', 'Hoff & Mazor — direct hit', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(10|15|20|30|45|60)[- ]minute (call|chat|conversation|meeting|demo)\\b', 'broader than the original 15/30-only pattern', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(open to|up for) a (quick |short |brief )?(call|chat|meeting|demo)\\b', 'common B2B opener', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b[Rr]espond with (stop|unsubscribe) to (opt[- ]?out|stop)\\b', 'unsolicited-mail compliance footer', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(actually deliver|deliver) results\\b', 'agency pitch boilerplate', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(scalable|user[- ]friendly) (apps?|websites?|solutions?|platforms?)\\b', 'app-dev shop pitch language', 'migration_024'),
  (UUID(), 'phrase_regex', '\\bfrom concept to launch\\b', 'agency-pitch boilerplate', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(building|improving) (a |the |your )?mobile app\\b', 'mobile-app cold-pitch tell', 'migration_024'),
  (UUID(), 'phrase_regex', "\\bgot (an idea|a goal)\\b", 'B2B opener', 'migration_024'),
  (UUID(), 'phrase_regex', '\\b(let'"'"'s|lets) (talk|chat|connect|hop on)\\b', 'common closer', 'migration_024');

-- ============================================================
-- Email substring (case-insensitive substring of full email)
-- ============================================================
INSERT IGNORE INTO spam_patterns (uuid, pattern_kind, pattern, notes, created_by) VALUES
  (UUID(), 'email_substring', 'hoffandmazor', 'Hoff & Mazor (and the .co/.com variants — typo + correct)', 'migration_024'),
  (UUID(), 'email_substring', 'appdevelopment', 'app-dev cold-pitch domain root', 'migration_024'),
  (UUID(), 'email_substring', 'mobileapp',      'mobile-app cold-pitch domain root', 'migration_024'),
  (UUID(), 'email_substring', 'webagency',      'agency cold-pitch domain root', 'migration_024'),
  (UUID(), 'email_substring', 'softwarehouse',  'agency cold-pitch domain root', 'migration_024'),
  (UUID(), 'email_substring', 'devstudio',      'agency cold-pitch domain root', 'migration_024');

-- Migration 024 complete.
