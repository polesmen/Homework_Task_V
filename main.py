class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.transactions = []

    def add_transaction(self, transaction_data):
        self.transactions.append(transaction_data)


class ShippingService:
    def __init__(self):
        # Shipping price depends on package size and a provider:
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
        if user.user_id not in self.user_monthly_discounts:
            self.user_monthly_discounts[user.user_id] = {}
        if month not in self.user_monthly_discounts[user.user_id]:
            self.user_monthly_discounts[user.user_id][month] = 0

        discount = 0
        # The third L shipment via LP should be free, but only once a calendar month.
        if transaction['size'] == 'L' and transaction['carrier'] == 'LP':
            l_lp_transactions = [t for t in user.transactions if
                                 t['date'][:7] == month and t['size'] == 'L' and t['carrier'] == 'LP']
            if len(l_lp_transactions) == 3:
                discount = min(original_price, 10 - self.user_monthly_discounts[user.user_id][month])

        # Accumulated discounts cannot exceed 10 € in a calendar month. If there are not
        # enough funds to fully cover a discount this calendar month, it should be covered
        # partially.
        if transaction['size'] == 'S':
            potential_discount = original_price - self.lowest_s_price
            adjusted_discount = min(potential_discount,
                                    10 - self.user_monthly_discounts[user.user_id][month] - discount)
            discount += adjusted_discount

        # Total discount per month
        self.user_monthly_discounts[user.user_id][month] += discount
        return discount


class TransactionReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_transactions(self):
        transactions = []
        with open(self.file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                transactions.append(parts)
        return transactions



def main():
    user = User('user123')
    shipping_service = ShippingService()
    transaction_reader = TransactionReader('input.txt')

    transaction_parts = transaction_reader.read_transactions()

    with open('output.txt', 'w') as f:
        for parts in transaction_parts:
            output_line = ''
            if len(parts) != 3 or (parts[1], parts[2]) not in shipping_service.prices:
                output_line = f"{' '.join(parts)} Ignored"
            else:
                transaction = {'date': parts[0], 'size': parts[1], 'carrier': parts[2]}
                user.add_transaction(transaction)
                cost, discount = shipping_service.calculate_shipping_cost(user, transaction)
                output_line = f"{transaction['date']} {transaction['size']} {transaction['carrier']} {cost:.2f} {'-' if discount == 0 else f'{discount:.2f}'}"

            f.write(output_line + '\n')
            print(output_line)




if __name__ == "__main__":
    main()
