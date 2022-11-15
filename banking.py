import random
import sqlite3
conn = sqlite3.connect('card.s3db')
cur = conn.cursor()


# A function that creates a number of n digits for the password and login
# (from the range 000.. - 999..)
def random_n_numb(n):
    num = str()
    for i in range(n):
        num += str(random.randint(0, 9))
    return num


# A function that checks if an account exists in the system
def login_in_system(login_try, password_try):
    cur.execute("SELECT number, pin FROM card WHERE number = {} AND pin = {} ;".format(login_try, password_try))
    activ_card = cur.fetchone()
    return activ_card is not None


# Calculating the last number of a credit card number using Luhn's algorithm
def last_num_luna(login):
    if len(login) == 16:
        login = login[:-1]
    login_list = [int(x) for x in login]
    login_list = [login_list[i] * 2 if i % 2 == 0 else login_list[i] for i in range(15)]
    login_list = [x - 9 if x > 9 else x for x in login_list]
    sum_num = sum(login_list)
    if sum_num % 10 == 0:
        last_num = 0
    else:
        last_num = 10 - sum_num % 10
    return last_num


# Creating a credit card number based on Luhn's algorithm
def create_login():
    login_new = "400000" + random_n_numb(9)
    last_num = last_num_luna(login_new)
    return login_new + str(last_num)


# Function that defines the interface and actions on the start window
def start_wind():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    ans = int(input())

    if ans == 0:
        print("", "Bye!", sep="\n")
        quit()
    elif ans == 1:
        # Creating a new account and adding it to the database,
        # with checking for identity of the login
        login_new = create_login()
        password_new = random_n_numb(4)

        while True:
            cur.execute("SELECT number FROM card WHERE number = {};".format(login_new))
            log_in_sys = cur.fetchone()
            if log_in_sys is None:
                cur.execute("INSERT INTO card(number, pin) VALUES(?, ?)", (login_new, password_new))
                conn.commit()
                break
            else:
                login_new = create_login()

        print("", "Your card has been created", sep="\n")
        print("Your card number:")
        print(login_new)
        print("Your card PIN:")
        print(password_new)
        print("")
        start_wind()
    else:
        # Log in to the system
        print("", "Enter your card number:", sep="\n")
        login_ans = input()
        print("Enter your PIN:")
        password_ans = input()

        if login_in_system(login_ans, password_ans):
            print("", "You have successfully logged in!", sep="\n")
            logged_wind(login_ans, password_ans)
        else:
            print("", "Wrong card number or PIN!", "", sep="\n")
            start_wind()


# A function that defines the interface and actions after logging in
def logged_wind(login_ans, password_ans):
    print("")
    print("1. Balance")  # Check account balance
    print("2. Add income")  # Add funds to account
    print("3. Do transfer")  # Transfer funds from account to another
    print("4. Close account")  # Delete account
    print("5. Log out")
    print("0. Exit")

    ans = int(input())

    if ans == 0:
        print("", "Bye!", sep="\n")
        quit()
    elif ans == 1:
        # Check account balance
        cur.execute("SELECT balance FROM card WHERE number = {};".format(login_ans))
        print("", "Balance: {}".format(cur.fetchone()[0]), sep="\n")
        logged_wind(login_ans, password_ans)
    elif ans == 2:
        # Add funds to account
        print("", "Enter income:", sep="\n")
        income = int(input())
        cur.execute("SELECT balance FROM card WHERE number = {};".format(login_ans))
        new_balance = cur.fetchone()[0] + income
        cur.execute("UPDATE card SET balance = {} WHERE number = {};".format(new_balance, login_ans))
        conn.commit()
        print("Income was added!")
        logged_wind(login_ans, password_ans)
    elif ans == 3:
        # Transfer funds from account to another
        print("", "Transfer", "Enter card number:", sep="\n")
        login_trans = input()

        # Login validation checks:
        # Check: If the user tries to transfer money to the same account
        if login_trans == login_ans:
            print("You can`t transfer money to the same account!")
            logged_wind(login_ans, password_ans)

        # Check: If the receiver's card number doesn’t pass the Luhn algorithm
        last_num = last_num_luna(login_trans)
        if last_num != int(login_trans[-1]):
            print("Probably you made a mistake in the card number. Please try again!")
            logged_wind(login_ans, password_ans)

        # Check: If the receiver's card number doesn’t exist
        cur.execute("SELECT number FROM card WHERE number = {};".format(login_trans))
        if cur.fetchone() is None:
            print("Such a card does not exist.")
            logged_wind(login_ans, password_ans)

        print("Enter how much money  you want to transfer:")
        trans_money = int(input())

        # Check: If the user tries to transfer more money than he/she has
        cur.execute("SELECT balance FROM card WHERE number = {};".format(login_ans))
        sender_balance = cur.fetchone()[0]
        if trans_money > sender_balance:
            print("Not enough money!")
            logged_wind(login_ans, password_ans)

        # Money transfer from card to card
        cur.execute("SELECT balance FROM card WHERE number = {};".format(login_trans))
        recipient_balance = cur.fetchone()[0]
        cur.execute("UPDATE card SET balance = {} WHERE number = {};".format(sender_balance - trans_money, login_ans))
        cur.execute("UPDATE card SET balance = {} WHERE number = {};"
                    .format(recipient_balance + trans_money, login_trans))
        conn.commit()
        print("Success!")
        logged_wind(login_ans, password_ans)
    elif ans == 4:
        # Delete account
        cur.execute("DELETE FROM card WHERE number = {};".format(login_ans))
        conn.commit()
        print("", "The account has been closed!", "", sep="\n")
        start_wind()
    else:
        print("", "You have successfully logged out!", "", sep="\n")
        start_wind()


def main():
    start_wind()


if __name__ == "__main__":
    main()
