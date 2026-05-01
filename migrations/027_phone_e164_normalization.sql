-- Migration 027: Phone numbers → E.164 (storage standardization)
--
-- Steven flagged the free-for-all phone formatting on prod (raw 10-digit,
-- hyphenated, parenthesized) and pointed out it would break the upcoming
-- SIP/CTI lookup integration — ``GET /api/v1/lookup/phone/{number}`` does
-- literal string equality, so a SIP query of "+18035551212" against a
-- stored "(803) 555-1212" returns no match.
--
-- Decision: VARCHAR(20) stays (a `+` is non-numeric so a numeric type
-- would be hostile to international and to leading zeros), values are
-- normalized to E.164 (`+CCNNNNNNNNNN`), and a CHECK constraint enforces
-- the format at the DB layer so a future direct-DB writer can't pollute
-- the column. The Pydantic schema normalizes at ingestion via
-- ``app.services.phone_utils.normalize_to_e164`` so consumer sites do
-- not need to change anything.
--
-- See docs/handoffs/cdc-v0.3.0.md and docs/handoffs/clever-orchid-v0.3.0.md.

-- ============================================================
-- Step 1 — Backfill existing rows to E.164.
-- ============================================================
-- All current prod data is US, either 10-digit (with or without
-- formatting characters) or already E.164. The CASE handles all three
-- shapes; anything that escapes (already-bad data) is left alone and
-- will surface when the CHECK constraint is added below.

UPDATE contact_phones
SET phone_number = CASE
    -- Already E.164 — leave alone (safe even with re-runs)
    WHEN phone_number REGEXP '^\\+[0-9]{10,15}$' THEN phone_number
    -- 10 digits after stripping non-digits → assume US, prepend +1
    WHEN LENGTH(REGEXP_REPLACE(phone_number, '[^0-9]', '')) = 10 THEN
        CONCAT('+1', REGEXP_REPLACE(phone_number, '[^0-9]', ''))
    -- 11 digits starting with 1 → already country-coded US, prepend +
    WHEN LENGTH(REGEXP_REPLACE(phone_number, '[^0-9]', '')) = 11
         AND LEFT(REGEXP_REPLACE(phone_number, '[^0-9]', ''), 1) = '1' THEN
        CONCAT('+', REGEXP_REPLACE(phone_number, '[^0-9]', ''))
    -- Unhandled (international without +, or genuinely malformed)
    -- — leave as-is so the CHECK below surfaces it
    ELSE phone_number
END
WHERE phone_number IS NOT NULL;

UPDATE org_phones
SET phone_number = CASE
    WHEN phone_number REGEXP '^\\+[0-9]{10,15}$' THEN phone_number
    WHEN LENGTH(REGEXP_REPLACE(phone_number, '[^0-9]', '')) = 10 THEN
        CONCAT('+1', REGEXP_REPLACE(phone_number, '[^0-9]', ''))
    WHEN LENGTH(REGEXP_REPLACE(phone_number, '[^0-9]', '')) = 11
         AND LEFT(REGEXP_REPLACE(phone_number, '[^0-9]', ''), 1) = '1' THEN
        CONCAT('+', REGEXP_REPLACE(phone_number, '[^0-9]', ''))
    ELSE phone_number
END
WHERE phone_number IS NOT NULL;

-- ============================================================
-- Step 2 — Add CHECK constraint at the DB layer.
-- ============================================================
-- Defense in depth. The Pydantic validator catches ingestion via the
-- API; this catches anything that reaches the DB through any other
-- path (direct SQL, future ETL, future MCP write tool).

ALTER TABLE contact_phones
    ADD CONSTRAINT chk_cp_phone_e164
    CHECK (phone_number REGEXP '^\\+[0-9]{10,15}$');

ALTER TABLE org_phones
    ADD CONSTRAINT chk_op_phone_e164
    CHECK (phone_number REGEXP '^\\+[0-9]{10,15}$');

-- Migration 027 complete.
