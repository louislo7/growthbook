from functools import partial
from unittest import TestCase, main as unittest_main

import numpy as np
import pandas as pd

from gbstats.gbstats import (
    detect_unknown_variations,
    reduce_dimensionality,
    analyze_metric_df,
    get_metric_df,
)
from gbstats.shared.constants import StatsEngine

DECIMALS = 9
round_ = partial(np.round, decimals=DECIMALS)

MULTI_DIMENSION_STATISTICS_DF = pd.DataFrame(
    [
        {
            "dimension": "one",
            "variation": "one",
            "numerator_sum": 300,
            "numerator_sum_squares": 869,
            "users": 120,
            "count": 120,
        },
        {
            "dimension": "one",
            "variation": "zero",
            "numerator_sum": 270,
            "numerator_sum_squares": 848.79,
            "users": 100,
            "count": 100,
        },
        {
            "dimension": "two",
            "variation": "one",
            "numerator_sum": 770,
            "numerator_sum_squares": 3571,
            "users": 220,
            "count": 220,
        },
        {
            "dimension": "two",
            "variation": "zero",
            "numerator_sum": 740,
            "numerator_sum_squares": 3615.59,
            "users": 200,
            "count": 200,
        },
    ]
).assign(statistic_type="mean", numerator_type="count")

THIRD_DIMENSION_STATISTICS_DF = pd.DataFrame(
    [
        {
            "dimension": "three",
            "variation": "one",
            "numerator_sum": 222,
            "numerator_sum_squares": 555,
            "users": 3000,
            "count": 3000,
        },
        {
            "dimension": "three",
            "variation": "zero",
            "numerator_sum": 333,
            "numerator_sum_squares": 999,
            "users": 3001,
            "count": 3001,
        },
    ]
).assign(statistic_type="mean", numerator_type="count")

RATIO_STATISTICS_DF = pd.DataFrame(
    [
        {
            "dimension": "one",
            "variation": "one",
            "users": 120,
            "count": 120,
            "numerator_sum": 300,
            "numerator_sum_squares": 869,
            "denominator_sum": 500,
            "denominator_sum_squares": 800,
            "num_denom_sum_product": -905,
        },
        {
            "dimension": "one",
            "variation": "zero",
            "numerator_sum": 270,
            "users": 100,
            "count": 100,
            "numerator_sum_squares": 848.79,
            "denominator_sum": 510,
            "denominator_sum_squares": 810,
            "num_denom_sum_product": -900,
        },
    ]
).assign(statistic_type="ratio", numerator_type="count", denominator_type="count")


class TestDetectVariations(TestCase):
    def test_unknown_variations(self):
        rows = MULTI_DIMENSION_STATISTICS_DF
        self.assertEqual(detect_unknown_variations(rows, {"zero": 0, "one": 1}), set())
        self.assertEqual(
            detect_unknown_variations(rows, {"zero": 0, "hello": 1}), {"one"}
        )
        self.assertEqual(
            detect_unknown_variations(rows, {"hello": 0, "world": 1}), {"one", "zero"}
        )

    def test_multiple_exposures(self):
        rows = pd.concat(
            [
                MULTI_DIMENSION_STATISTICS_DF,
                pd.DataFrame(
                    [
                        {
                            "dimension": "All",
                            "variation": "__multiple__",
                            "numerator_sum": 99,
                            "numerator_sum_squares": 9999,
                            "users": 500,
                        }
                    ]
                ),
            ]
        )
        self.assertEqual(detect_unknown_variations(rows, {"zero": 0, "one": 1}), set())
        self.assertEqual(
            detect_unknown_variations(rows, {"zero": 0, "one": 1}, {"some_other"}),
            {"__multiple__"},
        )


class TestReduceDimensionality(TestCase):
    def test_reduce_dimensionality(self):
        rows = pd.concat([MULTI_DIMENSION_STATISTICS_DF, THIRD_DIMENSION_STATISTICS_DF])
        df = get_metric_df(
            rows,
            {"zero": 0, "one": 1},
            ["zero", "one"],
        )
        print(df)
        reduced = reduce_dimensionality(df, 3)
        self.assertEqual(len(reduced.index), 3)
        self.assertEqual(reduced.at[0, "dimension"], "three")
        self.assertEqual(reduced.at[0, "v1_numerator_sum"], 222)

        reduced = reduce_dimensionality(df, 2)
        self.assertEqual(len(reduced.index), 2)
        self.assertEqual(reduced.at[1, "dimension"], "(other)")
        self.assertEqual(reduced.at[1, "total_users"], 640)
        self.assertEqual(reduced.at[1, "v1_numerator_sum"], 1070)
        self.assertEqual(reduced.at[1, "v1_numerator_sum_squares"], 4440)
        self.assertEqual(reduced.at[1, "v1_users"], 340)
        self.assertEqual(reduced.at[1, "baseline_users"], 300)
        self.assertEqual(reduced.at[1, "baseline_numerator_sum"], 1010)
        self.assertEqual(reduced.at[1, "baseline_numerator_sum_squares"], 4464.38)


