-- Migration 030: spam_events.peer_ip + tighter remote_ip semantics
--
-- Background: the v0.3.6 audit (2026-05-06) found a SEO-pitch
-- breakthrough on CDC where spam_events.remote_ip recorded the
-- consumer-site droplet IP (134.199.195.114) instead of the real
-- visitor IP (106.219.155.100, India). The visitor IP was only
-- present inside contacts.external_refs_json — hard to query, hard
-- to filter, useless for forensics.
--
-- Fix: split the two notions into separate columns.
--
--   remote_ip  — best-known canonical *visitor* IP. Public-only,
--                derived via app.services.request_meta.extract_request_meta
--                (precedence: payload external_refs.ip_address →
--                request.client.host). This is the field analytics
--                and rate-limit keying should treat as authoritative.
--   peer_ip    — raw TCP peer (request.client.host, even if private/
--                loopback). Forensic only — proves what hit our
--                edge regardless of how the consumer site labelled it.
--
-- Cutover semantics (post-migration): every new spam_events row
-- written by app/services/spam_filter_service.py populates both
-- columns. Historical rows have peer_ip = NULL because we cannot
-- reliably tell whether the old remote_ip was the canonical or the
-- peer.

ALTER TABLE spam_events
  ADD COLUMN peer_ip VARCHAR(45) NULL AFTER remote_ip,
  ADD INDEX idx_se_remote_ip (remote_ip),
  ADD INDEX idx_se_peer_ip (peer_ip);
