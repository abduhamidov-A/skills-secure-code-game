from collections import namedtuple
from decimal import Decimal, InvalidOperation

Order = namedtuple('Order', 'id, items')
Item = namedtuple('Item', 'type, description, amount, quantity')

MAX_AMOUNT = Decimal('100000')
MAX_QUANTITY = 100
MAX_TOTAL = Decimal('1000000')


def validorder(order: Order):
    payments = Decimal(0)
    expenses = Decimal(0)
    for item in order.items:
        if item.type not in ('payment', 'product'):
            return "Invalid item type: %s" % item.type
        try:
            amount = Decimal(str(item.amount))
        except InvalidOperation:
            return "Invalid item amount"
        if item.type == 'payment':
            if amount.is_finite() and abs(amount) <= MAX_AMOUNT:
                payments += amount
        else:
            if not amount.is_finite() or not 0 < amount <= MAX_AMOUNT:
                return "Invalid item amount"
            if type(item.quantity) is not int or not 0 < item.quantity <= MAX_QUANTITY:
                return "Invalid item quantity"
            expenses += amount * item.quantity

    if abs(payments) > MAX_TOTAL or expenses > MAX_TOTAL:
        return "Total amount payable for an order exceeded"
    if payments != expenses:
        return "Order ID: %s - Payment imbalance: $%0.2f" % (order.id, payments - expenses)
    return "Order ID: %s - Full payment received!" % order.id
