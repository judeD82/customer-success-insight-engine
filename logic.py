from datetime import datetime


# --------------------------------------------------
# HEALTH SCORING
# --------------------------------------------------
def calculate_health(customer):
    score = 100
    reasons = []

    if customer["usage_per_week"] < 2:
        score -= 25
        reasons.append("Low product usage")

    if customer["open_tickets"] > 5:
        score -= 20
        reasons.append("High support ticket volume")

    if customer["nps"] < 6:
        score -= 20
        reasons.append("Low NPS score")

    if customer["days_since_login"] > 14:
        score -= 15
        reasons.append("No recent login activity")

    if customer["contract_age_months"] < 3:
        score -= 10
        reasons.append("Early lifecycle customer")

    score = max(score, 0)

    if score >= 70:
        status = "Green"
    elif score >= 40:
        status = "Amber"
    else:
        status = "Red"

    return score, status, reasons


# --------------------------------------------------
# TREND LOGIC
# --------------------------------------------------
def calculate_trends(customer):
    return {
        "usage": customer["usage_per_week"] - customer["usage_prev_period"],
        "tickets": customer["open_tickets"] - customer["open_tickets_prev_period"],
        "nps": customer["nps"] - customer["nps_prev_period"],
    }


# --------------------------------------------------
# RENEWAL / REVENUE LOGIC
# --------------------------------------------------
def days_to_renewal(customer):
    renewal_date = datetime.strptime(customer["renewal_date"], "%Y-%m-%d")
    return (renewal_date - datetime.today()).days


def renewal_risk_flag(customer, health_score):
    days = days_to_renewal(customer)

    if days < 90 and health_score < 50:
        return "High renewal risk"
    elif days < 90:
        return "Renewal approaching"
    else:
        return "No immediate renewal risk"


# --------------------------------------------------
# ACTION ENGINE
# --------------------------------------------------
def recommend_actions(customer, health_score, renewal_days):
    actions = []

    if health_score < 50:
        actions.append("Schedule enablement session")

    if customer["usage_per_week"] < 2:
        actions.append("Offer onboarding refresher")

    if renewal_days < 90:
        actions.append("Prepare renewal alignment call")

    if health_score > 75 and customer["nps"] > 8:
        actions.append("Explore expansion opportunity")

    return actions


# --------------------------------------------------
# CLIENT-FACING NARRATIVE
# --------------------------------------------------
def generate_client_summary(customer, health_score, trends, renewal_days):
    intro = f"Here’s a snapshot of how things are currently tracking for **{customer['customer_name']}**."

    if health_score >= 75:
        engagement = (
            "Overall engagement is strong. Platform usage is consistent, and activity patterns "
            "suggest the product is well embedded in day-to-day workflows."
        )
    elif health_score >= 50:
        engagement = (
            "Engagement is steady, with clear signs of value being realised. "
            "There are a few areas where we can help unlock additional benefit."
        )
    else:
        engagement = (
            "Engagement has softened recently. This is often a sign that priorities have shifted, "
            "and it’s a good moment to realign the platform to current needs."
        )

    trend_notes = []

    if trends["usage"] > 0:
        trend_notes.append("Usage has increased compared to the previous period.")
    elif trends["usage"] < 0:
        trend_notes.append("Usage is slightly down compared to the previous period.")

    if trends["tickets"] > 0:
        trend_notes.append("Support activity has increased, which may indicate areas needing clarification.")
    elif trends["tickets"] < 0:
        trend_notes.append("Support volume has reduced, suggesting improved stability.")

    trend_section = (
        " ".join(trend_notes)
        if trend_notes
        else "Engagement levels are broadly consistent period over period."
    )

    if renewal_days < 60:
        renewal = (
            "With renewal approaching, this is a good time to ensure the platform is fully aligned "
            "to your current goals and delivering maximum value."
        )
    elif renewal_days < 120:
        renewal = (
            "As we move toward the next renewal window, we’ll continue to focus on strengthening "
            "adoption and impact."
        )
    else:
        renewal = (
            "At this stage in the contract, our focus remains on long-term value and continuous improvement."
        )

    return f"""
{intro}

**Engagement overview**  
{engagement}

**What we’re seeing**  
{trend_section}

**Looking ahead**  
{renewal}
""".strip()


def generate_email_draft(customer, summary):
    return f"""Subject: Engagement Overview – {customer['customer_name']}

Hi {customer['customer_name']} team,

I hope you’re well.

I wanted to share a short overview of your recent platform engagement and a few observations from our side.

{summary}

If helpful, I’d be very happy to set up a short session to walk through this together and discuss next steps.

Best regards,  
Customer Success Team
"""
