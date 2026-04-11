-- Migration 017: Cross-source attribution view

CREATE OR REPLACE VIEW v_events_by_source AS
SELECT
    c.id               AS communication_id,
    c.uuid             AS communication_uuid,
    s.code             AS source_code,
    s.name             AS source_name,
    s.source_type      AS source_type,
    s.domain           AS source_domain,
    ct.code            AS channel_code,
    ct.label           AS channel_label,
    c.direction,
    c.occurred_at,
    c.subject,
    c.body,
    c.external_message_id,
    c.contact_id,
    co.uuid            AS contact_uuid,
    co.first_name,
    co.last_name,
    co.external_refs_json,
    c.created_at,
    c.created_by
FROM communications c
JOIN sources s        ON s.id = c.source_id
JOIN channel_types ct ON ct.id = c.channel_type_id
LEFT JOIN contacts co ON co.id = c.contact_id;
