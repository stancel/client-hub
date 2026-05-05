# @bradstancel/clienthub-sdk

TypeScript SDK for the [Client Hub](https://github.com/stancel/client-hub)
data-first customer intelligence API.

> Auto-generated from the OpenAPI spec on every Client Hub release.
> **Do not edit by hand** — changes are clobbered on the next
> `./scripts/generate-sdks.sh` run.

## Install

The package is published to a private registry
(`https://npm.onlinesalessystems.com/`) under the `@bradstancel`
scope. Configure your project's `.npmrc` once:

```
@bradstancel:registry=https://npm.onlinesalessystems.com/
//npm.onlinesalessystems.com/:_authToken=${NPM_TOKEN}
```

Set `NPM_TOKEN` in your environment (the read-only `consumer` token
is sufficient for installs). Then:

```bash
npm install @bradstancel/clienthub-sdk
```

## Versioning

The SDK version always matches the Client Hub API version it was
generated against. `^0.3.5` will pull the latest `0.3.x` patch
release. Every Client Hub release tags `vX.Y.Z` in git and publishes
that exact version here via GitHub Actions.

## Quick start

```typescript
import { Configuration, ContactsApi } from '@bradstancel/clienthub-sdk';

const config = new Configuration({
  basePath: 'https://your-clienthub-instance.example.com',
  headers: { 'X-API-Key': process.env.CLIENT_HUB_API_KEY! },
});

const contacts = new ContactsApi(config);
const result = await contacts.listContacts();
```

See your Client Hub instance's `/docs` URL for the full endpoint
surface (Swagger UI auto-generated from the same spec this SDK was
built from).

## Source

- Project: <https://github.com/stancel/client-hub>
- Generator: `openapitools/openapi-generator-cli` (`typescript-fetch`)
- Spec source: `sdks/openapi.json` in the Client Hub repo
