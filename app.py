from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.content import (
    CAMPAIGN_BLUEPRINTS,
    KPI_GLOSSARY,
    LIFECYCLE_STAGES,
    MEASUREMENT_PLAN,
    PAID_MEDIA_PLAYBOOKS,
    PARTNERSHIP_HYPOTHESES,
    SEO_OPPORTUNITIES,
    SOCIAL_CONTENT_PLAYS,
    SPRINT_PLAN,
)
from src.growth import ab_test_summary, aggregate_channels, enrich_campaign_metrics, recommend_decision


ROOT = Path(__file__).resolve().parent
DEMO_DATA = ROOT / "data" / "demo_campaigns.csv"
PAID_CHANNELS = {"Google Search", "Meta Paid Social"}

st.set_page_config(
    page_title="Eden Growth Acquisition Sprint",
    page_icon="↗",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 2.8rem; max-width: 1380px;}
      .hero {
        padding: 1.3rem 1.45rem;
        border: 1px solid #dbe7e2;
        border-radius: 18px;
        background: linear-gradient(135deg, #f8fbfa 0%, #edf6f2 100%);
        margin-bottom: .8rem;
      }
      .hero h1 {margin: 0 0 .25rem 0; font-size: 2.15rem; letter-spacing: -.02em;}
      .hero p {margin: 0; color: #48615b; font-size: 1rem;}
      .eyebrow {
        color: #1D6F64;
        font-size: .76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .06em;
      }
      .mini-card {
        padding: 1rem;
        border: 1px solid #dfe9e5;
        border-radius: 14px;
        background: #fff;
        min-height: 150px;
      }
      .mini-card h4 {margin-top: .25rem; margin-bottom: .45rem;}
      div[data-testid="stMetric"] {
        border: 1px solid #dfe9e5;
        background: white;
        padding: .72rem;
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


def get_data() -> tuple[pd.DataFrame, str]:
    if "growth_data" not in st.session_state:
        st.session_state.growth_data = load_demo()
        st.session_state.growth_source = "Synthetic demo dataset"
    return st.session_state.growth_data, st.session_state.growth_source


def data_controls() -> None:
    with st.expander("Data source / upload"):
        uploaded = st.file_uploader(
            "Upload campaign CSV",
            type=["csv"],
            help=(
                "Required columns: campaign, channel, objective, spend, impressions, "
                "clicks, leads, customers, revenue, repeat_customers."
            ),
        )
        c1, c2 = st.columns([1, 1])
        if uploaded is not None and c1.button("Use uploaded data"):
            st.session_state.growth_data = pd.read_csv(uploaded)
            st.session_state.growth_source = "Uploaded dataset"
            st.rerun()
        if c2.button("Reset to demo data"):
            st.session_state.growth_data = load_demo()
            st.session_state.growth_source = "Synthetic demo dataset"
            st.rerun()
        st.caption(
            "Demo campaign, lead, customer and revenue figures are synthetic. "
            "The upload path is included so the same workflow can accept first-party exports."
        )


def compact_campaign_table(df: pd.DataFrame) -> None:
    display = df[
        [
            "campaign",
            "channel",
            "spend",
            "customers",
            "revenue",
            "cac",
            "roas",
            "decision",
        ]
    ].copy()
    st.dataframe(
        display.style.format(
            {
                "spend": "€{:,.0f}",
                "revenue": "€{:,.0f}",
                "cac": "€{:,.0f}",
                "roas": "{:.2f}x",
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
      <p>Acquire → convert → retain → measure → decide what deserves the next euro and hour.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Independent portfolio case study · public Eden business context + synthetic demo performance data · "
    "no internal Eden campaign, customer or revenue data."
)

page = st.sidebar.radio(
    "Growth workspace",
    [
        "Growth overview",
        "Acquisition & campaigns",
        "Conversion & retention",
        "30-day sprint",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Operating principle: measure customer outcomes, not marketing activity for its own sake.")


if page == "Growth overview":
    st.subheader("Growth overview")
    st.caption(
        "A founder-facing view of what converted, what it cost and what should happen next."
    )

    data_controls()
    raw, source_label = get_data()

    try:
        enriched = enrich_campaign_metrics(raw)
        channels = aggregate_channels(raw)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    paid = enriched[enriched["channel"].isin(PAID_CHANNELS)].copy()
    paid_channel_summary = channels[channels["channel"].isin(PAID_CHANNELS)].copy()

    paid_spend = paid["spend"].sum()
    paid_customers = paid["customers"].sum()
    paid_revenue = paid["revenue"].sum()
    paid_cac = paid_spend / paid_customers if paid_customers else float("nan")
    paid_roas = paid_revenue / paid_spend if paid_spend else float("nan")
    all_customers = enriched["customers"].sum()

    st.caption(f"Data source: **{source_label}**")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Paid-media spend", money(paid_spend))
    c2.metric("Paid customers", f"{paid_customers:,.0f}")
    c3.metric("Paid CAC", money(paid_cac))
    c4.metric("Paid ROAS", ratio(paid_roas))
    c5.metric("All-channel customers", f"{all_customers:,.0f}")

    st.markdown("### Paid acquisition readout")
    left, right = st.columns([1, 1])
    with left:
        fig = px.bar(
            paid_channel_summary.sort_values("cac"),
            x="channel",
            y="cac",
            text_auto=".0f",
            title="Customer acquisition cost",
        )
        fig.update_layout(height=330, xaxis_title=None, yaxis_title="CAC (€)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.bar(
            paid_channel_summary.sort_values("roas", ascending=False),
            x="channel",
            y="roas",
            text_auto=".2f",
            title="Return on ad spend",
        )
        fig.update_layout(height=330, xaxis_title=None, yaxis_title="ROAS", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### What should happen next?")
    compact_campaign_table(paid)

    scale_count = int((paid["decision"] == "SCALE").sum())
    iterate_count = int((paid["decision"] == "ITERATE").sum())
    stop_count = int((paid["decision"] == "STOP").sum())

    q1, q2, q3 = st.columns(3)
    q1.markdown(
        f"""
        <div class="mini-card">
        <div class="eyebrow">Scale</div>
        <h4>{scale_count} paid test(s)</h4>
        Increase gradually only where CAC and downstream conversion remain healthy.
        </div>
        """,
        unsafe_allow_html=True,
    )
    q2.markdown(
        f"""
        <div class="mini-card">
        <div class="eyebrow">Iterate</div>
        <h4>{iterate_count} paid test(s)</h4>
        Keep the learning, fix the constraint, then retest before increasing budget.
        </div>
        """,
        unsafe_allow_html=True,
    )
    q3.markdown(
        f"""
        <div class="mini-card">
        <div class="eyebrow">Stop</div>
        <h4>{stop_count} paid test(s)</h4>
        Do not spend through weak economics just to keep a campaign active.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Measurement essentials"):
        st.markdown(
            "The minimum useful journey is **source → landing → booking start → booking complete → "
            "appointment complete → repeat booking**."
        )
        st.dataframe(pd.DataFrame(KPI_GLOSSARY), use_container_width=True, hide_index=True)
        st.caption(
            "The fuller proposed event taxonomy and implementation notes remain in the repository, "
            "but they are supporting detail rather than a separate recruiter-facing page."
        )


elif page == "Acquisition & campaigns":
    st.subheader("Acquisition & campaigns")
    st.caption(
        "The goal is not to be active on every channel. Start with a small number of testable acquisition motions."
    )

    p1, p2, p3 = st.columns(3)
    p1.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">1 — Capture intent</div>
        <h4>Google Search</h4>
        Match high-intent treatment searches to the exact service page and measure completed bookings.
        </div>
        """,
        unsafe_allow_html=True,
    )
    p2.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">2 — Create demand</div>
        <h4>Meta + organic social</h4>
        Test experience-led creative, one clear offer and one landing destination; judge it on commercial intent.
        </div>
        """,
        unsafe_allow_html=True,
    )
    p3.markdown(
        """
        <div class="mini-card">
        <div class="eyebrow">3 — Compound trust</div>
        <h4>SEO + referrals + partners</h4>
        Turn search intent, existing customers and local trust into trackable acquisition paths.
        </div>
        """,
        unsafe_allow_html=True,
    )

    paid_tab, organic_tab, partner_tab = st.tabs(
        ["Paid acquisition", "Organic & social", "Referrals & partnerships"]
    )

    with paid_tab:
        paid_options = {
            "Google Search — high-intent treatment": CAMPAIGN_BLUEPRINTS["High-intent treatment search"],
            "Meta — signature package demand": CAMPAIGN_BLUEPRINTS["Signature package demand"],
        }
        selected = st.selectbox("Choose a campaign hypothesis", list(paid_options))
        blueprint = paid_options[selected]

        c1, c2 = st.columns([1.1, 1])
        with c1:
            st.markdown(
                f"""
                **Audience**  
                {blueprint['audience']}

                **Message / creative**  
                {blueprint['message']}  
                {blueprint['creative']}

                **Landing experience**  
                {blueprint['landing']}
                """
            )
        with c2:
            st.markdown(
                f"""
                **Primary metric**  
                {blueprint['primary_metric']}

                **Guardrail**  
                {blueprint['guardrail']}

                **Follow-up**  
                {blueprint['follow_up']}
                """
            )

        playbook = PAID_MEDIA_PLAYBOOKS[blueprint["channel"]]
        with st.expander(f"{blueprint['channel']} execution details"):
            st.markdown(
                f"""
                **Campaign structure:** {playbook['structure']}

                **Example intent / creative themes:** {playbook['examples']}

                **Landing-page requirement:** {playbook['landing']}

                **Measurement chain:** {playbook['measurement']}
                """
            )

        st.markdown("#### Test the economics")
        i1, i2, i3, i4 = st.columns(4)
        spend = i1.number_input("Spend (€)", min_value=0.0, value=400.0, step=25.0)
        leads = i2.number_input("Leads / booking starts", min_value=0, value=50, step=5)
        customers = i3.number_input("Customers / bookings", min_value=0, value=12, step=1)
        revenue = i4.number_input("Revenue (€)", min_value=0.0, value=1500.0, step=50.0)

        lead_to_customer = customers / leads if leads else float("nan")
        cac = spend / customers if customers else float("nan")
        roas = revenue / spend if spend else float("nan")
        decision = recommend_decision(
            spend=float(spend),
            customers=float(customers),
            roas=float(roas),
            lead_to_customer=float(lead_to_customer),
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("CAC", money(cac))
        m2.metric("Lead → customer", percent(lead_to_customer))
        m3.metric("ROAS", ratio(roas))
        m4.metric("Decision", decision)

    with organic_tab:
        st.markdown("#### Organic social: three content tests, not a posting calendar")
        st.dataframe(
            pd.DataFrame(SOCIAL_CONTENT_PLAYS),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### SEO: prioritise commercial intent")
        seo_display = pd.DataFrame(SEO_OPPORTUNITIES)[
            ["search_intent", "intent", "content_action", "conversion"]
        ]
        st.dataframe(seo_display, use_container_width=True, hide_index=True)

        st.info(
            "The shared rule for SEO and social is the same: content earns continued effort only when it creates "
            "qualified site activity, booking intent or customers — not because it generated views alone."
        )

    with partner_tab:
        st.markdown("#### Small, trackable trust channels")
        st.dataframe(
            pd.DataFrame(PARTNERSHIP_HYPOTHESES),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "Each test should use a tagged link, referral code or partner-specific path so it can be evaluated like any other acquisition source."
        )


elif page == "Conversion & retention":
    st.subheader("Conversion & retention")
    st.caption(
        "Acquisition only matters if the visitor completes the next useful action and the customer has a reason to return."
    )

    conversion_tab, retention_tab = st.tabs(["Landing-page experiment", "CRM & retention"])

    with conversion_tab:
        st.markdown(
            """
            **Hypothesis:** a visitor with a specific treatment intent may convert better when the landing page keeps
            the treatment, expectations and booking CTA tightly aligned instead of forcing a generic journey.

            **Control:** current landing experience  
            **Variant:** intent-matched headline + trust information + booking CTA  
            **Primary metric:** completed booking  
            **Guardrails:** cancellation / no-show rate and lead quality
            """
        )

        a, b = st.columns(2)
        with a:
            st.markdown("#### Control")
            control_visitors = st.number_input("Control visitors", min_value=1, value=1000, step=50)
            control_conversions = st.number_input("Control bookings", min_value=0, value=120, step=5)
        with b:
            st.markdown("#### Variant")
            variant_visitors = st.number_input("Variant visitors", min_value=1, value=1000, step=50)
            variant_conversions = st.number_input("Variant bookings", min_value=0, value=145, step=5)

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
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Control CVR", percent(result["control_rate"]))
            r2.metric("Variant CVR", percent(result["variant_rate"]))
            r3.metric("Absolute change", f"{result['absolute_change'] * 100:+.2f} pp")
            r4.metric("Relative uplift", percent(result["relative_uplift"]))

            st.caption(
                "This is a descriptive readout, not an automatic significance claim. "
                "A real experiment should be sized and interpreted with duration, traffic quality and guardrails."
            )

        st.markdown("#### What gets tested on the page?")
        x1, x2, x3 = st.columns(3)
        x1.markdown("**Message match**")
        x1.write("Does the page immediately match the ad/search intent?")
        x2.markdown("**Trust / uncertainty**")
        x2.write("Does the visitor have enough information to take the next step?")
        x3.markdown("**Primary CTA**")
        x3.write("Is there one obvious booking action without unnecessary friction?")

    with retention_tab:
        st.markdown("#### Behaviour-based lifecycle")
        st.dataframe(
            pd.DataFrame(LIFECYCLE_STAGES),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Example operating flow")
        st.code(
            "Completed appointment → thank-you / feedback → relevant next step → "
            "repeat booking → suppress reactivation sequence",
            language=None,
        )

        st.markdown(
            """
            **CRM rule:** trigger messages from customer behaviour, stop the sequence when the intended action is complete,
            and measure repeat booking / reactivation rather than email opens alone.
            """
        )


elif page == "30-day sprint":
    st.subheader("30-day sprint")
    st.caption(
        "The first month should establish a reliable learning loop: baseline → small tests → diagnosis → reallocation."
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

    st.markdown("### End-of-month founder readout")
    st.markdown(
        """
        By day 30, I would want a short operating record answering five questions:

        1. Which customer / offer / channel hypotheses were actually tested?
        2. What did each test cost and what converted?
        3. Where did the funnel lose customers?
        4. What should be scaled, iterated or stopped?
        5. Where should the next round of budget and attention go?
        """
    )

    with st.expander("Supporting measurement plan"):
        st.dataframe(
            pd.DataFrame(MEASUREMENT_PLAN)[["event", "meaning", "decision_use"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "This is a proposed measurement design, not a claim about Eden's current analytics implementation."
        )
