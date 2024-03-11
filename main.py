class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = []
        self.discounts = {}  # Используется для отслеживания скидок по месяцам

    def add_transaction(self, transaction_data):
        self.transactions.append(transaction_data)


class ShippingService:
    def __init__(self):
        self.prices = {
            ('S', 'LP'): 1.50,
            ('M', 'LP'): 4.90,
            ('L', 'LP'): 6.90,
            ('S', 'MR'): 2.00,
            ('M', 'MR'): 3.00,
            ('L', 'MR'): 4.00,
        }
        self.lowest_s_price = min(price for (size, _), price in self.prices.items() if size == 'S')
        self.user_monthly_discounts = {}

    def get_price(self, size, carrier):
        return self.prices.get((size, carrier), None)

    def calculate_shipping_cost(self, user, transaction):
        original_price = self.get_price(transaction['size'], transaction['carrier'])
        discount = self.calculate_discount(user, transaction, original_price)
        final_price = max(0, original_price - discount)
        return final_price, discount

    def calculate_discount(self, user, transaction, original_price):
        month = transaction['date'][:7]
        # Инициализация скидок пользователя за месяц
        if user.user_id not in self.user_monthly_discounts:
            self.user_monthly_discounts[user.user_id] = {}
        if month not in self.user_monthly_discounts[user.user_id]:
            self.user_monthly_discounts[user.user_id][month] = 0

        discount = 0
        if transaction['size'] == 'S' and original_price > self.lowest_s_price:
            discount = original_price - self.lowest_s_price
            # Ограничение скидки до 10 евро за месяц
            if self.user_monthly_discounts[user.user_id][month] + discount > 10:
                discount = max(0, 10 - self.user_monthly_discounts[user.user_id][month])

        self.user_monthly_discounts[user.user_id][month] += discount
        return discount


def read_transactions_from_file(file_path):
    transactions = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                transactions.append({
                    'date': parts[0],
                    'size': parts[1],
                    'carrier': parts[2]
                })
    return transactions


def main():
    user = User('user123')
    shipping_service = ShippingService()

    transactions = read_transactions_from_file('input.txt')

    with open('output.txt', 'w') as f:
        for transaction in transactions:
            if (transaction['size'], transaction['carrier']) not in shipping_service.prices:
                f.write(f"{transaction['date']} {transaction['size']} {transaction['carrier']} Ignored\n")
            else:
                user.add_transaction(transaction)
                cost, discount = shipping_service.calculate_shipping_cost(user, transaction)
                discount_output = f"{discount:.2f}" if discount > 0 else "-"
                f.write(f"{transaction['date']} {transaction['size']} {transaction['carrier']} {cost:.2f} {discount_output}\n")

if __name__ == "__main__":
    main()
