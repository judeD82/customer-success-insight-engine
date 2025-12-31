import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

from logic import (
    calculate_health,
    calculate_trends,
    days_to_renewal,
    renewal_risk_flag,
    recommend_actions,
    generate_client_summary,
    generate_email_draft,
)

from sample_data import generate_sample_data


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Customer Health Control Room",
    layout="wide",
)

st.title("🚦 Customer Health Control Room")
st.caption("Operational dashboard for Customer Success teams")


# --------------------------------------------------
# DATA SOURCE
# --------------------------------------------------
st.subheader("Data Source")

data_mode = st.radio(
    "Choose how to load customer data:",
    ["Upload CSV", "Use sample data"],
)

if data_mode == "Upload CSV":
    uploaded_file = st.file_uploader(
        "Upload customer data (.csv)",
        type=["csv"],
    )

    if not uploaded_file:
        st.info("Please upload a customer CSV file to begin.")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error("Unable to read CSV file.")
        st.code(str(e))
        st.stop()

else:
    df = generate_sample_data()
    st.success("Sample customer data loaded.")


# --------------------------------------------------
# SCHEMA VALIDATION
# --------------------------------------------------
REQUIRED_COLUMNS = [
    "customer_name",
    "usage_per_week",
    "open_tickets",
    "nps",
    "days_since_login",
    "contract_age_months",
    "usage_prev_period",
    "open_tickets_prev_period",
    "nps_prev_period",
    "renewal_date",
    "contract_value",
]

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing:
    st.error("The following required columns are missing:")
    st.write(missing)
    st.stop()


# --------------------------------------------------
# HEALTH CALCULATION
# --------------------------------------------------
df[["health_score", "status", "reasons"]] = df.apply(
    lambda row: pd.Series(calculate_health(row)),
    axis=1,
)


# --------------------------------------------------
# KPI ROW
# --------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Healthy", len(df[df["status"] == "Green"]))
k2.metric("At Risk", len(df[df["status"] == "Amber"]))
k3.metric("Critical", len(df[df["status"] == "Red"]))
k4.metric("Avg Health Score", round(df["health_score"].mean(), 1))

st.divider()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

status_filter = st.sidebar.multiselect(
    "Health status",
    ["Green", "Amber", "Red"],
    default=["Green", "Amber", "Red"],
)

filtered_df = df[df["status"].isin(status_filter)]

if filtered_df.empty:
    st.warning("No customers match the selected filters.")
    st.stop()


# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------
left, right = st.columns([1, 2])

with left:
    st.subheader("Customers")
    selected_customer = st.radio(
        "",
        filtered_df["customer_name"].tolist(),
    )

customer = df[df["customer_name"] == selected_customer].iloc[0]


with right:
    st.subheader(f"Customer Overview: {selected_customer}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Health Score", int(customer["health_score"]))
    c2.metric("Status", customer["status"])
    c3.metric("NPS", int(customer["nps"]))

    st.markdown("### Key Signals")
    st.write(f"Usage per week: {customer['usage_per_week']}")
    st.write(f"Open tickets: {customer['open_tickets']}")
    st.write(f"Days since last login: {customer['days_since_login']}")
    st.write(f"Contract age (months): {customer['contract_age_months']}")

    # --------------------------------------------------
    # TRENDS
    # --------------------------------------------------
    trends = calculate_trends(customer)

    st.markdown("### Trends vs Previous Period")
    st.write(f"Usage change: {trends['usage']:+}")
    st.write(f"Ticket change: {trends['tickets']:+}")
    st.write(f"NPS change: {trends['nps']:+}")

    # --------------------------------------------------
    # RENEWAL & ACTIONS
    # --------------------------------------------------
    renewal_days = days_to_renewal(customer)
    renewal_status = renewal_risk_flag(customer, customer["health_score"])

    st.markdown("### Revenue Signals")
    st.write(f"Days to renewal: {renewal_days}")
    st.warning(renewal_status)

    actions = recommend_actions(
        customer,
        customer["health_score"],
        renewal_days,
    )

    st.markdown("### Recommended Next Actions")
    if actions:
        for action in actions:
            st.success(action)
    else:
        st.info("No immediate actions recommended.")

    # --------------------------------------------------
    # CLIENT-FACING REPORT
    # --------------------------------------------------
    st.divider()
    st.subheader("📄 Client-Facing Summary")

    summary = generate_client_summary(
        customer,
        customer["health_score"],
        trends,
        renewal_days,
    )
    st.markdown(summary)

    # Chart
    fig, ax = plt.subplots()
    ax.bar(
        ["Usage", "Tickets", "Days Since Login"],
        [
            customer["usage_per_week"],
            customer["open_tickets"],
            customer["days_since_login"],
        ],
    )
    ax.set_title("Engagement Overview")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)

    st.image(buf, caption="Engagement Overview")

    st.download_button(
        "Download engagement chart",
        data=buf,
        file_name=f"{selected_customer}_engagement.png",
        mime="image/png",
    )

    # --------------------------------------------------
    # CLIENT EMAIL
    # --------------------------------------------------
    st.subheader("📧 Client Email Draft")

    email_text = generate_email_draft(customer, summary)
    st.text_area(
        "Copy into email client:",
        email_text,
        height=260,
    )
