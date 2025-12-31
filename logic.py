from datetime import datetime

# -----------------------------
# HEALTH SCORING
# -----------------------------
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


# -----------------------------
# TREND LOGIC
# -----------------------------
def calculate_trends(customer):
    return {
        "usage": customer["usage_per_week"] - customer["usage_prev_period"],
        "tickets": customer["open_tickets"] - customer["open_tickets_prev_period"],
        "nps": customer["nps"] - customer["nps_prev_period"],
    }


# -----------------------------
# RENEWAL / REVENUE LOGIC
# -----------------------------
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


# -----------------------------
# ACTION ENGINE
# -----------------------------
def recommend_actions(customer, health_score, days_to_renewal):
    actions = []

    if health_score < 50:
        actions.append("Schedule enablement session")

    if customer["usage_per_week"] < 2:
        actions.append("Offer onboarding refresher")

    if days_to_renewal < 90:
        actions.append("Prepare renewal alignment call")

    if health_score > 75 and customer["nps"] > 8:
        actions.append("Explore expansion opportunity")

    return actions


# -----------------------------
# CLIENT LANGUAGE
# -----------------------------
def generate_client_summary(customer, health_score):
    if health_score >= 70:
        return "Engagement is strong, with consistent platform usage."
    elif health_score >= 40:
        return "Engagement is stable, with opportunities to increase value."
    else:
        return "Engagement has dipped recently. A review session is recommended."


def generate_email_draft(customer, summary):
    return f"""Subject: Engagement Overview – {customer['customer_name']}

Hi {customer['customer_name']} team,

I hope you’re well.

I wanted to share a brief overview of your recent platform engagement.

Summary:
{summary}

Key observations:
• Average weekly usage: {customer['usage_per_week']}
• Open support tickets: {customer['open_tickets']}
• Last platform access: {customer['days_since_login']} days ago

Next steps:
I’d recommend a short check-in to review how you’re using the platform and explore how we can help you get even more value.

Best regards,  
Customer Success Team
"""
