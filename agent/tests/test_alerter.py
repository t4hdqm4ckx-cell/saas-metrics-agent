"""Tests for alerter.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import json
from alerter import evaluate_alerts, alert_summary, ALERT_RULES

with open(os.path.join(os.path.dirname(__file__), '../../data/synthetic_data.json')) as f:
    DATA = json.load(f)
MONTHS = DATA['months']


def test_alerts_return_list():
    alerts = evaluate_alerts(MONTHS)
    assert isinstance(alerts, list)


def test_alert_summary_has_required_keys():
    s = alert_summary(MONTHS)
    for key in ['month', 'total_fired', 'by_severity', 'critical_count', 'high_count']:
        assert key in s


def test_no_critical_alerts_on_healthy_data():
    s = alert_summary(MONTHS)
    assert s['critical_count'] == 0, f"Unexpected critical alerts: {s['by_severity'].get('CRITICAL', [])}"


def test_nrr_alert_fires():
    # Our data has NRR below 100%, so NRR alert should fire
    alerts = evaluate_alerts(MONTHS)
    nrr_alerts = [a for a in alerts if a.metric == 'nrr']
    assert len(nrr_alerts) > 0, "NRR below 100% alert should fire given our data"


def test_empty_months_returns_no_alerts():
    assert evaluate_alerts([]) == []
    assert evaluate_alerts([MONTHS[0]]) == []


def test_all_rules_have_valid_operators():
    valid_ops = {'gt', 'lt', 'gte', 'lte'}
    for rule in ALERT_RULES:
        assert rule.operator in valid_ops, f"Invalid operator in rule {rule.id}: {rule.operator}"


def test_fired_alert_has_message():
    alerts = evaluate_alerts(MONTHS)
    for a in alerts:
        assert a.message, f"Empty message for alert {a.rule.id}"
        assert a.month == '2026-05'


if __name__ == '__main__':
    tests = [test_alerts_return_list, test_alert_summary_has_required_keys,
             test_no_critical_alerts_on_healthy_data, test_nrr_alert_fires,
             test_empty_months_returns_no_alerts, test_all_rules_have_valid_operators,
             test_fired_alert_has_message]
    passed = sum(1 for t in tests if (print(f"  {'✓' if (lambda: (t(), True)[1])() else '✗'} {t.__name__}") or True))
    # simpler runner:
    passed = 0
    for t in tests:
        try:
            t(); print(f"  ✓ {t.__name__}"); passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
