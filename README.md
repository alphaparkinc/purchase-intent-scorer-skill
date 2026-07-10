# genpark-purchase-intent-scorer-skill

> **GenPark AI Agent Skill** -- Score visitor purchase intent from behavioral signals and recommend personalized interventions.

## Features

- 10-signal scoring model: cart adds, product views, time on site, search queries, recency, referral intent, and more
- Intent tiers: Hot (80+) / Warm (55-79) / Cool (30-54) / Cold (<30)
- Platform-specific interventions per tier (exit-intent popups, social proof, retargeting)
- Batch scoring for visitor prioritization
- Full signal breakdown for analytics

## Quick Start

```python
from client import PurchaseIntentClient

client = PurchaseIntentClient()
result = client.score(
    session={"product_views": 4, "cart_adds": 1, "time_on_site_sec": 300, "is_returning": True},
    historical={"past_purchases": 2},
    context={"referral_source": "google_shopping"},
)
print(f"Score: {result['intent_score']} | Tier: {result['intent_tier']}")
print(result["recommended_interventions"])
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
