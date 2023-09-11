CATEGORY_CHOICES = (
    (0, 'Portable'),
    (1, 'Touchscreen'),
    (2, 'Work'),
    (3, 'Business'),
    (4, 'Student')
)

LABEL_CHOICES = (
    (0, 'primary'),
    (1, 'secondary'),
    (2, 'danger')
)

ADDRESS_CHOICES = (
    (0, 'Billing'),
    (1, 'Shipping'),
)

ORDER_STATUS = (
    (0, 'In cart'),
    (1, 'Ordered'),
    (2, 'Shipping'),
    (3, 'Completed'),
    (4, 'Cancelled'),
)

REFUND_STATUS = (
    (0, 'None'),
    (1, 'Pending'),
    (2, 'Approved'),
    (3, 'Cancelled')
)

PAYMENT_STATUS = (
    (0, 'None'),
    (1, 'Paid')
)
