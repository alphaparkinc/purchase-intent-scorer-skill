"""
example_usage.py -- Demonstrates the PurchaseIntentClient SDK.
"""
from client import PurchaseIntentClient

def main():
    client = PurchaseIntentClient()

    print("[1] Single Visitor Intent Scoring")
    result = client.score(
        session={
            "pages_viewed": 8,
            "time_on_site_sec": 420,
            "product_views": 4,
            "cart_adds": 2,
            "search_queries": 2,
            "is_returning": True,
        },
        historical={
            "past_purchases": 2,
            "past_sessions": 5,
            "days_since_last_visit": 3,
            "avg_order_value": 65.0,
        },
        context={
            "device": "desktop",
            "referral_source": "google_shopping",
            "time_of_day": 14,
            "day_of_week": "Friday",
        }
    )
    print(f"Intent Score: {result['intent_score']}/100")
    print(f"Intent Tier: {result['intent_tier'].upper()}")
    print(f"\nTop Signals:")
    for sig in result["top_signals"]:
        print(f"  {sig['signal']:<25}: {sig['contribution']:>5.1f} / {sig['max']:.0f}")
    print(f"\nRecommended Interventions:")
    for action in result["recommended_interventions"]:
        print(f"  -> {action}")

    print("\n[2] Batch Scoring -- Visitor Prioritization")
    visitors = [
        {"visitor_id":"V001","session":{"product_views":5,"cart_adds":2,"time_on_site_sec":600,"is_returning":True},"historical":{"past_purchases":3},"context":{"referral_source":"email"}},
        {"visitor_id":"V002","session":{"product_views":1,"cart_adds":0,"time_on_site_sec":45,"is_returning":False},"historical":{},"context":{"referral_source":"display"}},
        {"visitor_id":"V003","session":{"product_views":3,"cart_adds":1,"time_on_site_sec":180,"is_returning":False},"historical":{"past_purchases":1},"context":{"referral_source":"google_search"}},
    ]
    batch = client.batch_score(visitors)
    print(f"{'Visitor':<10} {'Score':>8} {'Tier':>8}")
    for v in batch:
        print(f"{v['visitor_id']:<10} {v['intent_score']:>8.1f} {v['intent_tier'].upper():>8}")

if __name__ == "__main__":
    main()
