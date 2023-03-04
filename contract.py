"""
CSC148, Winter 2023
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import datetime
from math import ceil
from typing import Optional
from bill import Bill
from call import Call


# Constants for the month-to-month contract monthly fee and term deposit
MTM_MONTHLY_FEE = 50.00
TERM_MONTHLY_FEE = 20.00
TERM_DEPOSIT = 300.00

# Constants for the included minutes and SMSs in the term contracts (per month)
TERM_MINS = 100

# Cost per minute and per SMS in the month-to-month contract
MTM_MINS_COST = 0.05

# Cost per minute and per SMS in the term contract
TERM_MINS_COST = 0.1

# Cost per minute and per SMS in the prepaid contract
PREPAID_MINS_COST = 0.025


class Contract:
    """ A contract for a phone line

    This class is not to be changed or instantiated. It is an Abstract Class.

    === Public Attributes ===
    start:
         starting date for the contract
    bill:
         bill for this contract for the last month of call records loaded from
         the input dataset
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        self.start = start
        self.bill = None

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.

        DO NOT CHANGE THIS METHOD
        """
        raise NotImplementedError

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        """
        self.bill.add_billed_minutes(ceil(call.duration / 60.0))

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancelation is requested.
        """
        self.start = None
        return self.bill.get_cost()


class TermContract(Contract):
    """
    A Term Contract requires a commitment from its customer from
    the starting date to the specified end date.

    === Public Attributes ===
    end:
        The end date for the Term Contract

    === Private Attributes ===
    _curr_date:
        A list containing the current month of the contract at index 0, and
        the current year of the contract at index 1.

    === Representation Invariants ===
    - self.start.month <= self.end.month and self.start.year <= self.end.year

    """
    start: datetime.date
    bill: Optional[Bill]
    end: datetime.date
    _curr_date: list[int, int]

    def __init__(self, start: datetime.date, end: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.end = end
        self._curr_date = [start.month, start.year]

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the term contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        self._curr_date[0] = month
        self._curr_date[1] = year
        bill.set_rates("TERM", TERM_MINS_COST)
        if self.start.month == month and self.start.year == year:
            bill.add_fixed_cost(TERM_DEPOSIT)
        bill.add_fixed_cost(TERM_MONTHLY_FEE)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        - call.time.month >= self.start.month and call.time.year >=
        self.start.year
        - call.time.month <= self.end.month and call.time.year <=
        self.end.year
        """
        m = TERM_MINS
        t = ceil(call.duration / 60.0)
        remainder = TERM_MINS - (self.bill.free_min + t)
        if remainder < 0:
            self.bill.add_billed_minutes(abs(m - (self.bill.free_min + t)))
            self.bill.free_min = TERM_MINS
        else:
            self.bill.add_free_minutes(t)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """
        self.start = None
        m = self._curr_date[0]
        y = self._curr_date[1]
        if self.end.month <= m and self.end.year <= y:
            self.bill.add_fixed_cost(-1 * TERM_DEPOSIT)
        return self.bill.get_cost()


class MTMContract(Contract):
    """
    A month-to-month contract; A contract with no end date and no initial
    term deposit. It has higher rates for calls than a term
    contract, and comes with no free minutes included.
    """
    start: datetime.date
    bill: Optional[Bill]

    def __init__(self, start: datetime.date) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the term contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        bill.set_rates("MTM", MTM_MINS_COST)
        bill.add_fixed_cost(MTM_MONTHLY_FEE)
        self.bill = bill


class PrepaidContract(Contract):
    """
    A prepaid contract; has a start date but does not have an end date.
    It comes with no included minutes. It has an associated balance,
    which is the amount of money the customer owes.

    === Public Attributes ===
    balance:
        The amount of money the customer owes.
    """
    start: datetime.date
    bill: Optional[Bill]
    balance: float

    def __init__(self, start: datetime.date, balance: float) -> None:
        """ Create a new Contract with the <start> date, starts as inactive
        """
        Contract.__init__(self, start)
        self.balance = 0.0
        self.balance -= balance

    def new_month(self, month: int, year: int, bill: Bill) -> None:
        """ Advance to a new month in the contract, corresponding to <month> and
        <year>. This may be the first month of the term contract.
        Store the <bill> argument in this contract and set the appropriate rate
        per minute and fixed cost.
        """
        if self.balance > -10:
            self.balance -= 25
        bill.set_rates("PREPAID", PREPAID_MINS_COST)
        bill.add_fixed_cost(self.balance)
        self.bill = bill

    def bill_call(self, call: Call) -> None:
        """ Add the <call> to the bill.

        Precondition:
        - a bill has already been created for the month+year when the <call>
        was made. In other words, you can safely assume that self.bill has been
        already advanced to the right month+year.
        - call.time.month >= self.start.month and call.time.year >=
        self.start.year
        """
        time = ceil(call.duration / 60.0)
        cost = time * self.bill.min_rate
        self.balance += cost
        self.bill.add_billed_minutes(time)

    def cancel_contract(self) -> float:
        """ Return the amount owed in order to close the phone line associated
        with this contract.

        Precondition:
        - a bill has already been created for the month+year when this contract
        is being cancelled. In other words, you can safely assume that self.bill
        exists for the right month+year when the cancellation is requested.
        """
        self.start = None
        if self.balance < 0:
            self.balance = 0.0
            return self.balance
        else:
            return self.balance


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'datetime', 'bill', 'call', 'math'
        ],
        'disable': ['R0902', 'R0913'],
        'generated-members': 'pygame.*'
    })
