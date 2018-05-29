from django.db import models
from django.conf import settings


def to_currency(value):
    currency_format = settings.CURRENCY_FORMAT if hasattr(settings, 'CURRENCY_FORMAT') else "{0}{1}.{2:02}€"
    currency_factor = settings.CURRENCY_FACTOR if hasattr(settings, 'CURRENCY_FACTOR') else 100
    return currency_format.format("-" if value < 0 else "", abs(value) // currency_factor, abs(value) % currency_factor)

class AccountManager(models.Manager):
    """A manager for accounts
    """
    def current(self, user):
        if user.is_authenticated:
            account, created = self.get_or_create(user=user)
            return account
        return None

class Account(models.Model):
    """An account which can hold records and transactions.
    """
    objects = AccountManager()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def saldo(self):
        cost = Record.objects.filter(account=self).exclude(state=Record.REVOKED).aggregate(models.Sum('cost')).get('cost__sum') or 0
        sent = Transaction.objects.filter(acc_from=self).exclude(state=Transaction.RETURNED).aggregate(models.Sum('value')).get('value__sum') or 0
        recv = Transaction.objects.filter(acc_to=self).exclude(state=Transaction.RETURNED).aggregate(models.Sum('value')).get('value__sum') or 0
        return recv - cost - sent;

    def currency(self):
        return to_currency(self.saldo())

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return "Account #{0}".format(self.pk)

class Transaction(models.Model):
    """A transaction from one account to another
    """
    ACTIVE = 'AC'
    CHALLENGED = 'CH'
    RETURNED = 'RT'

    STATE_CHOICES = (
        (ACTIVE, 'Active'),
        (CHALLENGED, 'Challenged'),
        (RETURNED, 'Returned'),
    )

    registered = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    acc_from = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='transaction_set_out')
    acc_to = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='transaction_set_in')

    value = models.PositiveIntegerField()
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ACTIVE)

    def currency(self):
        return to_currency(self.value)

    def inv_currency(self):
        return to_currency(-self.value)

    def type(self):
        return "transaction"

    def __str__(self):
        return "{0} -> {1} ({2})".format(self.acc_from, self.acc_to, self.currency())


class RecordManager(models.Manager):
    """Manager for records
    """
    def record(self, account, barcode, name, cost, amount=1, **kwargs):
        if not type(amount) == int:
            raise ValueError("Amount not an Integer: {0}".format(amount))
        elif amount <= 0:
            raise ValueError("Invalid Amount: {0}".format(amount))
        elif amount > 1:
            name = "{0}x {1}".format(amount, name)
            cost = cost * amount
        record = self.create(account=account, barcode=barcode, name=name, cost=cost, **kwargs)
        record.save()


class Record(models.Model):
    """A record for buying an item. The ba
    """
    objects = RecordManager()

    ACTIVE = 'AC'
    REVOKED = 'RV'
    STATE_CHOICES = (
        (ACTIVE, 'Active'),
        (REVOKED, 'Revoked'),
    )

    registered = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    barcode = models.PositiveIntegerField()
    name = models.CharField(max_length=100)

    cost = models.IntegerField()
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=ACTIVE)

    account = models.ForeignKey('Account', on_delete=models.PROTECT)

    def type(self):
        return "record"

    def currency(self):
        return to_currency(self.cost)

    def inv_currency(self):
        return to_currency(-self.cost)

    def __str__(self):
        return "{0} ({1})".format(self.name, self.currency())


class Category(models.Model):
    """A category for products
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    """A product, which can be bought
    """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    barcode = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    cost = models.IntegerField()
    storage = models.IntegerField(default=0)

    def currency(self):
        return to_currency(self.cost)

    def __str__(self):
        return "{0} ({1}) [{2}]".format(self.name, self.currency(), self.barcode)
