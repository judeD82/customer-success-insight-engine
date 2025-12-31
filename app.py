import streamlit as st
import pandas as pd
import plotly.express as px

from logic import (
    calculate_health,
    calculate_trends,
    days_to_renewal,
    renewal_flag,
    recommend_actions,
    generate_client_summary,
    generate_email_draft,
)
from sample_data import generate_sample_data


# --------------------------------------------------
# PAGE CONFIG + THEME
# --------------------------------------------------
st.set_page_config(page_title="Customer Health Control Room", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
}
.card {
    background: white;
    border-radius: 14px;
    padding: 1.25rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 1.25rem;
}
.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🚦 Customer Health Control Room")
st.caption("Executive-grade Customer Success intelligence")


# --------------------------------------------------
# DATA SOURCE
# --------------------------------------------------
mode = st.radio("Data source:", ["Use sample data", "Upload CSV"])

if mode == "Upload CSV":
    uploaded = st.file_uploader("Upload customer CSV", type=["csv"])
    if not uploaded:
        st.stop()
    df = pd.read_csv(uploaded)
else:
    df = generate_sample_data()
    st.success("Sample data loaded")


# --------------------------------------------------
# HEALTH + TRENDS
# --------------------------------------------------
df[["health_score", "status"]] = df.apply(
    lambda r: pd.Series(calculate_health(r)), axis=1
)

# --------------------------------------------------
# PORTFOLIO DONUT
# --------------------------------------------------
status_counts = df["status"].value_counts().reset_index()
status_counts.columns = ["Status", "Count"]

fig_portfolio = px.pie(
    status_counts,
    names="Status",
    values="Count",
    hole=0.6,
    color="Status",
    color_discrete_map={
        "Green": "#2e7d32",
        "Amber": "#f9a825",
        "Red": "#c62828",
    },
)

fig_portfolio.update_traces(textinfo="none")
fig_portfolio.update_layout(height=280, margin=dict(t=0, b=0, l=0, r=0))

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Portfolio Health</div>', unsafe_allow_html=True)
st.plotly_chart(fig_portfolio, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# CUSTOMER SELECTION
# --------------------------------------------------
customer_name = st.selectbox("Select customer", df["customer_name"])
customer = df[df["customer_name"] == customer_name].iloc[0]

score, status = customer["health_score"], customer["status"]
trends = calculate_trends(customer)
renewal_days = days_to_renewal(customer)
actions = recommend_actions(customer, score, renewal_days)


# --------------------------------------------------
# MOMENTUM BAR
# --------------------------------------------------
trend_df = pd.DataFrame({
    "Metric": ["Usage", "Support", "NPS"],
    "Change": [trends["usage"], -trends["tickets"], trends["nps"]],
})

fig_trends = px.bar(
    trend_df,
    x="Metric",
    y="Change",
    color="Change",
    color_continuous_scale=["#c62828", "#f9a825", "#2e7d32"],
)

fig_trends.update_layout(height=260, showlegend=False)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Momentum</div>', unsafe_allow_html=True)
st.plotly_chart(fig_trends, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# CLIENT SUMMARY
# --------------------------------------------------
summary = generate_client_summary(customer, score, trends, renewal_days)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Client Engagement Summary</div>', unsafe_allow_html=True)
st.markdown(summary.replace("\n", "<br>"), unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# ACTIONS
# --------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Recommended Focus Areas</div>', unsafe_allow_html=True)
for a in actions:
    st.markdown(f"• {a}")
st.markdown('</div>', unsafe_allow_html=True)


# --------------------------------------------------
# EMAIL
# --------------------------------------------------
email = generate_email_draft(customer, summary)
st.text_area("Client email draft", email, height=220)
