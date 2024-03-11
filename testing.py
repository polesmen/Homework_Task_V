import unittest
from main import User, ShippingService, TransactionReader

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User('user123')

    def test_add_transaction(self):
        self.user.add_transaction({'item': 'book', 'price': 15})
        self.assertEqual(len(self.user.transactions), 1)
        self.assertEqual(self.user.transactions[0], {'item': 'book', 'price': 15})

class TestShippingService(unittest.TestCase):
    def setUp(self):
        self.service = ShippingService()

    def test_get_price(self):
        self.assertEqual(self.service.get_price('S', 'LP'), 1.50)
        self.assertEqual(self.service.get_price('M', 'MR'), 3.00)
        self.assertIsNone(self.service.get_price('S', 'XYZ'))

    def test_calculate_discount(self):
        user = User('user123')
        # LP lower then S
        self.service.user_monthly_discounts[user.user_id] = {'2023-01': 0}
        transaction = {'date': '2023-01-01', 'size': 'S', 'carrier': 'MR'}
        self.assertEqual(self.service.calculate_discount(user, transaction, 2.00), 0.50)

    def test_calculate_shipping_cost(self):
        user = User('user123')
        transaction = {'date': '2023-01-02', 'size': 'S', 'carrier': 'LP'}
        final_price, discount = self.service.calculate_shipping_cost(user, transaction)
        self.assertEqual(final_price, 1.50)
        self.assertEqual(discount, 0.00)

class TestTransactionReader(unittest.TestCase):
    def setUp(self):
        # Test file
        self.reader = TransactionReader('/home/poles/PycharmProjects/Homework Task(V)/test_input.txt')

    def test_read_transactions(self):
        # For example in our file only 2 lines
        transactions = self.reader.read_transactions()
        self.assertEqual(len(transactions), 2)

if __name__ == '__main__':
    unittest.main()
