import unittest
import pandas as pd

from soccerlearn.tests.custom_assert_functions import assertFrameEqual
from soccerlearn.features.home_and_visitor_features import _get_local_team_id, _get_visitor_team_id, compute_home_and_visitor_features


class TestHomeAndVisitorFeatures(unittest.TestCase):

    def setUp(self):
        fixture_data = pd.DataFrame({
            'team_id': ['a', 'b', 'c', 'd'],
            'date': [1, 1, 2, 2],
            'local': [False, True, False, True],
            'opposite_team_id': ['b', 'a', 'd', 'c'],
        }).set_index(['team_id', 'date'])
        feature_data = pd.DataFrame({
            'team_id': ['a', 'b', 'c', 'd'],
            'date': [1, 1, 2, 2],
            'goals_scored': [10, 5, 10, 15],
        }).set_index(['team_id', 'date'])
        self.data = {
            'fixtures': fixture_data,
            'features': feature_data,
        }

    def test_compute_home_and_visitor_features(self):
        expected_output = pd.DataFrame({
            'date': [1, 2],
            'local_goals_scored': [5, 15],
            'visitor_goals_scored': [10, 10],
            'local_team_id': ['b', 'd'],
            'visitor_team_id': ['a', 'c'],
        }).set_index(['local_team_id', 'date'])
        output = compute_home_and_visitor_features(self.data)
        assertFrameEqual(output, expected_output)

    def test_local_team_id_happy_path(self):
        expected_output = pd.DataFrame({
            'team_id': ['a', 'b', 'c', 'd'],
            'date': [1, 1, 2, 2],
            'local_team_id': ['b', 'b', 'd', 'd'],
        }).set_index(['team_id', 'date'])
        output = _get_local_team_id(self.data['fixtures'])
        pd.testing.assert_frame_equal(output, expected_output)

    def test_visitor_team_id_happy_path(self):
        expected_output = pd.DataFrame({
            'team_id': ['a', 'b', 'c', 'd'],
            'date': [1, 1, 2, 2],
            'visitor_team_id': ['a', 'a', 'c', 'c'],
        }).set_index(['team_id', 'date'])
        output = _get_visitor_team_id(self.data['fixtures'])
        pd.testing.assert_frame_equal(output, expected_output)