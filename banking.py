# Write your code here
import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
drop_table_card = """
DROP TABLE IF EXISTS card;
"""
create_table_card = """
CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY autoincrement,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
    );
"""
# If you remove the comment, a new table will be generated each time.
# cur.execute(drop_table_card)
cur.execute(create_table_card)
conn.commit()
cur.execute('SELECT * FROM card')
for row in cur.fetchall():
    print(row)


class Account:
    def __init__(self):
        self.iin = 400000
        self.can = random.randint(1000000000, 9999999999)
        self.pin_code = random.randint(1000, 9999)
        self.full_number = int('{}{}'.format(self.iin, self.can))
        self.balance = 0

    def luhn(self):
        list_of_card_number = []
        for str_data in str(self.full_number):
            list_of_card_number.append(int(str_data))

        LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
        evens = sum(int(i) for i in list_of_card_number[-1::-2])
        odds = sum(LOOKUP[int(i)] for i in list_of_card_number[-2::-2])
        if (evens + odds) % 10 == 0:
            return 0
        else:
            return 1

    def create_ac_message(self):
        print("\nYour card has been created")
        print("Your card number:")
        print(self.full_number)
        print("Your card PIN:")
        print(self.pin_code)
        print()


while True:
    print(f"1. Create an account\n"
          f"2. Log into account\n"
          f"0. Exit")
    choices = int(input())

    if choices == 1:
        while True:
            new_account = Account()
            if new_account.luhn() == 0:
                cur.execute(f'INSERT INTO card(number,pin) VALUES({new_account.full_number}, {new_account.pin_code});')
                conn.commit()
                new_account.create_ac_message()
                break

    elif choices == 2:
        print("\nEnter your card number: ")
        login_number = int(input())
        if len(str(login_number)) != 16:
            continue
        print("Enter your PIN: ")
        login_pin_code = int(input())
        check_db_number = cur.execute(
            f'SELECT number, pin FROM card WHERE number={login_number} AND pin={login_pin_code};')
        control_data = cur.fetchone()
        if control_data is None or control_data[0] != str(login_number) and control_data[1] != str(login_pin_code):
            print("\nWrong card number or PIN!")
            continue
        print("\nYou have successfully logged in!\n")
        while True:
            print(f"1. Balance\n"
                  f"2. Add income\n"
                  f"3. Do transfer\n"
                  f"4. Close account\n"
                  f"5. Log out\n"
                  f"0. Exit")

            choice = int(input())
            if choice == 1:
                get_balance_data = cur.execute(
                    f'SELECT balance FROM card WHERE number={control_data[0]} AND pin={control_data[1]};')
                balance_data = cur.fetchone()
                print(f'\nBalance: {balance_data[0]}\n')
            elif choice == 2:
                print("\nEnter income: ")
                enter_income = int(input())
                data = f"""
                UPDATE card SET balance=(balance+{enter_income})
                WHERE number={control_data[0]} AND pin={control_data[1]};
                """
                cur.execute(data)
                conn.commit()
                print("Income was added!\n")
            elif choice == 3:
                print("\nTransfer: ")
                print("Enter card number: ")
                transfer_card_number = int(input())

                list_of_card_number = []

                luhn_accept = 0

                for str_data in str(transfer_card_number):
                    list_of_card_number.append(int(str_data))

                LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)
                evens = sum(int(i) for i in list_of_card_number[-1::-2])
                odds = sum(LOOKUP[int(i)] for i in list_of_card_number[-2::-2])
                if (evens + odds) % 10 == 0:
                    luhn_accept = 0
                else:
                    luhn_accept = 1

                get_balance_data = cur.execute(
                    f'SELECT * FROM card WHERE number={control_data[0]} AND pin={control_data[1]};')
                balance_data = cur.fetchone()

                get_exist_card_number = cur.execute(
                    f'SELECT number FROM card WHERE number={transfer_card_number};'
                )
                exist_data = cur.fetchone()

                if str(transfer_card_number) == balance_data[1]:
                    print("\nYou can't transfer money to the same account! ")

                elif luhn_accept == 1:
                    print("Probably you made a mistake in the card number. Please try again!\n")

                elif exist_data is None:
                    print("Such a card does not exist.\n")

                elif exist_data[0] == str(transfer_card_number):
                    print("Enter how much money you want to transfer:")
                    transfer_quantity = int(input())

                    if balance_data[3] < transfer_quantity:
                        print("Not enough money!\n")
                    else:
                        transfer_from = f"""
                                    UPDATE card SET balance=(balance-{transfer_quantity})
                                    WHERE number={control_data[0]} AND pin={control_data[1]};
                                    """
                        transfer_to = f"""
                                    UPDATE card SET balance=(balance+{transfer_quantity})
                                    WHERE number={exist_data[0]};
                                  """
                        cur.execute(transfer_from)
                        conn.commit()
                        cur.execute(transfer_to)
                        conn.commit()
                        print("Success!\n")
            elif choice == 4:
                cur.execute(
                    f'DELETE FROM card WHERE number={control_data[0]} AND pin={control_data[1]};')
                print("\nThe account has been closed!\n")
                conn.commit()
                break
            elif choice == 5:
                print("\nYou have successfully logged out!\n")
                break
            elif choice == 0:
                print("\nBye!")
                exit()

    if choices == 0:
        print("\nBye!")
        exit()
