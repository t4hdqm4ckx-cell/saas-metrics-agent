"""
Tests for metrics_calculator.py — validates KPI computation correctness.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import json

from data_generator import DataGenerator
from metrics_calculator import MetricsCalculator


def load_test_data():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    return gen.to_json(snapshots)


DATA = load_test_data()
CALC = MetricsCalculator(DATA)


def test_nrr_series_length():
    nrr = CALC.nrr_series()
    assert len(nrr) == 24


def test_nrr_first_month_is_100():
    nrr = CALC.nrr_series()
    assert nrr[0] == 100.0


def test_ltv_cac_series_has_no_negatives():
    series = CALC.ltv_cac_series()
    for item in series:
        if item['ratio'] is not None:
            assert item['ratio'] > 0, f"Negative LTV:CAC at {item['month']}"


def test_cohort_retention_matrix_dimensions():
    matrix = CALC.cohort_retention_matrix()
    assert len(matrix) == 12
    for row in matrix:
        assert len(row) == 12


def test_cohort_retention_month_0_is_close_to_1():
    matrix = CALC.cohort_retention_matrix()
    for row in matrix:
        if row[0] is not None:
            assert 0.85 <= row[0] <= 1.05, f"Month-0 retention should be ~1.0, got {row[0]}"


def test_waterfall_data_net_new_mrr_is_correct():
    wf = CALC.waterfall_data()
    for w in wf:
        expected = w['new_mrr'] + w['expansion_mrr'] + w['contraction_mrr'] + w['churned_mrr']
        assert abs(w['net_new_mrr'] - expected) < 0.01


def test_latest_snapshot_is_last_month():
    latest = CALC.latest_snapshot()
    assert latest['month'] == '2026-05'


def test_growth_summary_structure():
    summary = CALC.growth_summary()
    required = ['mrr_start', 'mrr_end', 'mrr_growth_total_pct',
                'customer_start', 'customer_end', 'avg_monthly_churn', 'avg_nrr']
    for key in required:
        assert key in summary, f"Missing key in growth_summary: {key}"


def test_growth_summary_mrr_grew():
    summary = CALC.growth_summary()
    assert summary['mrr_growth_total_pct'] > 100, "Expected >100% total MRR growth"


def test_zero_denominator_safe_div():
    calc = MetricsCalculator({'months': []})
    result = calc._safe_div(100, 0)
    assert result is None


if __name__ == '__main__':
    tests = [
        test_nrr_series_length,
        test_nrr_first_month_is_100,
        test_ltv_cac_series_has_no_negatives,
        test_cohort_retention_matrix_dimensions,
        test_cohort_retention_month_0_is_close_to_1,
        test_waterfall_data_net_new_mrr_is_correct,
        test_latest_snapshot_is_last_month,
        test_growth_summary_structure,
        test_growth_summary_mrr_grew,
        test_zero_denominator_safe_div,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
