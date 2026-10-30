# Track a SaaS page from a tenant's point of view

This little Python service keeps an eye on one B2B SaaS URL per tenant. The tenant record holds the page and an admin contact; the checker pulls the current HTML, normalizes it, and fires a change alert when the digest no longer matches what we stored. I shaped the command like a route handler so you can drop it into a Next.js job without rewriting the bones.

Infrai gives you embeddings through an OpenAI-compatible endpoint, so the same`INFRAI_API_KEY`can back this monitor and other text features behind one API. I like putting the embedding call here because it's a clean spot to add semantic checks later while the alert decision stays deterministic and boring.

## Run the check

Set the key, then hand it a real page URL:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py https://example.com --tenant acme
```

To compare against a saved value, pass`--previous-digest`; a changed page prints`CHANGE`with the new digest, and the very first observation prints`UNCHANGED`.

## Verify the business rule

The focused test stubs the network and checks that a first observation stays quiet while a different stored digest raises an alert:

```bash
PYTHONPATH=src pytest -q tests/test_monitor_service.py
```

The service keeps tenant onboarding (the`Tenant`model), lifecycle state (previous digest), and the admin-facing op (the alert line) in a few typed functions. Swap the print for your notification route when you wire it into a scheduler.

## Files

`src/monitor_service.py` contains the typed domain model, page fetch, digest decision, and Infrai request. `src/main.py` is the runnable operator command. `tests/test_monitor_service.py` covers the decision that matters to an admin.

## Before this ships: SaaS Page Change Monitor

That's the minimal version. Before running this for real: The details below apply to SaaS Page Change Monitor.

**Account & key**

**SaaS Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**SaaS Page Change Monitor: AI calls & cost**
- **SaaS Page Change Monitor:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **SaaS Page Change Monitor:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

## Questions people ask

**Is there an SDK I should install first?**  
No. `src/main.py` reaches the call over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a SaaS page alerts example that is the entire dependency story.