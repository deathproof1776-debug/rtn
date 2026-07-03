# Environment & Data Separation — INVARIANTS (do not break)

This app runs in TWO isolated environments with SEPARATE databases. These rules
keep test (preview) data and production data fully separated across all future
deployments and code updates.

## The two environments
| | PREVIEW (dev/test) | PRODUCTION (live) |
|---|---|---|
| Frontend URL | https://homestead-barter.preview.emergentagent.com | https://homestead-barter.emergent.host |
| Backend URL | same preview host (`/api`) | same production host (`/api`) |
| Database | local Mongo, `DB_NAME="test_database"` | Emergent-managed Mongo (separate `MONGO_URL`/`DB_NAME` injected at deploy) |
| Purpose | build & test freely | real users/data only |

## INVARIANTS — never violate
1. **`frontend/.env` `REACT_APP_BACKEND_URL` MUST stay the PREVIEW URL** in committed
   code. The deploy pipeline substitutes the production URL at build time. NEVER
   hardcode the production URL here — doing so makes preview read/write PRODUCTION
   data (this exact bug happened once and was reverted).
2. **Backend MUST read `MONGO_URL` and `DB_NAME` only from `os.environ`** (see
   `database.py`). Never hardcode a connection string or DB name. This is what
   guarantees preview and production hit different databases.
3. **No destructive DB scripts in the repo.** Any wipe/reset utility must be a
   local one-off that is deleted after use (never committed, never run against
   production). `seed_production.py` is insert-only and idempotent (creates the
   admin ONLY if it doesn't already exist) — keep it that way.
4. **Test scripts default to the PREVIEW URL only.** `backend_test.py` and
   `backend/tests/*` use `os.environ.get("REACT_APP_BACKEND_URL", "<preview url>")`.
   Never point tests at the production host.
5. **Production admin credentials come from env vars** (`PROD_ADMIN_EMAIL`,
   `PROD_ADMIN_PASSWORD`) — never hardcode the plaintext password in any file.

## Deployment behavior to remember
- First deploy may seed production from the current preview DB. AFTER that,
  production has its own persistent database that later code-update deploys do
  NOT overwrite with preview data. If unsure whether a deploy will overwrite
  production data, confirm with Emergent Support (support@emergent.sh) BEFORE
  deploying.
- To safely test again in preview without touching production, keep invariant #1.

## Current primary admin (clean slate, Jul 3 2026)
- deathproofrebel@protonmail.com (role: admin) — password stored hashed in DB,
  and configurable for production via PROD_ADMIN_PASSWORD env var.
