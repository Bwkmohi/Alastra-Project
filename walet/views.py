from django.shortcuts import render,redirect,get_object_or_404
from accaunts.check_auth import check_user_authentication
from .models import Wallet,Transaction,BankCartNumber
from django.contrib import messages
from facelogin.views import check_secure_and_enter_password
from decimal import Decimal, InvalidOperation
from django.db.models import F
from django.db import transaction
from notifications.user_notification import (
    notification_in_deposin_to_wallet,
    notification_in_withdrawal_from_wallet,
    notification_in_payment_with_wallet
)


def get_or_create_wallet(request, user):
    try:
        return Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        return Wallet.objects.create(user=user)



def check_wallet_balance(wallet,amount):
    if Decimal(wallet.balance) < Decimal(amount):
        return False
    else:return True




def check_amount(amount, wallet):
    try:
        amount_dec = Decimal(amount)
        if amount_dec <= 0:
            return False
        else:
            return True
    except (InvalidOperation, TypeError):
        return False




def wallet_view(request):
    user = check_user_authentication(request)

    if not user:
        messages.error(
            request,
            'بدون احراز هویت نمیتوانید برای خود کیف پول ایجاد کنید!'
        )
        return redirect('acc:authentication')
    

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')


    context = {
        'transactions': Transaction.objects.filter(wallet__user=user),
        'bankCartNumber':BankCartNumber.objects.filter(wallet = get_or_create_wallet(request,user))
    }
    return render(request, 'walet/wallet.html', context)





def add_bank_cart_number(request):
    user_authentication = check_user_authentication(request)

    if not user_authentication:
        return redirect('acc:pro')
    
    wallet = get_or_create_wallet(request,user_authentication)

    if request.method == 'POST':
        bank_cart_number = request.POST.get('bank_cart_number')

        BankCartNumber.objects.create(wallet=wallet,number = bank_cart_number)
        messages.success(request,'شماره کارت با موفقت ایجاد شد!')
        return redirect('walet')

    



def deposit_view(request, amount):
    user = check_user_authentication(request)
    
    if not user:
        return False
    
    wallet = get_or_create_wallet(request, user)

    if check_amount(amount,wallet) == False:
        return False

    with transaction.atomic():
        Wallet.objects.filter(pk=wallet.pk).update(
            balance=F("balance") + Decimal(amount)
        )

    wallet.refresh_from_db()

    t=Transaction.objects.create(
        wallet=wallet,
        amount=Decimal(amount),
        description='واریز به کیف پول از طریق کارت بانکی',
        transaction_type='deposit',
        status=True
    )

    notification_in_deposin_to_wallet(t.pk)
    return True



def payment(request, amount, payment_to_wallet_id):
    user = check_user_authentication(request)

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')

    if not user:
        return False

    amount_dec = Decimal(amount)
    from_wallet = get_or_create_wallet(request, user)
    to_wallet = get_object_or_404(Wallet, id=payment_to_wallet_id)

    if check_amount(amount, from_wallet) == False:
        return False
    
    if check_wallet_balance(from_wallet,amount) == False:
        return False

    with transaction.atomic():
        Wallet.objects.filter(pk=from_wallet.pk).update(
            balance=F("balance") - amount_dec
        )
    from_wallet.refresh_from_db()


    with transaction.atomic():
        Wallet.objects.filter(pk=to_wallet.pk).update(
            balance=F("balance") + amount_dec
        )
    to_wallet.refresh_from_db()

    Transaction.objects.create(
        wallet=from_wallet,
        amount=amount_dec,
        description=f'پرداخت از طریق کاربر {request.user.first_name} {request.user.last_name} به فروشگاه دیگر',
        transaction_type='payment',
        status=True
    )

    Transaction.objects.create(
        wallet=to_wallet,
        amount=amount_dec,
        description=f'واریز پول از حساب کاربری {request.user.pk} به کاربر {to_wallet.user.pk}',
        transaction_type='payment_by_others',
        status=True
    )
    notification_in_payment_with_wallet(from_wallet.pk,to_wallet.pk,amount)

    return True



def withdrawal(request, amount):
    user = check_user_authentication(request)
    amount_dec = Decimal(amount)

    if not user:
        return 'user_not_authed'
    
    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')

    wallet = get_or_create_wallet(request, user)


    if check_amount(amount_dec, wallet) == False:
        return 'amount_not_valid'
    
    if check_wallet_balance(wallet,Decimal(amount)) == False:
        return 'balance_'

    with transaction.atomic():
        Wallet.objects.filter(pk=wallet.pk).update(
            balance=F("balance") - amount_dec
        )
    wallet.refresh_from_db()

    t=Transaction.objects.create(
        wallet=wallet,
        amount=amount_dec,
        description='برداشت پول از کیف پول به حساب بانکی',
        transaction_type='withdraw',
        status=True
    )
    notification_in_withdrawal_from_wallet(t.pk)
    return True