from collections import Iterable
from itertools import chain
from operator import attrgetter

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView, ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Account, Category, Product, Transaction, Record
from .forms import RecordForm, TransactionForm, BuyProductForm, ChallengeTransactionForm
from . import forms


class LedgerView(LoginRequiredMixin, TemplateView):
    template_name = 'kdv/ledger.html'

    def get_context_data(self):
        context = super().get_context_data()
        account = Account.objects.current(self.request.user)
        recs = account.record_set.all()
        send = account.transaction_set_out.all()
        recv = account.transaction_set_in.all()
        ledger = sorted(chain(recs, send, recv), key=attrgetter('registered'), reverse=True)

        context['ledger'] = ledger
        context['account'] = account
        return context

class AddRecordView(FormView):
    form_class = RecordForm
    template_name = 'kdv/add_record.html'
    success_url = reverse_lazy('kdv:ledger')

    def form_valid(self, form):
        form.record(Account.objects.current(self.request.user))
        return super().form_valid(form)

class BaseTransactionView(FormView, DetailView):
    success_url = reverse_lazy('kdv:ledger')
    model = Transaction

    def form_valid(self, form):
        transaction = self.get_object()
        form.trigger(transaction)
        return super().form_valid(form)

class BaseTransactionOutgoingView(BaseTransactionView):
    def get_queryset(self):
        account = Account.objects.current(self.request.user)
        return super().get_queryset().filter(acc_from=account, state=self.from_state)

class ChallengeTransactionView(BaseTransactionOutgoingView):
    form_class = ChallengeTransactionForm
    template_name = 'kdv/challenge_transaction.html'
    from_state = Transaction.ACTIVE
    
class UnChallengeTransactionView(BaseTransactionOutgoingView):
    form_class = forms.UnChallengeTransactionForm
    template_name = 'kdv/unchallenge_transaction.html'
    from_state=Transaction.CHALLENGED

class BaseTransactionIncomingView(BaseTransactionView):
    def get_queryset(self):
        account = Account.objects.current(self.request.user)
        return super().get_queryset().filter(acc_to=account, state__in=self.from_state)

class ReturnTransactionView(BaseTransactionIncomingView):
    form_class = forms.ReturnTransactionForm
    template_name = 'kdv/return_transaction.html'
    from_state=(Transaction.CHALLENGED, Transaction.ACTIVE)

class RevokeRecordView(FormView, DetailView):
    template_name = 'kdv/revoke_record.html'
    success_url = reverse_lazy('kdv:ledger')
    from_state = Record.ACTIVE
    form_class = forms.RevokeRecordForm
    model = Record

    def get_queryset(self):
        account = Account.objects.current(self.request.user)
        return super().get_queryset().filter(account=account, state=self.from_state)

    def form_valid(self, form):
        record = self.get_object()
        form.trigger(record)
        return super().form_valid(form)

class BuyProductView(FormView, DetailView):
    form_class = BuyProductForm
    template_name = 'kdv/buy_product.html'
    success_url = reverse_lazy('kdv:ledger')

    def get_object(self):
        kwargs = self.request.resolver_match.kwargs
        return get_object_or_404(Product, **kwargs)

    def form_invalid(self, form):
        self.object = self.get_object()
        return super().form_invalid(form)

    def form_valid(self, form):
        kwargs = self.request.resolver_match.kwargs
        form.record(Account.objects.current(self.request.user), **kwargs)
        return super().form_valid(form)

class AddTransactionView(FormView):
    template_name = 'kdv/add_transaction.html'
    success_url = reverse_lazy('kdv:ledger')

    def get_form(self):
        return TransactionForm(Account.objects.current(self.request.user), **self.get_form_kwargs())

    def form_valid(self, form):
        form.record(Account.objects.current(self.request.user))
        return super().form_valid(form)

class ProductListView(ListView):
    template_name = 'kdv/product_list.html'
    model = Category
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'form': BuyProductForm(initial={'amount':1})})
        return context

class AccountView(DetailView):
    template_name = 'kdv/account.html'
    context_object_name = 'account'
    model = Account

    def get_object(self, **kwargs):
        return Account.objects.current(self.request.user)
