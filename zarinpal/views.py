import requests
from django.shortcuts import redirect ,get_object_or_404,render
from django.urls import reverse
from reservations.models import OrderModel
from django.contrib import messages
from siteinfo.systemsendmail import send_quick_mail
from costs_fee.views import cost_from_order
from django.contrib.auth.models import User
from reservations.views import make_true_order_model
from accaunts.check_auth import check_user_authentication
from walet.models import Transaction
from walet.views import get_or_create_wallet
from shop.mange_product_quantity import cost_product_quantity
from siteinfo.models import MerchanteCode,SiteInfo
from walet.models import Wallet
from decimal import Decimal
from django.db.models import F
from django.db import transaction
from django.views.decorators.http import require_POST
from walet.views import withdrawal,check_amount
from walet.models import BankCartNumber
ZARINPAL_PAYOUT_URL = "https://api.zarinpal.com/pg/v4/payout/transfer.json"


def zarinpal_request(request,order_id):
    order = get_object_or_404(OrderModel, id=order_id)
    site_title = SiteInfo.objects.all().first().site_title
    mc = MerchanteCode.objects.first().code
    ZARINPAL_MERCHANT_ID = mc 

    amount = int(order.total_price)   # مطمئن شوید واحد ریال است
    description = f"پرداخت از سایت {site_title if site_title else 'Alastra'}"
    email = order.email
    mobile = order.phone
    callback_url = request.build_absolute_uri(reverse('zarinpal_verify'))
    
    
    data = {
        "merchant_id":ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "callback_url": callback_url,
        "description": description,
        "metadata": {
            "email": email,
            "mobile": mobile
        }
    }

    headers = {'accept': 'application/json', 'content-type': 'application/json'}

    try:
        response = requests.post('https://sandbox.zarinpal.com/pg/v4/payment/request.json', json=data, headers=headers, timeout=10)
        res_data = response.json()
    except requests.RequestException as e:
        messages.error(
            request,
            'خطا در ارسال درخواست'
        )
        return redirect('res:list_reservations')

    if res_data.get('data') and res_data['data'].get('code') == 100:
        cost_from_order(request,order_id)
        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{res_data['data']['authority']}')
    else:
        messages.error(
            request,
            'خطا در درخواست'
        )
        return redirect('res:list_reservations')




def zarinpal_verify(request):
    order_id = request.session.get('order_id')
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')


    if status == 'OK':
        data = {
            "merchant_id": "zarinpal_test",
            "amount": 10000,
            "authority": authority
        }

        headers = {'accept': 'application/json', 'content-type': 'application/json'}
        response = requests.post('https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json', json=data, headers=headers)
        res_data = response.json()

        if res_data.get('data') and res_data['data'].get('code') == 100:
            user = get_object_or_404(User,id=request.user.pk)
            order = get_object_or_404(OrderModel,id=order_id)
            order.paid = True
            order.save()
            
            cost_from_order(request,order_id)
            cost_product_quantity(order_id)
            make_true_order_model(order.pk)

            message = 'پرداخت با موفقیت انجام شد'
            
            send_quick_mail(
                subject='پرداخت ',
                message=message,
                to_email=user.email
            )

            messages.success(request,message)
         
            con = {
                'ref_id':{res_data['data']['ref_id']}
            }
            return render(request,'zarinpal/paid_succ.html',con)

        else:
            user = get_object_or_404(User,id=request.user.pk)
            message = 'پرداخت ناموفق بود'

            send_quick_mail(
                subject='پرداخت ',
                message=message,
                to_email=user.email
            )
            messages.error(request,message)
            return redirect('res:list_reservations')
    else:
            message = ' پرداخت ناموفق بود  توسط شما کنسل شد'
            user = get_object_or_404(User,id=request.user.pk)

            send_quick_mail(
                subject='پرداخت ',
                message=message,
                to_email=user.email
            )
            messages.warning(request,message)
            return redirect('acc:pro')


 


 
def start_deposit_to_wallet(request):
    user=check_user_authentication(request)
    wallet=get_or_create_wallet(request,user)
    mc = MerchanteCode.objects.first().code
    ZARINPAL_MERCHANT_ID = mc 

    if not user:
        return redirect('acc:authentication')
    
    if request.method == 'POST':

        amount = int(request.POST.get('amount'))
        callback_url = request.build_absolute_uri(reverse('verify_deposit_to_wallet'))
        description = f'Wallet recharge for user {user.user.username}'

        data = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
        }

        response = requests.post('https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json', json=data)
        res_data = response.json()

        if res_data.get('data', {}).get('code') == 100:
            authority = res_data['data']['authority']

            Transaction.objects.create(
                wallet = wallet,
                amount=amount,
                transaction_type='deposit',
                authority=authority,
            )
            payment_url = f'https://www.zarinpal.com/pg/StartPay/{authority}'
            return redirect(payment_url)
        
        else:
            messages.error(
                request,
                res_data.get('errors')
            )
            
            return redirect('walet')
 

