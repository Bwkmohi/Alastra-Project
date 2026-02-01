from django.shortcuts import render,get_object_or_404,redirect
from reservations.models import OrderModel
from .models import CostFeeSite,WebsiteCostFeeTransaction,WebsiteWallet
from decimal import Decimal
from django.contrib import messages
from django.db.models import F
from django.db import transaction
from walet.models import Wallet,Transaction

def get_or_create_site_wallet():
    websiteWallet = WebsiteWallet.objects.first()
    if not websiteWallet:
        return WebsiteWallet.objects.create(balance=0)
    else:
        return websiteWallet
        
        
        

def cost_from_order(request, order_id):
    order = get_object_or_404(OrderModel, id=order_id)
    wallet=get_or_create_site_wallet() 

    for cost_fee in CostFeeSite.objects.filter(active=True):
        if not WebsiteCostFeeTransaction.objects.filter(order=order,cost_fee = cost_fee).exists():

            if cost_fee.is_percent:
                res = (Decimal(cost_fee.value) / Decimal(100)) * order.total_price
            else:
                res = Decimal(cost_fee.value)

            WebsiteCostFeeTransaction.objects.create(
                amount=res,
                order=order,
                cost_fee = cost_fee
            )

            with transaction.atomic():
                WebsiteWallet.objects.filter(pk=wallet.pk).update(
                    balance=F("balance") + res
                )

            order.total_price += res
            wallet.refresh_from_db()
            order.save()

        else:
            print('Order Exist!!!')


def payout_to_user_wallet(request):
    if not request.user.is_superuser:
        return redirect('index')
        

    if request.method == 'POST':
        wallet_id = request.POST.get('wallet_id')
        user_id = request.POST.get('user_id')

        try:
            wallet=Wallet.objects.get(id = wallet_id,user__user__id = user_id)
            site_wallet = get_or_create_site_wallet()

            WebsiteWallet.objects.filter(pk=site_wallet.pk).update(
                balance=F("balance") - Decimal(site_wallet.balance)
            )

            WebsiteCostFeeTransaction.objects.create(
                description = f"""
                    برداشت از کیف پول وب سایت به کیف پول شخصی.  
                    \n
                    wallet Id: {wallet_id}
                    User Id: {user_id} 
                    User Name: {wallet.user.user.username}
                    Fist Name - Last Name" {wallet.user.user.get_full_name()}

                    Amount: {site_wallet.balance}
                """,
                amount = site_wallet.balance
            )

            Wallet.objects.filter(pk=wallet.pk).update(
                balance=F("balance") + Decimal(site_wallet.balance)
            )
            Transaction.objects.create(
                wallet = wallet,
                amount = site_wallet.balance,
                description = '  برداشت از کیف پول وب سایت به کیف پول شخصی.  ',
                transaction_type = 'deposit',
                status = True
            )
            messages.success(
                request,
                'برداشت با موفقیت انجام شد!'
            )
            return redirect('walet')
        except Wallet.DoesNotExist:
            messages.error(
                request,
                'کیف پول یافت نشد!'
            )
            return redirect('payout_to_user_wallet')
    else:
        return render(request,'costs_fee/payout_to_user_wallet.html',
            {
                'WebsiteWallet':get_or_create_site_wallet()
            }
        )
