from unittest import TestCase
from unittest.mock import Mock, patch, call
from datetime import date


class Account:
    def __init__(self, transaction_history, balance=0):
        self.transaction_history = transaction_history
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.get('transactions').append(
            DepositTransaction(amount, date.today(), self.balance)
        )

    def withdraw(self, amount):
        self.balance -= amount
        self.transaction_history.get('transactions').append(
            WithdrawTransaction(amount, date.today(), self.balance)
        )


class Transaction:
    def __init__(self, amount, date, balance):
        self.amount = amount
        self.date = date
        self.balance = balance


class DepositTransaction(Transaction):
    pass


class WithdrawTransaction(Transaction):
    pass


class BankStatement:
    def __init__(self, transaction_history):
        self.transaction_history = transaction_history

    def __str__(self):
        statement = ''
        for transaction in self.transaction_history.get('transactions'):
            if isinstance(transaction, DepositTransaction):
                statement += "Deposited {} on {} => balance: {}\n".format(
                    transaction.amount, transaction.date, transaction.balance
                )
            else:
                statement += "Withdrew {} on {} => balance: {}\n".format(
                    transaction.amount, transaction.date, transaction.balance
                )
        return statement

class TestBanking(TestCase):

    def setUp(self):
        self.mock_transaction_history = Mock(transactions=[])
        self.account = Account(self.mock_transaction_history)



    @patch("test_banking.date")
    @patch("test_banking.DepositTransaction")
    def test_deposit_adds_transaction_history(self, mock_deposit_transaction, mock_date):
        mock_date.today.return_value = date(2010, 1, 1)

        self.account.deposit(1000)

        self.assertEqual(self.account.balance, 1000)

        self.mock_transaction_history.get('transactions').append.assert_called_with(
            mock_deposit_transaction.return_value
        )
        mock_deposit_transaction.assert_called_with(1000, date(2010, 1, 1), 1000)


    @patch("test_banking.date")
    @patch("test_banking.DepositTransaction")
    def test_deposit_with_multiple_transactions(self, mock_deposit_transaction, mock_date):
        mock_date.today.side_effect = [date(2010, 1, 1), date(2010, 1, 2)]

        self.account.deposit(1000)
        self.account.deposit(2000)

        self.mock_transaction_history.get('transactions').append.assert_has_calls([
            call(mock_deposit_transaction.return_value),
            call(mock_deposit_transaction.return_value)
        ])

        mock_deposit_transaction.assert_has_calls([
            call(1000, date(2010, 1, 1), 1000),
            call(2000, date(2010, 1, 2), 3000)
        ])


    @patch("test_banking.date")
    @patch("test_banking.WithdrawTransaction")
    def test_withdraw_adds_transaction_history(self, mock_withdraw_transaction, mock_date):
        mock_date.today.return_value = date(2010, 1, 3)

        self.account.withdraw(1000)

        self.mock_transaction_history.get('transactions').append.assert_called_with(
            mock_withdraw_transaction.return_value
        )
        mock_withdraw_transaction.assert_called_with(1000, date(2010, 1, 3), -1000)


    def test_bank_statement_for_single_transaction(self):
        mock_transaction_history = {
            'transactions': [
                DepositTransaction(1000, date.today(), 1000)
            ]
        }
        bank_statement = BankStatement(mock_transaction_history)
        self.assertEqual("Deposited {} on {} => balance: {}\n".format(
            1000, date.today(), 1000), bank_statement.__str__()
        )

    
    def test_bank_statement_for_multiple_transactions(self):
        mock_transaction_history = {
            'transactions': [
            DepositTransaction(1000, date.today(), 1000),
            DepositTransaction(2000, date.today(), 3000),
            WithdrawTransaction(500, date.today(), 2500)
        ]}
        bank_statement = BankStatement(mock_transaction_history)
        self.assertEqual(
            "Deposited 1000 on {} => balance: 1000\nDeposited 2000 on {} => balance: 3000\nWithdrew 500 on {} => balance: 2500\n"
            .format(date.today(), date.today(), date.today()), bank_statement.__str__()
        )