def verify_deposit_to_wallet(request):
    
    user=check_user_authentication(request)
    wallet=get_or_create_wallet(request,user)
    authority = request.GET.get('Authority')
    status = request.GET.get('Status')
    mc = MerchanteCode.objects.first().code
    ZARINPAL_MERCHANT_ID = mc 

    if not user:
        return redirect('acc:authentication')

    try:
        transactions = Transaction.objects.get(authority=authority, wallet=wallet, status=False)
    except Transaction.DoesNotExist:
        messages.error(
            request,
            'Transaction not found or already processed.'
        )        
        return redirect('walet')


    if status == 'OK':
        data = {
            "merchant_id": ZARINPAL_MERCHANT_ID,
            "amount": int(transactions.amount),
            "authority": authority,
        }
        response = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', json=data)
        res_data = response.json()

        if res_data.get('data', {}).get('code') == 100:
            transactions.status = True
            transactions.ref_id = res_data['data']['ref_id']
            transactions.save()
                    
            with transaction.atomic():
                Wallet.objects.filter(pk=wallet.pk).update(
                    balance=F("balance") + Decimal(transactions.amount)
                )
            wallet.refresh_from_db()
            
            return render(request, 'zarinpal/paid_succ.html', {'ref_id': transactions.ref_id})
        else:
            transactions.status = False
            transactions.save()
            messages.warning(
                request,
                'واریز با شکست مواجه شد'
            )
            return redirect('walet')
    else:
        transactions.status = False
        transactions.save()
        messages.warning(
            request,
            'واریز با خطا مواجه شد . یا کنسل شده!'
        )
        return redirect('walet')
    








def zarinpal_payout(amount, destination_value, destination_type="card", description="برداشت وجه"):
    """
    amount: مبلغ به تومان
    destination_value: شماره کارت یا شبا
    destination_type: card | sheba
    """
    mc = MerchanteCode.objects.first().code
    ZARINPAL_MERCHANT_ID = mc 
    payload = {
        "merchant_id": ZARINPAL_MERCHANT_ID,
        "amount": amount,
        "destination": {
            "type": destination_type,
            "value": destination_value
        },
        "description": description
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        ZARINPAL_PAYOUT_URL,
        json=payload,
        headers=headers,
        timeout=30
    )

    return response.json()






@require_POST
def withdraw_view(request):
    user = check_user_authentication(request)
    wallet = get_or_create_wallet(request,user)
    amount = Decimal(request.POST.get("amount")) #required number
    bank_cart_number_id = request.POST.get("bank_cart_number_id") #select in front
    bankCartNumber = BankCartNumber.objects.filter(wallet = wallet)

    if not bankCartNumber.exists():
        pass
    
    try:
        bankCartNumber.get(id = bank_cart_number_id)
    except:
        pass

    if check_amount(amount,wallet) == False:
        messages.warning(
            request,
            '(InvalidOperation, TypeError)'
        )
        return redirect('walet')

    result = zarinpal_payout(
        amount=amount,
        destination_value=bankCartNumber.first().number,
        destination_type="card",
        description="برداشت کاربر"
    )

    withdraw_ = withdrawal(request,amount)

    if withdraw_ == 'amount_not_valid':
        messages.error(
            request,
            '(InvalidOperation, TypeError)'
        )        
        return redirect('walet')

    elif withdraw_ == 'balance_':
        messages.error(
            request,
            'برداشت بیشتر از موجودی کیف پول!'
        )        
        return redirect('walet')

    elif withdraw_ == 'user_not_authed':
        messages.error(
            request,
            'ابتدا اهراز هویت کنید!'
        )        
        return redirect('acc:authentication')
    
    elif withdraw_ == True:
        if result.get("data", {}).get("code") == 100:
            Transaction.objects.create(
                wallet = wallet,
                amount = amount,
                ref_id = result["data"].get("authority"),
                description = f"""
                    برداشت موجودی از کیف پول به حساب بانکی
                """,
                transaction_type = 'withdraw',
                status = True
            )
            messages.success(
                request,
                'برداشت موفقیت امیز بود!'
            )
            return redirect('walet')

        else:
            Transaction.objects.create(
                wallet = wallet,
                amount = amount,
                ref_id = result["data"].get("authority"),
                description = f"""
                    برداشت موجودی از کیف پول به حساب بانکی
                """,
                transaction_type = 'withdraw',
                status = False
            )
            with transaction.atomic():
                Wallet.objects.filter(pk=wallet.pk).update(
                    balance=F("balance") - amount
                )
            wallet.refresh_from_db()
            messages.warning(
                request,
                'برداشت نا موفق!'
            )
            return redirect('walet')