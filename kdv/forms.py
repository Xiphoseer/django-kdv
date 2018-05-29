from django import forms
from django.forms import widgets

from .models import Record, Account, Transaction, Product

class RecordForm(forms.Form):
    value = forms.DecimalField(min_value=0.01, decimal_places=2)
    record_type = forms.ChoiceField(choices=(('IN', 'Payment'), ('OUT', 'Withdrawal')), widget=widgets.RadioSelect)

    def record(self, account):
        cost = self.cleaned_data['value'] * 100
        cost = -cost if self.cleaned_data['record_type'] == 'IN' else cost
        Record.objects.record(account, 2990005000008, 'Manuelle Ein/Auszahlung', cost)

class BuyProductForm(forms.Form):
    amount = forms.IntegerField(min_value=1)

    def record(self, account, barcode):
        product = Product.objects.get(barcode=barcode)
        amount = self.cleaned_data['amount']
        Record.objects.record(account, barcode, product.name, product.cost, amount)

class TransactionForm(forms.Form):
    value = forms.DecimalField(min_value=0.01, decimal_places=2)
    acc_to = forms.ModelChoiceField(queryset=Account.objects.all())

    def record(self, account):
        value = self.cleaned_data['value'] * 100
        acc_to = self.cleaned_data['acc_to']
        Transaction.objects.create(acc_from=account, acc_to=acc_to, value=value).save()

    def __init__(self, acc_from, **kwargs):
        super().__init__(**kwargs)
        self.fields['acc_to'].queryset = self.fields['acc_to'].queryset.exclude(pk=acc_from.pk)

class BaseTransactionForm(forms.Form):

    def trigger(self, transaction):
        transaction.state = self.state
        transaction.save()

class ChallengeTransactionForm(BaseTransactionForm):
    state = Transaction.CHALLENGED

class UnChallengeTransactionForm(BaseTransactionForm):
    state = Transaction.ACTIVE

class ReturnTransactionForm(BaseTransactionForm):
    state = Transaction.RETURNED

class RevokeRecordForm(forms.Form):
    def trigger(self, record):
        record.state = Record.REVOKED
        record.save()
