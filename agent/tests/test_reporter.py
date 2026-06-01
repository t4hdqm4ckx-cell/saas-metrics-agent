"""Tests for reporter.py — narrative generation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import json
from reporter import monthly_report, revenue_narrative, churn_narrative, unit_economics_narrative

with open(os.path.join(os.path.dirname(__file__), '../../data/synthetic_data.json')) as f:
    DATA = json.load(f)
MONTHS = DATA['months']


def test_monthly_report_has_all_sections():
    r = monthly_report(MONTHS)
    for key in ['month', 'revenue', 'churn', 'engagement', 'unit_economics', 'headline_kpis']:
        assert key in r, f"Missing section: {key}"


def test_revenue_narrative_mentions_mrr():
    n = revenue_narrative(MONTHS[-1], MONTHS[-2])
    assert 'MRR' in n or 'mrr' in n.lower()


def test_churn_narrative_contains_rate():
    n = churn_narrative(MONTHS[-1], MONTHS[-2])
    assert '%' in n or 'churn' in n.lower()


def test_unit_economics_narrative_contains_ltv_cac():
    n = unit_economics_narrative(MONTHS[-1])
    assert 'LTV' in n or 'CAC' in n


def test_monthly_report_month_is_correct():
    r = monthly_report(MONTHS)
    assert r['month'] == '2026-05'


def test_monthly_report_empty_returns_empty():
    assert monthly_report([]) == {}


if __name__ == '__main__':
    tests = [test_monthly_report_has_all_sections, test_revenue_narrative_mentions_mrr,
             test_churn_narrative_contains_rate, test_unit_economics_narrative_contains_ltv_cac,
             test_monthly_report_month_is_correct, test_monthly_report_empty_returns_empty]
    passed = 0
    for t in tests:
        try:
            t(); print(f"  ✓ {t.__name__}"); passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
