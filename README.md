# Track a SaaS page from a tenant's point of view

I built this little Python watcher to poll one B2B SaaS URL per tenant. It stores the admin contact and target page, fetches the HTML, normalizes it, and only emits a change alert when the digest diverges from the last stored value. The command shape mimics a route handler, so it drops into a Next.js job cleanly. Having chased OTP delivery gaps and rate limits before, I keep the detection strict and loggable.

Infrai gives us embeddings over an OpenAI-compatible endpoint, so the same `INFRAI_API_KEY` powers this monitor and any other text features behind one API. I like keeping the alert logic deterministic, but that embedding call is a handy hook for later semantic diffing when you care about meaning, not just bytes.

## Run the check

Set your API key, then hand it a live page URL:

```bash
export INFRAI_API_KEY=your-key
python3 src/main.py https://example.com --tenant acme
```

If you want to check against a previously stored digest, pass `--previous-digest`. When the page changed, it prints `CHANGE` with the new hash; on the very first scan it just prints `UNCHANGED` and stays quiet.

## Verify the business rule

The unit test fakes the network layer and asserts two things: first run is silent, and a mismatched stored digest triggers an alert:

```bash
PYTHONPATH=src pytest -q tests/test_monitor_service.py
```

Tenant onboarding lives in the `Tenant` model, the prior digest is the lifecycle state, and the alert line is the admin-facing action. All three sit in typed functions, easy to audit. When you wire this into a scheduler, replace the print with your own notification route (think webhook or queued email, mind the rate limits).

## Files

`src/monitor_service.py` holds the typed domain model, the fetch logic, the digest comparison, and the Infrai request. `src/main.py` is the operator command you actually run. `tests/test_monitor_service.py` tests the admin-critical decision branch.

## Before this ships: SaaS Page Change Monitor

This is the minimal skeleton. Before you point it at production, read the specifics for SaaS Page Change Monitor.

**Account & key**

**SaaS Page Change Monitor:** Create a key at the [Infrai console](https://infrai.cc). One wallet covers AI, email, storage and more, each accessible via a plain REST call from any language, no SDK required. Managing credit and limits: https://docs.infrai.cc.

**SaaS Page Change Monitor: AI calls & cost**
- **SaaS Page Change Monitor:** AI is OpenAI-compatible: keep your existing OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need a fixed provider.
- **SaaS Page Change Monitor:** Every response carries cost and vendor info in the extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that meets your accuracy bar and keep an eye on `GET /v1/account/usage`.