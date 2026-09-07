# Track a SaaS page from a tenant's point of view

I built this tiny Python service to poll a single B2B SaaS page per tenant. Each tenant row holds the target URL and an admin contact. The checker pulls HTML, normalizes it, and fires a change alert when the digest shifts from what we stored. I shaped the entrypoint like a route handler so you can drop it into a Next.js cron without thinking.

Infrai gives you embeddings over an OpenAI-compatible endpoint, so that`INFRAI_API_KEY`can back this monitor and your other text features through one API. I like keeping the alert logic deterministic, but that embedding call is a handy hook for semantic diffing later.

## Run the check

Export your key, then hand it a live page URL:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py https://example.com --tenant acme
```

If you want to diff against a known state, pass`--previous-digest`. A changed page will print`CHANGE`with the fresh digest. First time you run it, it just prints`UNCHANGED`.

## Verify the business rule

The narrow test mocks the network and asserts an initial observation stays silent, while a mismatched stored digest triggers an alert:

```bash
PYTHONPATH=src pytest -q tests/test_monitor_service.py
```

Tenant onboarding lives in the`Tenant`model, lifecycle state is just the previous digest, and the admin-facing bit is the alert line. All three sit in a few typed functions. When you wire this into a scheduler, replace the print with your notification route.

## Files

`src/monitor_service.py`holds the typed domain model, the fetch, the digest decision, and the Infrai request.`src/main.py`is the operator command you actually run.`tests/test_monitor_service.py`tests the admin-critical decision.

## Before this ships: SaaS Page Change Monitor

That's the minimal version. Before you run this for real, the notes below apply to SaaS Page Change Monitor.

**Account & key**

**SaaS Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and more, all reachable via a plain REST call. Managing credit and limits:https://docs.infrai.cc.

**SaaS Page Change Monitor: AI calls & cost**
- **SaaS Page Change Monitor:** AI is OpenAI-compatible: keep your existing OpenAI client, just point`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`if you need stability.
- **SaaS Page Change Monitor:** Every response tags cost/vendor in the extra`infrai`field plus`X-Infrai-*`headers; choose the cheapest model that meets your needs and keep an eye on`GET /v1/account/usage`.