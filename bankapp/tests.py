from django.test import TestCase, Client
from django.urls import reverse
from bankapp.models import reg, Transaction


class RegModelTests(TestCase):
    def setUp(self):
        self.user = reg.objects.create(
            accno=1234567890,
            name="Test User",
            amount=5000,
            address="Test Address",
            mobileno="9876543210"
        )
        self.user.set_password("testpass123")
        self.user.save()

    def test_password_hashing(self):
        self.assertTrue(self.user.verify_password("testpass123"))
        self.assertFalse(self.user.verify_password("wrongpass"))

    def test_account_creation(self):
        self.assertEqual(str(self.user), "Test User - 1234567890")

    def test_transaction_creation(self):
        tx = Transaction.objects.create(
            account=self.user,
            transaction_type='DEPOSIT',
            amount=1000,
            balance_after=6000,
            description="Test deposit"
        )
        self.assertEqual(str(tx), "DEPOSIT - 1000 - 1234567890")


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = reg.objects.create(
            accno=1111111111,
            name="Alice",
            amount=10000,
            address="Street 1",
            mobileno="9999999999"
        )
        self.user.set_password("alice123")
        self.user.save()

        self.target = reg.objects.create(
            accno=2222222222,
            name="Bob",
            amount=5000,
            address="Street 2",
            mobileno="8888888888"
        )
        self.target.set_password("bob123")
        self.target.save()

    def test_homepage(self):
        response = self.client.get(reverse('homev'))
        self.assertEqual(response.status_code, 200)

    def test_balance_enquiry_valid(self):
        response = self.client.post(reverse('balv'), {
            'accno': '1111111111',
            'password': 'alice123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10000")

    def test_balance_enquiry_invalid_password(self):
        response = self.client.post(reverse('balv'), {
            'accno': '1111111111',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Invalid password" in str(m) for m in messages))

    def test_transfer_success(self):
        response = self.client.post(reverse('transv'), {
            'accno': '1111111111',
            'name': 'Alice',
            'password': 'alice123',
            'target_account': '2222222222',
            'amount': '2000'
        })
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.target.refresh_from_db()
        self.assertEqual(self.user.amount, 8000)
        self.assertEqual(self.target.amount, 7000)

    def test_transfer_same_account_blocked(self):
        response = self.client.post(reverse('transv'), {
            'accno': '1111111111',
            'name': 'Alice',
            'password': 'alice123',
            'target_account': '1111111111',
            'amount': '1000'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, "Cannot transfer to the same account.")

    def test_deactivated_account_blocked(self):
        self.user.active = False
        self.user.save()
        response = self.client.post(reverse('balv'), {
            'accno': '1111111111',
            'password': 'alice123'
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("deactivated" in str(m).lower() for m in messages))