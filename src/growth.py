from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


REQUIRED_CAMPAIGN_COLUMNS = {
    "campaign",
    "channel",
    "objective",
    "spend",
    "impressions",
    "clicks",
    "leads",
    "customers",
    "revenue",
    "repeat_customers",
}


@dataclass(frozen=True)
class DecisionThresholds:
    """Transparent commercial rules used for synthetic/demo campaign triage."""

    scale_roas: float = 3.0
    scale_customer_rate: float = 0.25
    stop_roas: float = 1.2
    stop_customer_rate: float = 0.10


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Vectorised division that returns NaN where the denominator is zero."""

    denominator = denominator.replace(0, np.nan)
    return numerator / denominator


def validate_campaign_frame(df: pd.DataFrame) -> None:
    """Raise a helpful error when an uploaded campaign export is incomplete."""

    missing = REQUIRED_CAMPAIGN_COLUMNS.difference(df.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_text}")

    numeric_columns = [
        "spend",
        "impressions",
        "clicks",
        "leads",
        "customers",
        "revenue",
        "repeat_customers",
    ]
    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Campaign metrics cannot contain negative values.")


def enrich_campaign_metrics(
    df: pd.DataFrame,
    thresholds: DecisionThresholds | None = None,
) -> pd.DataFrame:
    """Add commercial acquisition metrics and a simple decision recommendation."""

    validate_campaign_frame(df)
    thresholds = thresholds or DecisionThresholds()
    out = df.copy()

    out["ctr"] = safe_divide(out["clicks"], out["impressions"])
    out["cpc"] = safe_divide(out["spend"], out["clicks"])
    out["lead_rate"] = safe_divide(out["leads"], out["clicks"])
    out["cpl"] = safe_divide(out["spend"], out["leads"])
    out["lead_to_customer"] = safe_divide(out["customers"], out["leads"])
    out["cac"] = safe_divide(out["spend"], out["customers"])
    out["roas"] = safe_divide(out["revenue"], out["spend"])
    out["repeat_rate"] = safe_divide(out["repeat_customers"], out["customers"])

    out["decision"] = [
        recommend_decision(
            spend=float(row.spend),
            customers=float(row.customers),
            roas=float(row.roas) if pd.notna(row.roas) else np.nan,
            lead_to_customer=float(row.lead_to_customer)
            if pd.notna(row.lead_to_customer)
            else np.nan,
            thresholds=thresholds,
        )
        for row in out.itertuples()
    ]

    return out


def recommend_decision(
    *,
    spend: float,
    customers: float,
    roas: float,
    lead_to_customer: float,
    thresholds: DecisionThresholds | None = None,
) -> str:
    """Return SCALE, ITERATE or STOP using explicit, inspectable rules.

    Organic/no-spend rows are marked MEASURE because paid-media ROAS is not
    meaningful when spend is zero.
    """

    thresholds = thresholds or DecisionThresholds()

    if spend <= 0:
        return "MEASURE"
    if customers <= 0:
        return "STOP"
    if (
        pd.notna(roas)
        and pd.notna(lead_to_customer)
        and roas >= thresholds.scale_roas
        and lead_to_customer >= thresholds.scale_customer_rate
    ):
        return "SCALE"
    if (
        (pd.notna(roas) and roas < thresholds.stop_roas)
        or (
            pd.notna(lead_to_customer)
            and lead_to_customer < thresholds.stop_customer_rate
        )
    ):
        return "STOP"
    return "ITERATE"


def aggregate_channels(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate raw campaign rows by channel before calculating ratios."""

    validate_campaign_frame(df)
    grouped = (
        df.groupby("channel", as_index=False)[
            [
                "spend",
                "impressions",
                "clicks",
                "leads",
                "customers",
                "revenue",
                "repeat_customers",
            ]
        ]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    grouped["ctr"] = safe_divide(grouped["clicks"], grouped["impressions"])
    grouped["cpl"] = safe_divide(grouped["spend"], grouped["leads"])
    grouped["lead_to_customer"] = safe_divide(
        grouped["customers"], grouped["leads"]
    )
    grouped["cac"] = safe_divide(grouped["spend"], grouped["customers"])
    grouped["roas"] = safe_divide(grouped["revenue"], grouped["spend"])
    grouped["repeat_rate"] = safe_divide(
        grouped["repeat_customers"], grouped["customers"]
    )
    return grouped


def ab_test_summary(
    control_visitors: int,
    control_conversions: int,
    variant_visitors: int,
    variant_conversions: int,
) -> dict[str, float]:
    """Return transparent conversion-rate and relative-uplift calculations.

    This is intentionally descriptive rather than a significance-test shortcut.
    A real experiment should be sized and interpreted using the experiment
    design, traffic quality and guardrails.
    """

    values: Iterable[int] = (
        control_visitors,
        control_conversions,
        variant_visitors,
        variant_conversions,
    )
    if any(value < 0 for value in values):
        raise ValueError("Experiment counts cannot be negative.")
    if control_visitors == 0 or variant_visitors == 0:
        raise ValueError("Both variants need at least one visitor.")
    if control_conversions > control_visitors:
        raise ValueError("Control conversions cannot exceed visitors.")
    if variant_conversions > variant_visitors:
        raise ValueError("Variant conversions cannot exceed visitors.")

    control_rate = control_conversions / control_visitors
    variant_rate = variant_conversions / variant_visitors
    relative_uplift = (
        (variant_rate - control_rate) / control_rate
        if control_rate > 0
        else np.nan
    )

    return {
        "control_rate": control_rate,
        "variant_rate": variant_rate,
        "absolute_change": variant_rate - control_rate,
        "relative_uplift": relative_uplift,
    }
