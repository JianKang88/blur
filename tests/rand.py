from __future__ import division

import unittest
import math
import random

from .. import rand

"""
Tests for functions in the ``rand`` module.

Due to the stochastic nature of many of these functions,
this is not absolute proof that the functions are working as expected.
False failures, while highly unlikely, are possible.

If something fails and you aren't sure why, try re-running
the tests a few times before going bug-hunting.
"""

class TestRand(unittest.TestCase):
    def test__linear_interp(self):
        # Positive integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2)], 1, round_result=False),
            1)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2)], 1, round_result=True),
            1)
        # Negative integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(-2, -2), (0, 0)], -1, round_result=False),
            -1)
        self.assertAlmostEqual(
            rand._linear_interp([(-2, -2), (0, 0)], -1, round_result=True),
            -1)
        # Positive non-integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (4, 1)], 1, round_result=True),
            0)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (4, 1)], 1, round_result=False),
            0.25)
        # Negative non-integer slope with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(-4, -1), (0, 0)], -1, round_result=True),
            0)
        self.assertAlmostEqual(
            rand._linear_interp([(-4, -1), (0, 0)], -1, round_result=False),
            -0.25)
        # Three points in curve with and without rounding
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2), (18, 7)],
                                1, round_result=False), 1)
        self.assertAlmostEqual(
            rand._linear_interp([(0, 0), (2, 2), (18, 7)],
                                1, round_result=True), 1)
        # test_x out of the domain of the curve
        with self.assertRaises(rand.PointNotFoundError):
            rand._linear_interp([(0, 0), (2, 2)], -1, round_result=False)

    def test__point_under_curve(self):
        # Build several random curves and test points below the minimum
        # and above the maximum
        MIN_X = -100
        MIN_Y = -100
        MAX_X = 100
        MAX_Y = 100
        curve = [(random.randint(-100, 100), random.randint(-100, 100))
                 for i in range(30)]
        # Attach points to domain bounds at MIN_Y
        curve.append((MIN_X, MIN_Y))
        curve.append((MAX_X, MIN_Y))
        # Sort the points in the curve as this is a requirement of the function
        curve.sort(key=lambda p: p[0])

        # Point guaranteed to be under the random curve
        point_under = ((MIN_X + MAX_X) / 2, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(curve, point_under))
        # Point guaranteed to be over the random curve
        point_over = ((MIN_X + MAX_X) / 2, MAX_Y + 1)
        self.assertFalse(rand._point_under_curve(curve, point_over))
        # Points outside the x domain of the random curve
        point_out_of_lower_x_bound = (MIN_X - 1, MIN_Y - 1)
        self.assertFalse(rand._point_under_curve(
            curve, point_out_of_lower_x_bound))
        point_out_of_upper_x_bound = (MAX_X + 1, MIN_Y - 1)
        self.assertFalse(rand._point_under_curve(
            curve, point_out_of_upper_x_bound))
        # Points under the curve but on the curve bounds
        point_on_lower_x_bound = (MIN_X, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(
            curve, point_on_lower_x_bound))
        point_on_upper_x_bound = (MAX_X, MIN_Y - 1)
        self.assertTrue(rand._point_under_curve(
            curve, point_on_upper_x_bound))

    def test_normal_distribution(self):
        """
        Test the accuracy of ``rand.normal_distribution()``
        by using the curve it creates to generate a large number of samples,
        and then calculate the real variance and mean of the resulting
        sample group and compare the two within a comfortable margin.
        """
        MEAN = -12
        VARIANCE = 2.5
        STANDARD_DEVIATION = math.sqrt(VARIANCE)
        SAMPLE_COUNT = 200
        curve = rand.normal_distribution(MEAN, VARIANCE, 23)
        samples = [rand.weighted_rand(curve) for i in range(SAMPLE_COUNT)]
        samples_mean = sum(samples) / len(samples)
        samples_variance = (
            sum((s - samples_mean) ** 2 for s in samples) /
            len(samples)
        )
        mean_diff = abs(MEAN - samples_mean)
        variance_diff = abs(VARIANCE - samples_variance)
        self.assertLess(mean_diff, abs(MEAN / 5))
        self.assertLess(variance_diff, abs(VARIANCE / 5))

    def test_prob_bool(self):
        # Test guaranteed outcomes
        self.assertTrue(rand.prob_bool(100))
        self.assertTrue(rand.prob_bool(1))
        self.assertFalse(rand.prob_bool(0))
        self.assertFalse(rand.prob_bool(-100))
        # Test that probabilties are working as expected
        true_count = 0
        for i in range(1000):
            if rand.prob_bool(0.2):
                true_count += 1
        self.assertTrue(5 <= true_count <= 400)

    def test_percent_possible(self):
        # Test guaranteed outcomes
        self.assertTrue(rand.prob_bool(1000))
        self.assertTrue(rand.prob_bool(100))
        self.assertFalse(rand.prob_bool(0))
        self.assertFalse(rand.prob_bool(-1000))
        # Test that probabilties are working as expected
        true_count = 0
        for i in range(1000):
            if rand.percent_possible(20):
                true_count += 1
        self.assertTrue(5 <= true_count <= 400)

    def test_pos_or_neg_with_given_prob(self):
        # Test guaranteed outcomes
        self.assertEqual(rand.pos_or_neg(5, 10), 5)
        self.assertEqual(rand.pos_or_neg(5, 1), 5)
        self.assertEqual(rand.pos_or_neg(5, 0), -5)
        self.assertEqual(rand.pos_or_neg(5, -10), -5)
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg(5, 0.2) == 5:
                pos_count += 1
        self.assertTrue(5 <= pos_count <= 400)

    def test_pos_or_neg_without_given_prob(self):
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg(5) == 5:
                pos_count += 1
        self.assertTrue(300 <= pos_count <= 700)

    def test_pos_or_neg_1_with_given_prob(self):
        # Test guaranteed outcomes
        self.assertEqual(rand.pos_or_neg_1(10), 1)
        self.assertEqual(rand.pos_or_neg_1(1), 1)
        self.assertEqual(rand.pos_or_neg_1(0), -1)
        self.assertEqual(rand.pos_or_neg_1(-10), -1)
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg_1(0.2) == 1:
                pos_count += 1
        self.assertTrue(5 <= pos_count <= 400)

    def test_pos_or_neg_1_without_given_prob(self):
        # Test that probabilties are working as expected
        pos_count = 0
        for i in range(1000):
            if rand.pos_or_neg_1() == 1:
                pos_count += 1
        self.assertTrue(300 <= pos_count <= 700)

    def test_weighted_option(self):
        options = [(0, 1), (5, 2), (10, 5)]
        zero_count = 0
        five_count = 0
        ten_count = 0
        for i in range(1000):
            result = rand.weighted_option(options)
            if result == 0:
                zero_count += 1
            elif result == 5:
                five_count += 1
            elif result == 10:
                ten_count += 1
            else:
                self.fail('Unexpected weighted_option'
                          'result {0}'.format(result))
        self.assertTrue(25 <= zero_count <= 250)
        self.assertTrue(50 <= five_count <= 600)
        self.assertTrue(300 <= ten_count <= 900)

    def test_weighted_rand(self):
        """
        Test ``rand.weighted_rand()``  by finding a large number of
        points from a randomly built weight distribution and comparing the
        distribution against the expectation using a crude histogram model.
        """
        MIN_X = -1000
        MIN_Y = 0
        MAX_X = 1000
        MAX_Y = 1000
        curve = [(random.randint(MIN_X, MAX_X), random.randint(MIN_Y, MAX_Y))
                 for i in range(30)]
        # Attach points to domain bounds at MIN_Y
        curve.append((MIN_X, MIN_Y))
        curve.append((MAX_X, MIN_Y))
        # Sort the points in the curve as this is a
        # requirement of _linear_interp()
        curve.sort(key=lambda p: p[0])

        BIN_WIDTH = 1
        bins = {b: 0 for b in range(MIN_X, MAX_X, BIN_WIDTH)}
        TEST_COUNT = 1000
        for i in range(TEST_COUNT):
            point = rand.weighted_rand(curve, round_result=False)
            # Match the found point to the closest bin to the left
            bins[int(math.floor(point / BIN_WIDTH) * BIN_WIDTH)] += 1
        # Make sure the binning is working as expected
        self.assertEqual(sum(values for i, values in bins.items()), TEST_COUNT,
                         msg='This test itself is broken! '
                             'Not all rolled points were matched to a bin.')
        sum_probability = 0
        for bin_x in bins.keys():
            sum_probability += rand._linear_interp(curve, bin_x)
        for bin_x, count in bins.items():
            bin_probability = rand._linear_interp(curve, bin_x)
            expected_count = (bin_probability / sum_probability) * TEST_COUNT
            self.assertLess(abs(count - expected_count), TEST_COUNT / 10)

    def test_weighted_sort(self):
        # TODO: Build me
        pass
