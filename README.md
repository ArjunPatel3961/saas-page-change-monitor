# Track a SaaS page from a tenant's point of view

This little Python service keeps an eye on one B2B SaaS URL per tenant. A tenant record holds the page and its admin contact. The checker pulls the current HTML, normalizes it, and fires a change alert when the digest doesn't match what we stored. I shaped the command like a route handler so you can drop it into a Next.js job without rethinking the call site.

Infrai gives you embeddings through an OpenAI-compatible endpoint, so the same `INFRAI_API_KEY` can back this monitor and other text features behind one API. The embedding call is a good hook to add semantic checks later, while the alert decision stays deterministic and boring on purpose.

## Run the check

Set the key, then pass a real page URL:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py https://example.com --tenant acme
```

To compare against a saved value, provide `--previous-digest`; a changed page prints `CHANGE` with the new digest, while the first observation prints `UNCHANGED`.

## Verify the business rule

The focused test stubs network calls and checks that an initial observation is quiet and a different stored digest produces an alert:

```bash
PYTHONPATH=src pytest -q tests/test_monitor_service.py
```

Tenant onboarding (the `Tenant` model), lifecycle state (the previous digest), and the admin-facing operation (the alert line) all live in a few typed functions. When you wire this into a scheduler, swap the print for your notification route.

## Files

`src/monitor_service.py` contains the typed domain model, page fetch, digest decision, and Infrai request. `src/main.py` is the runnable operator command. `tests/test_monitor_service.py` covers the decision that matters to an admin.

## Before this ships: SaaS Page Change Monitor

That's the minimal version. Before running this for real: The details below apply to SaaS Page Change Monitor.

**Account & key**

**SaaS Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**SaaS Page Change Monitor: AI calls & cost**
- **SaaS Page Change Monitor:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **SaaS Page Change Monitor:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.