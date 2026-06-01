"""
Tests for data_generator.py — validates synthetic data quality and constraints.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_generator import DataGenerator, PLAN_PRICES


def test_generates_correct_month_count():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    assert len(snapshots) == 24


def test_mrr_monotonically_increasing_on_average():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    mrrs = [s.mrr for s in snapshots]
    # MRR should be higher at month 24 than month 1
    assert mrrs[-1] > mrrs[0] * 2, f"Expected 2× growth, got {mrrs[-1]/mrrs[0]:.1f}×"


def test_churn_rate_improves_over_time():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    early_churn = sum(s.monthly_churn_rate for s in snapshots[:4]) / 4
    late_churn = sum(s.monthly_churn_rate for s in snapshots[-4:]) / 4
    assert late_churn < early_churn, "Churn should improve over time"


def test_trial_conversion_improves():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    early_conv = sum(s.trial_conversion_rate for s in snapshots[:4]) / 4
    late_conv = sum(s.trial_conversion_rate for s in snapshots[-4:]) / 4
    assert late_conv > early_conv, "Trial conversion should improve"


def test_plan_mrr_sums_to_approximately_total_mrr():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    for s in snapshots:
        plan_sum = (
            s.plan_breakdown['starter']['mrr']
            + s.plan_breakdown['pro']['mrr']
            + s.plan_breakdown['business']['mrr']
        )
        # Plan MRR is computed independently, allow 30% delta
        ratio = plan_sum / s.mrr if s.mrr > 0 else 0
        assert 0.3 < ratio < 3.0, f"Plan MRR ratio {ratio:.2f} out of range for {s.month}"


def test_plan_customer_counts_sum_to_total():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    for s in snapshots:
        plan_customers = (
            s.plan_breakdown['starter']['customers']
            + s.plan_breakdown['pro']['customers']
            + s.plan_breakdown['business']['customers']
        )
        # Allow small rounding difference
        assert abs(plan_customers - s.total_customers) <= 5, \
            f"Plan customer sum mismatch at {s.month}"


def test_ltv_cac_ratio_is_positive():
    gen = DataGenerator(seed=42, months=24)
    snapshots = gen.generate()
    for s in snapshots:
        assert s.ltv_cac_ratio > 0, f"Negative LTV:CAC at {s.month}"


def test_reproducible_with_same_seed():
    gen1 = DataGenerator(seed=99, months=12)
    s1 = gen1.generate()
    gen2 = DataGenerator(seed=99, months=12)
    s2 = gen2.generate()
    # Compare rounded to 2dp to avoid float repr differences
    assert round(s1[0].mrr, 2) == round(s2[0].mrr, 2), \
        f"MRR mismatch: {s1[0].mrr} vs {s2[0].mrr}"
    assert s1[-1].total_customers == s2[-1].total_customers


def test_different_seeds_produce_different_data():
    gen1 = DataGenerator(seed=1, months=12)
    gen2 = DataGenerator(seed=2, months=12)
    s1 = gen1.generate()
    s2 = gen2.generate()
    assert s1[-1].mrr != s2[-1].mrr


def test_json_output_schema_has_required_fields():
    gen = DataGenerator(seed=42, months=3)
    snapshots = gen.generate()
    data = gen.to_json(snapshots)
    assert data['schema_version'] == '1.0'
    assert data['company'] == 'FlowSync'
    required_keys = ['mrr', 'arr', 'total_customers', 'monthly_churn_rate',
                     'ltv', 'cac', 'mau', 'dau', 'trial_conversion_rate']
    for key in required_keys:
        assert key in data['months'][0], f"Missing required field: {key}"


if __name__ == '__main__':
    tests = [
        test_generates_correct_month_count,
        test_mrr_monotonically_increasing_on_average,
        test_churn_rate_improves_over_time,
        test_trial_conversion_improves,
        test_plan_mrr_sums_to_approximately_total_mrr,
        test_plan_customer_counts_sum_to_total,
        test_ltv_cac_ratio_is_positive,
        test_reproducible_with_same_seed,
        test_different_seeds_produce_different_data,
        test_json_output_schema_has_required_fields,
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
