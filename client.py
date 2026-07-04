"""
purchase-intent-scorer-skill: Client SDK
Score visitor purchase intent from behavioral signals and recommend interventions.
"""
from __future__ import annotations
from typing import Optional

# Scoring weights per signal (max contribution)
SIGNAL_WEIGHTS = {
    "cart_add":             25.0,
    "product_view_depth":   15.0,
    "time_on_site":         12.0,
    "search_queries":       10.0,
    "returning_visitor":     8.0,
    "past_purchases":        8.0,
    "page_depth":            7.0,
    "recency":               6.0,
    "referral_intent":       5.0,
    "device_match":          4.0,
}

REFERRAL_INTENT_SCORES = {
    "google_shopping": 1.0, "google_search": 0.8, "email": 0.9,
    "direct": 0.7, "social": 0.5, "affiliate": 0.6, "display": 0.3,
}

INTERVENTION_RULES = [
    (85, "hot",   "Show exit-intent popup with 10% off coupon if user moves to close tab."),
    (85, "hot",   "Display live social proof: 'X people viewing this product right now'."),
    (85, "hot",   "Trigger chat proactively: 'Need help choosing? We are here!'"),
    (65, "warm",  "Show a product comparison widget to help the visitor decide."),
    (65, "warm",  "Display shipping deadline reminder: 'Order in X hours for delivery by [date]'."),
    (65, "warm",  "Recommend complementary products based on current cart or page."),
    (40, "cool",  "Show trust badges and social proof section on product pages."),
    (40, "cool",  "Trigger retargeting pixel for follow-up ads on Meta and Google."),
    (40, "cool",  "Display a wishlist prompt to capture future purchase intent."),
    (0,  "cold",  "Show an email capture popup with a welcome discount."),
    (0,  "cold",  "Display best-seller or trending products section."),
    (0,  "cold",  "Activate a scroll-triggered content marketing module."),
]


class PurchaseIntentClient:
    """
    SDK for real-time purchase intent scoring from behavioral and contextual signals.
    """

    def score(
        self,
        session: dict,
        historical: Optional[dict] = None,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Score a visitor's purchase intent.

        Args:
            session: Current session signals:
                     - pages_viewed (int)
                     - time_on_site_sec (int)
                     - product_views (int)
                     - cart_adds (int)
                     - search_queries (int)
                     - is_returning (bool)
            historical: Historical data:
                     - past_purchases (int)
                     - past_sessions (int)
                     - days_since_last_visit (int)
                     - avg_order_value (float)
            context: Contextual signals:
                     - device (str: mobile/desktop/tablet)
                     - referral_source (str)
                     - time_of_day (int: 0-23)
                     - day_of_week (str)

        Returns:
            dict with intent_score, intent_tier, top_signals, recommended_interventions
        """
        hist = historical or {}
        ctx = context or {}
        signals = {}

        # Cart adds (highest weight)
        cart_adds = int(session.get("cart_adds", 0))
        signals["cart_add"] = min(SIGNAL_WEIGHTS["cart_add"] * (cart_adds * 0.8), SIGNAL_WEIGHTS["cart_add"])

        # Product view depth
        pv = int(session.get("product_views", 0))
        signals["product_view_depth"] = min(pv / 5.0, 1.0) * SIGNAL_WEIGHTS["product_view_depth"]

        # Time on site (5+ minutes = max)
        tos = int(session.get("time_on_site_sec", 0))
        signals["time_on_site"] = min(tos / 300.0, 1.0) * SIGNAL_WEIGHTS["time_on_site"]

        # Search queries (show active research)
        sq = int(session.get("search_queries", 0))
        signals["search_queries"] = min(sq / 3.0, 1.0) * SIGNAL_WEIGHTS["search_queries"]

        # Returning visitor
        signals["returning_visitor"] = SIGNAL_WEIGHTS["returning_visitor"] if session.get("is_returning") else 0.0

        # Past purchases
        pp = int(hist.get("past_purchases", 0))
        signals["past_purchases"] = min(pp / 5.0, 1.0) * SIGNAL_WEIGHTS["past_purchases"]

        # Page depth
        pg = int(session.get("pages_viewed", 0))
        signals["page_depth"] = min(pg / 8.0, 1.0) * SIGNAL_WEIGHTS["page_depth"]

        # Recency (visited in last 7 days = full score)
        days = int(hist.get("days_since_last_visit", 999))
        signals["recency"] = max(0, 1 - days / 30.0) * SIGNAL_WEIGHTS["recency"]

        # Referral intent
        ref = str(ctx.get("referral_source", "direct")).lower()
        ref_score = REFERRAL_INTENT_SCORES.get(ref, 0.4)
        signals["referral_intent"] = ref_score * SIGNAL_WEIGHTS["referral_intent"]

        # Device match (desktop = slightly higher intent on e-com)
        device = str(ctx.get("device", "desktop")).lower()
        signals["device_match"] = SIGNAL_WEIGHTS["device_match"] if device == "desktop" else SIGNAL_WEIGHTS["device_match"] * 0.7

        raw_score = sum(signals.values())
        intent_score = round(min(raw_score, 100.0), 1)

        # Tier classification
        if intent_score >= 80:
            tier = "hot"
        elif intent_score >= 55:
            tier = "warm"
        elif intent_score >= 30:
            tier = "cool"
        else:
            tier = "cold"

        # Top signals
        top_signals = sorted(
            [{"signal": k, "contribution": round(v, 1), "max": SIGNAL_WEIGHTS[k]} for k, v in signals.items() if v > 0],
            key=lambda x: x["contribution"], reverse=True
        )[:5]

        # Interventions
        interventions = [
            rule[2] for rule in INTERVENTION_RULES
            if intent_score >= rule[0] and rule[1] == tier
        ][:3]

        return {
            "intent_score": intent_score,
            "intent_tier": tier,
            "top_signals": top_signals,
            "recommended_interventions": interventions,
            "signal_breakdown": {k: round(v, 2) for k, v in signals.items()},
        }

    def batch_score(self, visitors: list[dict]) -> list[dict]:
        """Score multiple visitors at once."""
        results = []
        for v in visitors:
            result = self.score(
                session=v.get("session", {}),
                historical=v.get("historical", {}),
                context=v.get("context", {}),
            )
            result["visitor_id"] = v.get("visitor_id", "unknown")
            results.append(result)
        results.sort(key=lambda x: x["intent_score"], reverse=True)
        return results
