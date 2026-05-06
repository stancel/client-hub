# Client Hub v0.4.0 — Knowledge Transfer for Clever Orchid Website

**Audience:** the Claude Code session (or developer) working on the
**Clever Orchid Next.js consumer site** at
`/home/brad/Sites/clever-orchid-website`.

**Status:** Client Hub v0.4.0 is being released alongside this
prompt (driven by a 2026-05-06 SEO-pitch breakthrough at the
sister CDC site, see the v0.4.0 entry in `CHANGELOG.rst`). The new
SDK `@bradstancel/clienthub-sdk@0.4.0` will be on the private
registry at `https://npm.onlinesalessystems.com/` after the
tag-triggered publish workflow runs. **The existing v0.3.6
integration keeps working unchanged** — adopting v0.4.0 closes
two real defects on the consumer-site side that aren't covered by
the Client Hub fix alone.

The same investigation that prompted this prompt found no Clever
Orchid breakthrough rows in production — but the underlying defect
(visitor IP not propagating to communications, fake-NANP phones
passing form validation) applies equally to both sites. Same fix.

## TL;DR

1. Bump `@bradstancel/clienthub-sdk` to `^0.4.0` in `package.json`.
2. In `lib/client-hub.ts::logConversion`, add `externalRefsJson:
   externalRefs` to the `commCreate` payload of the
   `createCommunicationApiV1CommunicationsPost` call. Today the
   comm call sends nothing for it.
3. In `lib/client-hub.ts::appendCommunication`, accept `ipAddress`
   and `userAgent` parameters on the input type, build a fresh
   `externalRefsJson`, and pass it through to the comm call. Update
   page-level callers to extract `CF-Connecting-IP` and forward it.
4. In `lib/spam-filter.ts`, add a NANP area-code validator
   (`isValidNanpAreaCode`) and wire it into form-submit
   pre-validation alongside the existing `isValidUSPhone`. Mirror
   the area-code list from
   `api/app/services/phone_utils.py::NANP_AREA_CODES`.
5. Re-run the prebuild hook (`npm run prebuild`) to pull the new
   SEO-outreach patterns from `GET /api/v1/spam-patterns` into
   `lib/generated/spam-patterns.json`.
6. Test, commit, deploy.

## Why these changes

**(2) and (3) — comm `externalRefsJson`.** The 2026-05-06
investigation at CDC found that the spam_event for the
breakthrough comm recorded the consumer droplet IP instead of the
real visitor IP. Root cause: `logConversion` and
`appendCommunication` send `externalRefsJson` only on the contact
create, not the comm. Client Hub v0.4.0 falls back to the parent
contact's stored `external_refs_json.ip_address` when the comm
payload doesn't carry one, so production data after the API deploy
will be correct. But sending it explicitly on the comm is the right
contract long-term — your comm's `spam_events.remote_ip` then
reflects the *exact* visitor IP of that submission (which can
differ from the contact-create IP if the user navigates between
forms).

**(4) — NANP area-code validator.** The Davis Brown phone
`+12356895054` slipped past the existing `isValidUSPhone` check
(10 digits, leading `1` stripped — passes count) and
`phoneCountryIsBlocked` (the `+1` prefix masks it as domestic).
Area code 235 is not assigned in NANP. Adding
`isValidNanpAreaCode` to your filter catches the same family at
the website edge instead of relying on Client Hub.

**(5) — pattern sync.** Migration 031 on the API seeded 5 new
email substrings (`seowebexpert`, `webexpert`, `webexpertsolution`,
`seoanalyst`, `seospecialist`) and 7 new whitespace-tolerant phrase
regexes covering the SEO-outreach body shape. Your `prebuild` hook
pulls these automatically.

## Specifics — changes in `lib/client-hub.ts`

The CDC handoff at
`docs/handoffs/cdc-v0.4.0.md` has the full code snippets for
`logConversion` and `appendCommunication` — Clever Orchid's
`lib/client-hub.ts` should match the same shape after v0.3.6
synthesis (per `docs/Cross-Project-Integration.rst`), so the same
edits apply verbatim. Re-read that handoff for the diff blocks.

## Specifics — changes in `lib/spam-filter.ts`

Same as the CDC handoff — copy the `NANP_AREA_CODES` set from
`api/app/services/phone_utils.py`, add `isValidNanpAreaCode` and
`extractNanpAreaCode` helpers, wire into the form-submit validator
beside the existing `isValidUSPhone`. Verbatim same edit as CDC.

## Verification

After deploy:

1. Try submitting a contact with phone `+12356895054` — should be
   rejected at the website level with the standard phone-format
   error (no Client Hub round-trip).
2. Submit a clean contact + comm and confirm via the admin
   spam_events endpoint that any resulting events carry both
   `remote_ip` (visitor) and `peer_ip` (your droplet) and the
   comm event has a non-NULL `submitted_email` (looked up from
   the parent contact).
3. Check that the v0.4.0 SDK didn't regress any existing flows.

## Cross-reference

- Client Hub `CHANGELOG.rst` v0.4.0 — full defect walkthrough.
- `docs/handoffs/cdc-v0.4.0.md` — companion prompt for CDC; same
  diffs apply because of post-v0.3.6 module convergence.
- `docs/Spam-Defense-Pattern.rst` — updated subsections "Visitor IP
  vs proxy peer" and "Phone validation: digit count vs NANP area
  code".

Adoption is on your schedule. The Client Hub-side fixes are
fix-forward and don't require this consumer-site work to land —
but converging the consumer-site contract closes the remaining
gap.
