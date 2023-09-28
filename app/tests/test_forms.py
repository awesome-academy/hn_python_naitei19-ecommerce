from django.test import TestCase
from django_countries.fields import Country
from app.forms import CheckoutForm, ReviewForm


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

class CheckoutFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            'shipping_address': '123 Street',
            'shipping_address2': 'Apt 45',
            'shipping_country': 'VN',
            'shipping_zip': '12345',
            'billing_address': '456 Street',
            'billing_address2': 'Apt 67',
            'billing_country': 'VN',
            'billing_zip': '67890',
            'set_default_shipping': True,
            'set_default_billing': False,
            'payment_option': 'S',
        }

        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        # Test with missing required fields
        form_data = {
            'shipping_address': '', #require
            'shipping_address2': '',
            'shipping_country': 'VN', #require
            'shipping_zip': '12345', #require
            'billing_address': '',  #require
            'billing_address2': '',
            'billing_country': 'VN', #require
            'billing_zip': '67890', #require
            'payment_option': '', #require
        }

        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['shipping_address'], ['This field is required.'])
        self.assertEqual(form.errors['billing_address'], ['This field is required.'])
        self.assertEqual(form.errors['payment_option'], ['This field is required.'])
        self.assertEqual(len(form.errors), 3)  # There should be errors for two missing required fields

    def test_blank_fields(self):
        # Test with all fields blank
        form_data = {}
        form = CheckoutForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['shipping_address'], ['This field is required.'])
        self.assertEqual(form.errors['shipping_country'], ['This field is required.'])
        self.assertEqual(form.errors['shipping_zip'], ['This field is required.'])
        self.assertEqual(form.errors['billing_address'], ['This field is required.'])
        self.assertEqual(form.errors['billing_country'], ['This field is required.'])
        self.assertEqual(form.errors['billing_zip'], ['This field is required.'])
        self.assertEqual(form.errors['payment_option'], ['This field is required.'])
        self.assertEqual(len(form.errors), 7)  # There should be errors for all required fields
