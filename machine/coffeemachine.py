'''
CoffeeMachine
'''

MAX_DECIMAL_PLACES = 2
COFFEE_PRICE = 3.14

# Error Messages
ERROR_MSG = {
    '01': '%s should be greater that Zero',
    '02': 'Sorry, you do not have enough money to buy',
    '03': 'Invalid Value for %s, should be a number greater than Zero',
    '04': 'Amount for %s (EUR) should not be more than %i decimal places, GIVEN = %s, ACCEPTABLE = e.g. 2.99, 3, 3.01',
    '05': 'Do not have the change, so cannot fulfil your order',
    'eur_inserted': 'Inserted Euros amount',
    'coffee_price': 'Price of Coffee',
}

# General Messages
WELCOME_MSG = 'Hi, I am alive and ready to help you to save the word by Offering Best Coffee of the Universe ...'
INPUT_MSG = 'Please pay the amount for your coffee (EUR), I will not keep the change :) = '
BYE_MSG = 'I am tired, need some rest and refill, see you later, keep saving the world'
PRICE_MSG = 'Price of Coffee is: %.2f (Eur)' % COFFEE_PRICE
NO_CHANGE_MSG = 'You Have paid the desired amount'
AMOUNT_TO_RETURN = 'AMOUNT to return is %.2f Cents'
EXIT = 'exit'
EUR = 'EUR'
CENTS = 'Cents'

# key=coin's value, value = No. of those coins available in machine.
# for example, '1: 50' means 50 coins of 1 cent value are available in the machine
COIN_DENOMINATIONS = {
    1: 50,
    2: 50,
    5: 50,
    10: 50,
    20: 50,
    50: 50,
    100: 50,
    200: 50,
}

# for example, '200: 2.0, EUR' means 200 cents = 2.0 euros
COINS_VALUE_REPRESENTATION = {
    200: (2.0, EUR),
    100: (1.0, EUR),
    50: (50, CENTS),
    20: (20, CENTS),
    10: (10, CENTS),
    5: (5, CENTS),
    2: (2, CENTS),
    1: (1, CENTS),
}

class CoffeeMachine:
    def __init__(self):
        self._init_properties()
        self._load_money_tray()
        self._load_coffee_price()
        self._calculate_total_money()
        self._start()

    def _init_properties(self):
        self._money_tray = None
        self._coffee_price = None
        self._payment = None
        self._change = None
        self._total_money = None


    def _load_money_tray(self):
        self._money_tray = {k: v for k, v in sorted(COIN_DENOMINATIONS.items(), reverse=True)}

    def _calculate_total_money(self):
        self._total_money = 0
        for k, v in self._money_tray.items():
            self._total_money = self._total_money + (k * v)

    def _load_coffee_price(self):
        self._coffee_price = COFFEE_PRICE

    def _start(self):
        self._show_welcome_message()
        self._start_serving()

    def _show_welcome_message(self):
        print(WELCOME_MSG)
        print(PRICE_MSG)

    def _start_serving(self):
        try:
            while True:
                self._payment = self._ready_to_take_user_payment()
                if self._payment:
                    change = self._return_coins(self._coffee_price, float(self._payment))
                    if change:
                        self._return_change(change)
                    else:
                        print(NO_CHANGE_MSG)
                else:
                    self._stop_serving()
                    break
        except Exception as e:
            print(e)


    def _ready_to_take_user_payment(self):
        inserted_amount = None
        try:
            while True:
                inserted_amount = input(INPUT_MSG)
                if inserted_amount == EXIT:
                    return False
                elif self._validate_input(eur_inserted=inserted_amount):
                    break
        except Exception as e:
            print(e)
        return inserted_amount

    def _validate_input(self, **kwargs):
        valid_decimal_places = None
        try:
            for key, value in kwargs.items():
                try:
                    valid_decimal_places = None
                    assert float(value) > 0, ERROR_MSG['01'] % ERROR_MSG[key]
                    assert float(value) >= self._coffee_price, ERROR_MSG['02']
                    assert (float(value) - self._coffee_price)*100 <= self._total_money, ERROR_MSG['05']
                    valid_decimal_places = self._decimal_places(MAX_DECIMAL_PLACES, key, float(value))
                except (TypeError, ValueError):
                    print(ERROR_MSG['03'] % ERROR_MSG[key])
                except AssertionError as e:
                    print(e)

        except Exception as e:
            print(e)
        return valid_decimal_places

    def _decimal_places(self, max_places, key, number):
        places = str(number)[::-1].find('.')
        if places <= max_places:
            return True
        else:
            raise Exception(ERROR_MSG['04'] % (ERROR_MSG[key], max_places, number))

    def _return_coins(self, coffee_price, eur_inserted):
        return_amount = []
        # convert the remaining into cents
        balance_amount = round((eur_inserted - coffee_price)*100)
        print(AMOUNT_TO_RETURN % balance_amount)

        if balance_amount > 0:
            for coin, quantity in self._money_tray.items():
                no_of_coins = 0
                quotient, remainder = divmod(balance_amount, coin)

                if remainder == 0:
                    no_of_coins = quotient
                    return_amount.append({'coin': COINS_VALUE_REPRESENTATION[coin][0], 'quantity': no_of_coins,
                                          'unit': COINS_VALUE_REPRESENTATION[coin][1]})
                    break
                else:
                    if quotient == 0:
                        continue
                    elif quotient <= quantity:
                        no_of_coins = quotient
                    elif quotient > quantity:
                        no_of_coins = quantity
                    return_amount.append({'coin': COINS_VALUE_REPRESENTATION[coin][0], 'quantity': no_of_coins,
                                          'unit': COINS_VALUE_REPRESENTATION[coin][1]})
                    balance_amount = balance_amount - (no_of_coins * coin)

        return return_amount

    def _return_change(self, change):
        print(change)

    def _stop_serving(self):
        print(BYE_MSG)
        self._init_properties()

if __name__ == '__main__':
    CoffeeMachine()