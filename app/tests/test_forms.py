from django.test import TestCase
from app.forms import ReviewForm


class TestReviewForm(TestCase):
    def test_valid_form(self):
        form = ReviewForm(data={
            'review': "This is a valid review",
            'overall': '5'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_review(self):
        form = ReviewForm(data={
            'review': None,
            'overall': "5"
        })
        self.assertFalse(form.is_valid())

    def test_invalid_overall_none(self):
        form = ReviewForm(data={
            'review': "This is a valid review",
            'overall': None
        })
        self.assertFalse(form.is_valid())

    def test_invalid_overall_character(self):
        form = ReviewForm(data={
            'review': "This is a valid review",
            'overall': "a"
        })
        self.assertFalse(form.is_valid())

    def test_invalid_overall_upper_bound(self):
        form = ReviewForm(data={
            'review': "This is a valid review",
            'overall': "6"
        })
        self.assertFalse(form.is_valid())

    def test_invalid_overall_lower_bound(self):
        form = ReviewForm(data={
            'review': "This is a valid review",
            'overall': "-1"
        })
        self.assertFalse(form.is_valid())
