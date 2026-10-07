from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.growth import aggregate_channels, enrich_campaign_metrics


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
      .block-container {padding-top: 1.7rem; padding-bottom: 2.5rem; max-width: 1400px;}
      .hero {
        padding: 1.4rem 1.5rem;
        border: 1px solid #dbe7e2;
        border-radius: 18px;
        background: linear-gradient(135deg, #f7fbf9 0%, #eef6f2 100%);
        margin-bottom: 1.1rem;
      }
      .hero h1 {margin: 0 0 .35rem 0; font-size: 2.25rem;}
      .hero p {margin: 0; color: #48615b; font-size: 1.02rem;}
      .note {
        padding: .8rem 1rem;
        border-left: 4px solid #1D6F64;
        background: #f1f6f4;
        border-radius: 8px;
      }
      div[data-testid="stMetric"] {
        border: 1px solid #dfe9e5;
        background: white;
        padding: .75rem;
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
    return f"€{value:,.0f}"


def ratio(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.2f}x"


def percent(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:.1%}"


st.markdown(
    """
    <div class="hero">
      <h1>Eden Growth Acquisition Sprint</h1>
      <p>
        A founder-ready operating prototype for deciding what to test, what it
        cost, what converted, and what to scale next.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note">
      <b>Independent portfolio case study.</b> Public Eden Therapy Clinic
      information is used only for business context. Campaign, lead, customer
      and revenue numbers in this app are synthetic demonstration data and are
      not Eden results or forecasts.
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Growth workspace",
    [
        "Growth command centre",
        "Acquisition channels",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Demo mode: replace the bundled synthetic CSV with a real campaign export "
    "when first-party data is available."
)


def upload_or_demo() -> tuple[pd.DataFrame, str]:
    uploaded = st.file_uploader(
        "Optional: upload campaign CSV",
        type=["csv"],
        help=(
            "Required columns: campaign, channel, objective, spend, impressions, "
            "clicks, leads, customers, revenue, repeat_customers."
        ),
    )
    if uploaded is None:
        return load_demo(), "Synthetic demo dataset"
    return pd.read_csv(uploaded), "Uploaded dataset"


if page == "Growth command centre":
    st.subheader("Growth command centre")
    st.caption(
        "One view from acquisition spend to customers and revenue. "
        "The point is not more reporting; it is faster commercial decisions."
    )

    raw, source_label = upload_or_demo()

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
    paid_cac = paid["spend"].sum() / paid["customers"].sum()
    paid_roas = paid["revenue"].sum() / paid["spend"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Spend", money(total_spend))
    c2.metric("Leads", f"{total_leads:,.0f}")
    c3.metric("Customers", f"{total_customers:,.0f}")
    c4.metric("Paid CAC", money(paid_cac))
    c5.metric("Paid ROAS", ratio(paid_roas))

    st.markdown("### What should the founder do next?")

    decisions = (
        enriched.groupby("decision", as_index=False)
        .agg(campaigns=("campaign", "count"), revenue=("revenue", "sum"))
    )
    d1, d2 = st.columns([1.2, 1])

    with d1:
        decision_fig = px.bar(
            decisions,
            x="decision",
            y="campaigns",
            text="campaigns",
            title="Campaigns by recommended action",
        )
        decision_fig.update_layout(showlegend=False, height=330)
        st.plotly_chart(decision_fig, use_container_width=True)

    with d2:
        st.markdown(
            """
            **Decision logic is intentionally transparent**
            
            - **SCALE** — strong paid ROAS and strong lead-to-customer conversion.
            - **ITERATE** — promising but not yet strong enough to scale.
            - **STOP** — weak economics or weak conversion.
            - **MEASURE** — organic/no-spend activity where paid-media ROAS is not meaningful.
            
            These are demonstration rules, not a claim about Eden's commercial thresholds.
            """
        )

    st.markdown("### Campaign decision table")

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
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )

elif page == "Acquisition channels":
    st.subheader("Acquisition channels")
    st.caption(
        "Compare channels on downstream customer economics, not clicks alone."
    )

    raw, source_label = upload_or_demo()

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
            title="Paid-channel customer acquisition cost",
        )
        cac_fig.update_layout(height=390, xaxis_title=None, yaxis_title="CAC (€)")
        st.plotly_chart(cac_fig, use_container_width=True)

    st.markdown("### Funnel quality by channel")
    channel_display = channels[
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
    ].copy()

    st.dataframe(
        channel_display.style.format(
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

    st.info(
        "A cheap click is not the goal. The useful question is whether the "
        "channel produces customers at acceptable acquisition economics and "
        "whether those customers return."
    )
