from django.utils.translation import gettext as _

CATEGORY_CHOICES = (
    (0, _('Trousers')),
    (1, _('T-shirt')),
    (2, _('Jacket')),
    (3, _('Sportswear')),
    (4, _('Sweater')),
    (5, _('Suit'))
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