class TestAnalyzeMetricDfBayesian(TestCase):
    # New usage (no mean/stddev correction)
    def test_get_metric_df_new(self):
        rows = MULTI_DIMENSION_STATISTICS_DF
        df = get_metric_df(rows, {"zero": 0, "one": 1}, ["zero", "one"])
        result = analyze_metric_df(df, [0.5, 0.5])

        self.assertEqual(len(result.index), 2)
        self.assertEqual(result.at[0, "dimension"], "one")
        self.assertEqual(round_(result.at[0, "baseline_cr"]), 2.7)
        self.assertEqual(round_(result.at[0, "baseline_risk"]), 0.0021006)
        self.assertEqual(round_(result.at[0, "v1_cr"]), 2.5)
        self.assertEqual(round_(result.at[0, "v1_risk"]), 0.0821006)
        self.assertEqual(round_(result.at[0, "v1_expected"]), -0.074074074)
        self.assertEqual(round_(result.at[0, "v1_prob_beat_baseline"]), 0.079755378)
        self.assertEqual(result.at[0, "v1_p_value"], None)

    def test_get_metric_df_bayesian_ratio(self):
        rows = RATIO_STATISTICS_DF
        df = get_metric_df(rows, {"zero": 0, "one": 1}, ["zero", "one"])
        result = analyze_metric_df(df=df, weights=[0.5, 0.5], inverse=False)

        self.assertEqual(len(result.index), 1)
        self.assertEqual(result.at[0, "dimension"], "one")
        self.assertEqual(round_(result.at[0, "baseline_cr"]), 0.529411765)
        self.assertEqual(round_(result.at[0, "baseline_risk"]), 0.157756864)
        self.assertEqual(round_(result.at[0, "v1_cr"]), 0.6)
        self.assertEqual(round_(result.at[0, "v1_risk"]), 0.040109805)
        self.assertEqual(round_(result.at[0, "v1_expected"]), 0.133333333)
        self.assertEqual(round_(result.at[0, "v1_prob_beat_baseline"]), 0.706241155)
        self.assertEqual(result.at[0, "v1_p_value"], None)

    def test_get_metric_df_inverse(self):
        rows = MULTI_DIMENSION_STATISTICS_DF
        df = get_metric_df(rows, {"zero": 0, "one": 1}, ["zero", "one"])
        result = analyze_metric_df(df, [0.5, 0.5], inverse=True)

        self.assertEqual(len(result.index), 2)
        self.assertEqual(result.at[0, "dimension"], "one")
        self.assertEqual(round_(result.at[0, "baseline_cr"]), 2.7)
        self.assertEqual(round_(result.at[0, "baseline_risk"]), 0.0821006)
        self.assertEqual(round_(result.at[0, "v1_cr"]), 2.5)
        self.assertEqual(round_(result.at[0, "v1_risk"]), 0.0021006)
        self.assertEqual(round_(result.at[0, "v1_expected"]), -0.074074074)
        self.assertEqual(round_(result.at[0, "v1_prob_beat_baseline"]), 1 - 0.079755378)
        self.assertEqual(result.at[0, "v1_p_value"], None)


class TestAnalyzeMetricDfFrequentist(TestCase):
    def test_get_metric_df_frequentist(self):
        rows = MULTI_DIMENSION_STATISTICS_DF
        df = get_metric_df(
            rows,
            {"zero": 0, "one": 1},
            ["zero", "one"],
        )
        result = analyze_metric_df(
            df=df, weights=[0.5, 0.5], inverse=False, engine=StatsEngine.FREQUENTIST
        )

        self.assertEqual(len(result.index), 2)
        self.assertEqual(result.at[0, "dimension"], "one")
        self.assertEqual(round_(result.at[0, "baseline_cr"]), 2.7)
        self.assertEqual(result.at[0, "baseline_risk"], None)
        self.assertEqual(round_(result.at[0, "v1_cr"]), 2.5)
        self.assertEqual(result.at[0, "v1_risk"], None)
        self.assertEqual(round_(result.at[0, "v1_expected"]), -0.074074074)
        self.assertEqual(result.at[0, "v1_prob_beat_baseline"], None)
        self.assertEqual(round_(result.at[0, "v1_p_value"]), 0.163302082)

    def test_get_metric_df_frequentist_ratio(self):
        rows = RATIO_STATISTICS_DF
        df = get_metric_df(rows, {"zero": 0, "one": 1}, ["zero", "one"])
        result = analyze_metric_df(
            df=df, weights=[0.5, 0.5], inverse=False, engine=StatsEngine.FREQUENTIST
        )

        self.assertEqual(len(result.index), 1)
        self.assertEqual(result.at[0, "dimension"], "one")
        self.assertEqual(round_(result.at[0, "baseline_cr"]), 0.529411765)
        self.assertEqual(result.at[0, "baseline_risk"], None)
        self.assertEqual(round_(result.at[0, "v1_cr"]), 0.6)
        self.assertEqual(result.at[0, "v1_risk"], None)
        self.assertEqual(round_(result.at[0, "v1_expected"]), 0.133333333)
        self.assertEqual(result.at[0, "v1_prob_beat_baseline"], None)
        self.assertEqual(round_(result.at[0, "v1_p_value"]), 0.587981919)


if __name__ == "__main__":
    unittest_main()
