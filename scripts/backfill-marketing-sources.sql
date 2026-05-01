-- Backfill: derive marketing_source codes for contacts whose
-- contact_marketing_sources junction is currently empty.
--
-- Mirrors the derivation logic in
-- app/services/marketing_source_service.py::derive_codes() but
-- expressed in pure SQL so it runs from any mariadb client without
-- needing the API container.
--
-- Run once on each instance after the v0.3.0 deploy:
--
--   Cybertron dev (local):
--     mariadb -h 10.0.1.220 -uroot -p clienthub \
--       < scripts/backfill-marketing-sources.sql
--
--   Production VPS (CDC / Clever Orchid / etc.):
--     docker exec -i clienthub-mariadb mariadb -uroot -p"$ROOT_PW" clienthub \
--       < scripts/backfill-marketing-sources.sql
--
-- Idempotent: only contacts with zero junction rows are touched, so
-- re-running is a no-op once everyone has at least one attribution.
-- Rows are tagged ``source_detail='derived-backfill'`` so they can be
-- distinguished from live ``derived`` (in-flight at create time) and
-- ``explicit`` (consumer-site supplied) attributions.

INSERT INTO contact_marketing_sources
    (contact_id, marketing_source_id, source_detail, attributed_at)
SELECT
    c.id,
    ms.id,
    'derived-backfill',
    NOW()
FROM contacts c
LEFT JOIN contact_marketing_sources cms ON cms.contact_id = c.id
JOIN marketing_sources ms ON ms.code = (
    CASE
        -- UTM paid + search source → google_search
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_medium')))
             IN ('cpc','paid','ppc','display','banner')
         AND LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_source')))
             IN ('google','bing','duckduckgo','yahoo')
            THEN 'google_search'
        -- UTM paid + non-search source → social_media_ad
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_medium')))
             IN ('cpc','paid','ppc','display','banner')
            THEN 'social_media_ad'
        -- UTM organic social
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_medium')))
             IN ('social','organic_social','social-organic')
            THEN 'social_media_organic'
        -- UTM email
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_medium')))
             IN ('email','newsletter')
            THEN 'other'
        -- UTM source-only (organic search)
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_source')))
             IN ('google','bing','duckduckgo','yahoo')
            THEN 'google_search'
        -- UTM source-only (organic social)
        WHEN LOWER(JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.extra.utm_source')))
             IN ('facebook','instagram','twitter','x','linkedin','tiktok','pinterest','reddit')
            THEN 'social_media_organic'
        -- Referrer hostname → search engine
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.referrer'))
             REGEXP 'https?://[^/]*(google\\.|bing\\.|duckduckgo\\.|yahoo\\.)'
            THEN 'google_search'
        -- Referrer hostname → social
        WHEN JSON_UNQUOTE(JSON_EXTRACT(c.external_refs_json, '$.referrer'))
             REGEXP 'https?://[^/]*(facebook\\.|instagram\\.|twitter\\.|x\\.com|linkedin\\.|tiktok\\.|pinterest\\.|reddit\\.)'
            THEN 'social_media_organic'
        -- Default: website
        ELSE 'website'
    END
)
WHERE cms.id IS NULL;

-- Sanity check (run after to verify):
-- SELECT ms.code, COUNT(*) AS n
--   FROM contact_marketing_sources cms
--   JOIN marketing_sources ms ON ms.id = cms.marketing_source_id
--  WHERE cms.source_detail = 'derived-backfill'
--  GROUP BY ms.code
--  ORDER BY n DESC;
