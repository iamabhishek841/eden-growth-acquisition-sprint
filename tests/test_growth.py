import math

import pandas as pd
import pytest

from src.growth import (
    ab_test_summary,
    aggregate_channels,
    enrich_campaign_metrics,
    recommend_decision,
)


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "campaign": "A",
                "channel": "Google Search",
                "objective": "Bookings",
                "spend": 100.0,
                "impressions": 1000,
                "clicks": 100,
                "leads": 20,
                "customers": 10,
                "revenue": 400.0,
                "repeat_customers": 2,
            }
        ]
    )


def test_enrich_campaign_metrics_calculates_unit_economics():
    result = enrich_campaign_metrics(sample_frame()).iloc[0]

    assert result["ctr"] == pytest.approx(0.10)
    assert result["cpl"] == pytest.approx(5.0)
    assert result["cac"] == pytest.approx(10.0)
    assert result["roas"] == pytest.approx(4.0)
    assert result["lead_to_customer"] == pytest.approx(0.5)
    assert result["decision"] == "SCALE"


def test_aggregate_channels_recalculates_ratios_after_summing():
    df = pd.concat([sample_frame(), sample_frame()], ignore_index=True)
    result = aggregate_channels(df).iloc[0]

    assert result["spend"] == 200
    assert result["customers"] == 20
    assert result["cac"] == pytest.approx(10.0)
    assert result["roas"] == pytest.approx(4.0)


def test_decision_engine_marks_no_spend_rows_for_measurement():
    assert (
        recommend_decision(
            spend=0,
            customers=12,
            roas=math.nan,
            lead_to_customer=0.30,
        )
        == "MEASURE"
    )


def test_ab_summary_reports_relative_uplift_not_percentage_points():
    result = ab_test_summary(1000, 100, 1000, 120)

    assert result["control_rate"] == pytest.approx(0.10)
    assert result["variant_rate"] == pytest.approx(0.12)
    assert result["absolute_change"] == pytest.approx(0.02)
    assert result["relative_uplift"] == pytest.approx(0.20)


def test_ab_summary_rejects_impossible_counts():
    with pytest.raises(ValueError):
        ab_test_summary(100, 101, 100, 10)
