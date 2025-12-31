from datetime import datetime


# -----------------------------
# HEALTH SCORING
# -----------------------------
def calculate_health(customer):
    score = 100

    if customer["usage_per_week"] < 2:
        score -= 25
    if customer["open_tickets"] > 5:
        score -= 20
    if customer["nps"] < 6:
        score -= 20
    if customer["days_since_login"] > 14:
        score -= 15
    if customer["contract_age_months"] < 3:
        score -= 10

    score = max(score, 0)

    if score >= 70:
        status = "Green"
    elif score >= 40:
        status = "Amber"
    else:
        status = "Red"

    return score, status


# -----------------------------
# TRENDS
# -----------------------------
def calculate_trends(customer):
    return {
        "usage": customer["usage_per_week"] - customer["usage_prev_period"],
        "tickets": customer["open_tickets"] - customer["open_tickets_prev_period"],
        "nps": customer["nps"] - customer["nps_prev_period"],
    }


# -----------------------------
# RENEWALS
# -----------------------------
def days_to_renewal(customer):
    renewal_date = datetime.strptime(customer["renewal_date"], "%Y-%m-%d")
    return (renewal_date - datetime.today()).days


def renewal_flag(days, score):
    if days < 90 and score < 50:
        return "High renewal risk"
    if days < 90:
        return "Renewal approaching"
    return "No immediate risk"


# -----------------------------
# ACTION ENGINE
# -----------------------------
def recommend_actions(customer, score, renewal_days):
    actions = []

    if score < 50:
        actions.append("Schedule enablement session")

    if customer["usage_per_week"] < 2:
        actions.append("Offer onboarding refresher")

    if renewal_days < 90:
        actions.append("Prepare renewal alignment call")

    if score > 75 and customer["nps"] > 8:
        actions.append("Explore expansion opportunity")

    return actions


# -----------------------------
# CLIENT NARRATIVE
# -----------------------------
def generate_client_summary(customer, score, trends, renewal_days):
    intro = f"Here’s a snapshot of how things are currently tracking for **{customer['customer_name']}**."

    if score >= 75:
        engagement = (
            "Overall engagement is strong. Platform usage is consistent and well embedded "
            "in day-to-day workflows."
        )
    elif score >= 50:
        engagement = (
            "Engagement is steady, with clear signs of value being realised. "
            "There are opportunities to unlock additional benefit."
        )
    else:
        engagement = (
            "Engagement has softened recently, suggesting priorities may have shifted. "
            "This is a good moment to realign the platform to current needs."
        )

    trend_notes = []
    if trends["usage"] > 0:
        trend_notes.append("Usage has increased compared to the previous period.")
    elif trends["usage"] < 0:
        trend_notes.append("Usage is slightly down compared to the previous period.")

    if trends["tickets"] < 0:
        trend_notes.append("Support volume has reduced, indicating improved stability.")
    elif trends["tickets"] > 0:
        trend_notes.append("Support activity has increased, highlighting areas to review.")

    trend_section = (
        " ".join(trend_notes)
        if trend_notes
        else "Engagement levels are broadly consistent period over period."
    )

    if renewal_days < 60:
        renewal = (
            "With renewal approaching, this is an ideal time to ensure the platform "
            "is fully aligned to your goals and delivering maximum value."
        )
    elif renewal_days < 120:
        renewal = (
            "As we move toward the next renewal window, we’ll continue strengthening "
            "adoption and impact."
        )
    else:
        renewal = (
            "Our focus remains on long-term value and continuous improvement."
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

I wanted to share a brief overview of your recent platform engagement and a few observations.

{summary}

If useful, I’d be very happy to set up a short session to walk through this together and discuss next steps.

Best regards,  
Customer Success Team
"""
