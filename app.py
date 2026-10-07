from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.content import (
    ACQUISITION_HYPOTHESES,
    CAMPAIGN_BLUEPRINTS,
    LIFECYCLE_STAGES,
    PARTNERSHIP_HYPOTHESES,
    PUBLIC_CONTEXT,
    SEO_OPPORTUNITIES,
    SPRINT_PLAN,
)
from src.growth import (
    ab_test_summary,
    aggregate_channels,
    enrich_campaign_metrics,
    recommend_decision,
)


ROOT = Path(__file__).resolve().parent
DEMO_DATA = ROOT / "data" / "demo_campaigns.csv"

st.set_page_config(
    page_title="Eden Growth Acquisition Sprint",
    page_icon="↗",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.8rem;
        max-width: 1420px;
      }
      .hero {
        padding: 1.45rem 1.55rem;
        border: 1px solid #dbe7e2;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8fbfa 0%, #edf6f2 100%);
        margin-bottom: 1.05rem;
      }
      .hero h1 {
        margin: 0 0 .35rem 0;
        font-size: 2.25rem;
        letter-spacing: -.02em;
      }
      .hero p {
        margin: 0;
        color: #48615b;
        font-size: 1.02rem;
      }
      .note {
        padding: .82rem 1rem;
        border-left: 4px solid #1D6F64;
        background: #f1f6f4;
        border-radius: 8px;
        margin-bottom: .85rem;
      }
      .mini-card {
        padding: 1rem;
        border: 1px solid #dfe9e5;
        border-radius: 14px;
        background: #ffffff;
        min-height: 150px;
      }
      .mini-card h4 { margin-top: 0; margin-bottom: .45rem; }
      .eyebrow {
        color: #1D6F64;
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
      }
      div[data-testid="stMetric"] {
        border: 1px solid #dfe9e5;
        background: white;
        padding: .78rem;
        border-radius: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_demo() -> pd.DataFrame:
    return pd.read_csv(DEMO_DATA)


def money(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"€{value:,.0f}"


def ratio(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.2f}x"


def percent(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.1%}"


def upload_or_demo(key: str) -> tuple[pd.DataFrame, str]:
    uploaded = st.file_uploader(
        "Optional: upload campaign CSV",
        type=["csv"],
        key=key,
        help=(
            "Required columns: campaign, channel, objective, spend, impressions, "
            "clicks, leads, customers, revenue, repeat_customers."
        ),
    )
    if uploaded is None:
        return load_demo(), "Synthetic demo dataset"
    return pd.read_csv(uploaded), "Uploaded dataset"


def campaign_table(enriched: pd.DataFrame) -> None:
    display = enriched[
        [
            "campaign",
            "channel",
            "spend",
            "leads",
            "customers",
            "revenue",
            "cpl",
            "cac",
            "roas",
            "lead_to_customer",
            "decision",
        ]
    ].copy()

    st.dataframe(
        display.style.format(
            {
                "spend": "€{:,.0f}",
                "revenue": "€{:,.0f}",
                "cpl": "€{:,.2f}",
                "cac": "€{:,.2f}",
                "roas": "{:.2f}x",
                "lead_to_customer": "{:.1%}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">30-day growth operating prototype</div>
      <h1>Eden Growth Acquisition Sprint</h1>
      <p>
        From channel hypothesis to booking economics: what worked, what did it cost,
        what converted, and what should be tested or scaled next?
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note">
      <b>Independent portfolio case study.</b> Public Eden Therapy Clinic information
      is used only for business context. Campaign, lead, customer and revenue figures
      are synthetic demonstration data — not Eden results, internal data or forecasts.
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Growth workspace",
    [
        "Growth command centre",
        "Acquisition channels",
        "Experiment studio",
        "Conversion & A/B testing",
        "SEO & content",
        "CRM & retention",
        "Partnerships & referrals",
        "30-day sprint",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Operating principle: measure the customer outcome, not the amount of marketing activity."
)


if page == "Growth command centre":
    st.subheader("Growth command centre")
    st.caption(
        "One founder-facing view from acquisition spend to customers and revenue. "
        "The purpose is to decide where the next euro and hour should go."
    )

    raw, source_label = upload_or_demo("command_upload")
    try:
        enriched = enrich_campaign_metrics(raw)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.caption(f"Data source: **{source_label}**")

    total_spend = enriched["spend"].sum()
    total_leads = enriched["leads"].sum()
    total_customers = enriched["customers"].sum()
    total_revenue = enriched["revenue"].sum()

    paid = enriched[enriched["spend"] > 0]
    paid_cac = (
        paid["spend"].sum() / paid["customers"].sum()
        if paid["customers"].sum() > 0
        else float("nan")
    )
    paid_roas = (
        paid["revenue"].sum() / paid["spend"].sum()
        if paid["spend"].sum() > 0
        else float("nan")
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Spend", money(total_spend))
    c2.metric("Leads", f"{total_leads:,.0f}")
    c3.metric("Customers", f"{total_customers:,.0f}")
    c4.metric("Paid CAC", money(paid_cac))
    c5.metric("Paid ROAS", ratio(paid_roas))

    st.markdown("### Decision queue")
    decision_order = ["SCALE", "ITERATE", "STOP", "MEASURE"]
    decision_counts = (
        enriched.groupby("decision", as_index=False)
        .agg(campaigns=("campaign", "count"), revenue=("revenue", "sum"))
    )
    decision_counts["decision"] = pd.Categorical(
        decision_counts["decision"],
        categories=decision_order,
        ordered=True,
    )
    decision_counts = decision_counts.sort_values("decision")

    left, right = st.columns([1.15, 1])
    with left:
        fig = px.bar(
            decision_counts,
            x="decision",
            y="campaigns",
            text="campaigns",
            title="Campaigns by next action",
        )
        fig.update_layout(showlegend=False, height=340, xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown(
            """
            **Transparent demo decision rules**
            
            - **SCALE** — strong paid ROAS **and** strong lead-to-customer conversion.
            - **ITERATE** — promising economics, but a constraint still needs work.
            - **STOP** — weak downstream economics or conversion.
            - **MEASURE** — no-spend / organic activity where paid ROAS is not meaningful.
            
            These thresholds are demonstration rules. A real business should set them
            from margin, capacity, repeat behaviour and cash-flow constraints.
            """
        )

    campaign_table(enriched)

    st.download_button(
        "Download enriched scorecard CSV",
        data=enriched.to_csv(index=False).encode("utf-8"),
        file_name="growth_scorecard.csv",
        mime="text/csv",
    )

    with st.expander("Public business context used in this case study"):
        for item in PUBLIC_CONTEXT:
            st.markdown(f"- {item['observation']}")
            st.caption(f"Source: {item['source']}")


elif page == "Acquisition channels":
    st.subheader("Acquisition channels")
    st.caption(
        "Compare channels on customers, CAC and revenue — not clicks in isolation."
    )

    raw, source_label = upload_or_demo("channel_upload")
    try:
        channels = aggregate_channels(raw)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.caption(f"Data source: **{source_label}**")

    paid_channels = channels[channels["spend"] > 0].copy()

    left, right = st.columns(2)
    with left:
        roas_fig = px.bar(
            paid_channels.sort_values("roas", ascending=False),
            x="channel",
            y="roas",
            text_auto=".2f",
            title="Paid-channel ROAS",
        )
        roas_fig.update_layout(height=390, xaxis_title=None, yaxis_title="ROAS")
        st.plotly_chart(roas_fig, use_container_width=True)

    with right:
        cac_fig = px.bar(
            paid_channels.sort_values("cac"),
            x="channel",
            y="cac",
            text_auto=".0f",
            title="Paid-channel CAC",
        )
        cac_fig.update_layout(height=390, xaxis_title=None, yaxis_title="CAC (€)")
        st.plotly_chart(cac_fig, use_container_width=True)

    st.markdown("### Funnel quality by channel")
    st.dataframe(
        channels[
            [
                "channel",
                "spend",
                "clicks",
                "leads",
                "customers",
                "revenue",
                "ctr",
                "lead_to_customer",
                "cac",
                "roas",
                "repeat_rate",
            ]
        ].style.format(
            {
                "spend": "€{:,.0f}",
                "revenue": "€{:,.0f}",
                "ctr": "{:.1%}",
                "lead_to_customer": "{:.1%}",
                "cac": "€{:,.2f}",
                "roas": "{:.2f}x",
                "repeat_rate": "{:.1%}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Channel hypotheses to validate")
    st.dataframe(
        pd.DataFrame(ACQUISITION_HYPOTHESES),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "A cheap click is not the goal. A channel is useful when it produces the "
        "right customer at acceptable economics and supports sustainable repeat behaviour."
    )


elif page == "Experiment studio":
    st.subheader("Experiment studio")
    st.caption(
        "Turn a growth idea into one audience, one message, one landing experience, "
        "one primary metric and one commercial decision."
    )

    selected = st.selectbox("Choose a proposed experiment", list(CAMPAIGN_BLUEPRINTS))
    blueprint = CAMPAIGN_BLUEPRINTS[selected]

    top = st.columns(3)
    top[0].metric("Channel", blueprint["channel"])
    top[1].metric("Primary metric", blueprint["primary_metric"])
    top[2].metric("Guardrail", blueprint["guardrail"])

    st.markdown("### Launch brief")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            **Audience**  
            {blueprint['audience']}
            
            **Message**  
            {blueprint['message']}
            
            **Creative / asset**  
            {blueprint['creative']}
            """
        )
    with c2:
        st.markdown(
            f"""
            **Landing experience**  
            {blueprint['landing']}
            
            **Follow-up**  
            {blueprint['follow_up']}
            
            **Decision question**  
            Did this test acquire customers at economics worth continuing?
            """
        )

    st.markdown("### Enter observed test results")
    st.caption(
        "Defaults below are synthetic examples. In production these fields would come "
        "from the ad platform, analytics, booking and CRM systems."
    )

    r1, r2, r3, r4 = st.columns(4)
    spend = r1.number_input("Spend (€)", min_value=0.0, value=300.0, step=25.0)
    clicks = r2.number_input("Clicks / visits", min_value=0, value=500, step=25)
    leads = r3.number_input("Leads / booking starts", min_value=0, value=60, step=5)
    customers = r4.number_input("Customers / bookings", min_value=0, value=18, step=1)

    r5, r6 = st.columns(2)
    revenue = r5.number_input("Booked / purchase revenue (€)", min_value=0.0, value=2160.0, step=50.0)
    repeat_customers = r6.number_input("Repeat customers observed", min_value=0, value=4, step=1)

    lead_to_customer = customers / leads if leads > 0 else float("nan")
    cac = spend / customers if customers > 0 else float("nan")
    cpl = spend / leads if leads > 0 else float("nan")
    roas = revenue / spend if spend > 0 else float("nan")
    repeat_rate = repeat_customers / customers if customers > 0 else float("nan")

    decision = recommend_decision(
        spend=float(spend),
        customers=float(customers),
        roas=float(roas),
        lead_to_customer=float(lead_to_customer),
    )

    st.markdown("### Commercial readout")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("CPL", money(cpl))
    m2.metric("CAC", money(cac))
    m3.metric("Lead → customer", percent(lead_to_customer))
    m4.metric("ROAS", ratio(roas))
    m5.metric("Next action", decision)

    if decision == "SCALE":
        st.success(
            "Demo rule: economics are strong enough to justify a controlled scale-up. "
            "Increase gradually and watch whether CAC and customer quality hold."
        )
    elif decision == "ITERATE":
        st.warning(
            "Demo rule: keep the learning, but fix the main constraint before increasing spend."
        )
    elif decision == "STOP":
        st.error(
            "Demo rule: stop or materially change this version rather than spending through weak economics."
        )
    else:
        st.info(
            "No paid-media ROAS decision applies. Continue measuring downstream customer outcomes."
        )


elif page == "Conversion & A/B testing":
    st.subheader("Conversion & A/B testing")
    st.caption(
        "Do not promise an arbitrary uplift. Define a hypothesis, run a controlled comparison, "
        "then measure the uplift that actually occurred."
    )

    st.markdown("### Proposed conversion hypothesis")
    st.markdown(
        """
        **Hypothesis:** visitors arriving with a specific treatment intent may respond better
        when the landing page keeps the treatment, price/expectation context and booking action
        tightly aligned instead of sending them through a generic journey.
        
        **Control:** current landing experience  
        **Variant:** intent-matched headline / trust information / booking CTA
        
        **Primary metric:** completed booking  
        **Guardrails:** cancellation/no-show rate and lead quality
        """
    )

    a, b = st.columns(2)
    with a:
        st.markdown("#### Control")
        control_visitors = st.number_input(
            "Control visitors", min_value=1, value=1000, step=50
        )
        control_conversions = st.number_input(
            "Control bookings", min_value=0, value=120, step=5
        )
    with b:
        st.markdown("#### Variant")
        variant_visitors = st.number_input(
            "Variant visitors", min_value=1, value=1000, step=50
        )
        variant_conversions = st.number_input(
            "Variant bookings", min_value=0, value=145, step=5
        )

    try:
        result = ab_test_summary(
            int(control_visitors),
            int(control_conversions),
            int(variant_visitors),
            int(variant_conversions),
        )
    except ValueError as exc:
        st.error(str(exc))
    else:
        x1, x2, x3, x4 = st.columns(4)
        x1.metric("Control CVR", percent(result["control_rate"]))
        x2.metric("Variant CVR", percent(result["variant_rate"]))
        x3.metric(
            "Absolute change",
            f"{result['absolute_change'] * 100:+.2f} pp",
        )
        x4.metric("Relative uplift", percent(result["relative_uplift"]))

        st.info(
            "This readout is descriptive only. It does not automatically declare statistical "
            "significance. A real test should be sized in advance and interpreted with traffic "
            "quality, duration, guardrails and the experiment design."
        )

    st.markdown("### Experiment discipline")
    checks = [
        "Change one major hypothesis at a time.",
        "Choose the primary metric before looking at results.",
        "Keep guardrail metrics visible.",
        "Use comparable traffic allocation and an appropriate test window.",
        "Document the result even when the hypothesis loses.",
        "Scale only when the business outcome — not just engagement — improves.",
    ]
    for check in checks:
        st.markdown(f"- {check}")


elif page == "SEO & content":
    st.subheader("SEO & content")
    st.caption(
        "Prioritise search intent that can plausibly lead to a booking or purchase. "
        "No invented keyword volumes or ranking claims are used here."
    )

    seo_df = pd.DataFrame(SEO_OPPORTUNITIES)
    st.dataframe(seo_df, use_container_width=True, hide_index=True)

    st.markdown("### Content operating loop")
    s1, s2, s3 = st.columns(3)
    s1.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">1 — Intent</div>
        <h4>Start with the customer question</h4>
        Separate high-commercial intent from informational interest.
        </div>
        """,
        unsafe_allow_html=True,
    )
    s2.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">2 — Experience</div>
        <h4>Match page to intent</h4>
        Answer the important question, reduce uncertainty and keep one clear next action.
        </div>
        """,
        unsafe_allow_html=True,
    )
    s3.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">3 — Outcome</div>
        <h4>Measure beyond traffic</h4>
        Track service-page engagement, booking starts and completed bookings.
        </div>
        """,
        unsafe_allow_html=True,
    )


elif page == "CRM & retention":
    st.subheader("CRM & retention")
    st.caption(
        "Acquisition is incomplete if the customer journey ends at the first booking."
    )

    lifecycle_df = pd.DataFrame(LIFECYCLE_STAGES)
    st.dataframe(lifecycle_df, use_container_width=True, hide_index=True)

    st.markdown("### Lifecycle principles")
    st.markdown(
        """
        - Trigger messages from customer behaviour, not a blanket broadcast calendar.
        - Stop or suppress sequences when the customer has already taken the intended action.
        - Use one relevant next action rather than multiple competing CTAs.
        - Measure repeat booking and reactivation, not email opens alone.
        - Treat consent, preference and message frequency as product-quality constraints.
        """
    )

    st.markdown("### Example post-visit flow")
    st.code(
        "Completed appointment → thank-you / feedback → relevant next step → "
        "repeat booking → suppress reactivation sequence",
        language=None,
    )


elif page == "Partnerships & referrals":
    st.subheader("Partnerships & referrals")
    st.caption(
        "Treat partnerships as measurable acquisition channels, not untracked networking activity."
    )

    partner_df = pd.DataFrame(PARTNERSHIP_HYPOTHESES)
    st.dataframe(partner_df, use_container_width=True, hide_index=True)

    st.markdown("### Minimum tracking design")
    st.code(
        "Partner / referral source → tagged link or code → landing page → "
        "booking / purchase → first revenue → repeat behaviour",
        language=None,
    )

    st.info(
        "A partnership should earn continued effort by producing qualified customers "
        "at acceptable economics or strategic value — not by the number of conversations held."
    )


elif page == "30-day sprint":
    st.subheader("30-day execution sprint")
    st.caption(
        "The first month is designed to establish a reliable learning loop, not to promise miracles."
    )

    for item in SPRINT_PLAN:
        st.markdown(f"### {item['week']}")
        cols = st.columns([1, 2, 1.25])
        cols[0].markdown("**Goal**")
        cols[0].write(item["goal"])
        cols[1].markdown("**Actions**")
        cols[1].write(item["actions"])
        cols[2].markdown("**Decision**")
        cols[2].write(item["decision"])
        st.divider()

    st.markdown("### End-of-month founder scorecard")
    st.markdown(
        """
        By day 30, the useful output is not a pile of campaign activity. It is a short
        operating record showing:
        
        1. which customer / offer / channel hypotheses were tested,
        2. what each test cost,
        3. where the funnel lost customers,
        4. what converted into real bookings or revenue,
        5. what was stopped,
        6. what deserves the next round of budget and attention.
        """
    )
