from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from accaunts.models import UserAuthentication
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from random import randint
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .check_auth import check_user_authentication,check_user
from .models import NationalIDAuthentication
# from opencv import views
from config.settings import EMAIL_HOST_USER
from chat.share_list import chat_homes_view
from facelogin.views import check_secure_and_enter_password
from notifications.user_notification import notification_in_signup
from .check_auth import check_nation_cart
from reservations.models import ProvinceCategory,Citys
from siteinfo.views import create_user_and_shop_image
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from sellers.models import Seller
from collaborator.models import ShopCollaborator
from supporter.models import Supporter
from group_cart.models import GroupCart
from facelogin.models import UserFace
from blog.models import AuthorModel
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse 



def signup(request):
    if request.user.is_authenticated:
        return redirect('acc:pro')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        name = request.POST.get('first_name', '').strip()
        lastname = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()


        if len(username) < 4:
            messages.warning(
                request,
                'نام کاربری باید حداقل ۴ حرف باشد.'
            )
            return redirect('acc:sign')

        if len(password) < 8:
            messages.warning(request, 'رمز عبور باید حداقل ۸ کاراکتر باشد.')
            return redirect('acc:sign')

        if User.objects.filter(username=username).exists():
            messages.warning(request, 'این نام کاربری قبلاً ثبت شده.')
            return redirect('acc:sign')

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=name,
                last_name=lastname,
                email=email
            )
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

            
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد')
            return redirect('acc:send_otp_to_email')   

        except IntegrityError:
            messages.error(request, 'خطایی در ثبت نام رخ داد. لطفاً دوباره تلاش کنید.')
            return redirect('acc:sign')

    return render(request, 'accaunts/signup.html')
 
from config.settings import EMAIL_HOST_USER
def send_otp_to_email(request):
    user=get_object_or_404(User,id=request.user.pk)

    otp = randint(100000, 999999)

    request.session['verify_user_id'] = user.id
    request.session['otp'] = str(otp)

    send_mail(
        'کد تایید ',
        'کد تایید ورود:',
        EMAIL_HOST_USER,
        [user.email],
        html_message=f"<center><h3>کد شما: {otp}</h3></center>",
        fail_silently=True,
    )

    messages.success(request, 'کد به ایمیل شما ارسال شد')
    return redirect('acc:verify_email')


def verify_email(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        session_code = request.session.get('otp')
        user_id = request.session.get('verify_user_id')

        if not user_id or not session_code:
            messages.error(request, 'اطلاعات جلسه یافت نشد. دوباره تلاش کنید.')
            return redirect('acc:sign')

        if input_code == session_code:
            user = User.objects.get(id=user_id)
            user.is_staff = True
            user.is_active = True
            user.save()

            del request.session['otp']
            del request.session['verify_user_id']

            notification_in_signup(user)
            messages.success(
                request,
                  'با موفقیت وارد شدید'
            )
            return redirect('acc:pro')
        
        else:
            messages.error(request, 'کد وارد شده اشتباه است.')
            return redirect('acc:verify_email')

    return render(request, 'accaunts/verify_email.html')
 

def logout_view(request):
    logout(request)
    messages.success(
        request, 
        'با موفقیت خارج شدید!'
    )
    return redirect('index')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('acc:pro')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'سلام {user.first_name} خوش امدید ')
            return redirect('acc:pro')

        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
            return redirect('acc:login')

    return render(request, 'accaunts/login.html')


token_generator = PasswordResetTokenGenerator()

def send_reset_password_link(request):
    user = check_user(request)

    if user:
        reset_url = request.build_absolute_uri(
            reverse("acc:password_reset_confirm", args=[urlsafe_base64_encode(force_bytes(user.pk)), token_generator.make_token(user)])
        )
        login(request,user)

        msg = render_to_string("accaunts/password_reser_link.html", {
            "reset_url": reset_url,
        })
        login(request,user)
        send_mail(
            "بازیابی رمز عبور", 
            msg, EMAIL_HOST_USER,
            [user.email]
        )
        login(request,user)
        messages.success(
            request,
            'لینک بازیابی رمز عبور به ایمیل شما ارسال شد!'
        )
        return redirect('acc:pro')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            try:
                user_model=User.objects.get(username=username)
            except User.DoesNotExist:
                user_model=None
            
            reset_url = request.build_absolute_uri(
                reverse("acc:password_reset_confirm", args=[urlsafe_base64_encode(force_bytes(user_model.pk)), token_generator.make_token(user_model)])
            )

            msg = render_to_string("accaunts/password_reser_link.html", {
                "reset_url": reset_url,
            })
            send_mail(
                "بازیابی رمز عبور", 
                msg, EMAIL_HOST_USER,
                [user_model.email]
            )
            messages.success(
                request,
                'لینک بازیابی رمز عبور به ایمیل ارسال شد!'
            )
            return redirect('index')
        return render(request,'accaunts/enter_username_for_reset_password.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (
        TypeError, ValueError, OverflowError, get_user_model().DoesNotExist
    ):
        user = None
    print(f"Generated token: {token_generator.make_token(user)}")
    print(f"Generated UID: {urlsafe_base64_encode(force_bytes(user.pk))}")
    uid = force_bytes(user.pk)
    token = token_generator.make_token(user)

    print(f"UID: {uid}")
    print(f"Generated Token: {token}")

    if not user:
        messages.error(request, "کاربر یافت نشد!")
        return redirect('acc:pro')
    if not token_generator.check_token(user, token):
        messages.error(request, f"توکن نامعتبر است! UID: {uid}, Token: {token}")
        return redirect('acc:pro')



    if request.method == "POST":
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if len(new_password1) >= 8 and len(new_password2) >= 8:

            user.set_password(new_password1)
            user.save()
            messages.success(
                request, 
                'رمز شما تغییر یافت'
            )
            return redirect('acc:pro')
        else:
            messages.warning(
                request, 
                'رمز عبور باید حداقل 8 کاراکتر باشد!'
            )
        return redirect('acc:password_reset_confirm', uidb64, token)
    else:
        return render(
            request, 
            "accaunts/password_reset_confirm.html"
        )


@login_required
def user_edit(request):
    user = request.user  

    if not user.is_authenticated:
        return redirect('acc:login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()

        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')


        if user.username != username and User.objects.filter(username=username).exists():
            messages.error(
                request, 
                'این نام کاربری قبلاً انتخاب شده است.'
            )
            return redirect('acc:user_edit')
        
        user.first_name = first_name
        user.last_name = last_name
        user.username = username

        if old_password and new_password:
            if user.check_password(old_password):
                user.set_password(new_password)  
                update_session_auth_hash(request, user)  
                messages.success(
                    request, 
                    'رمز عبور با موفقیت تغییر یافت.'
                )

            else:
                messages.error(
                    request, 
                    'رمز عبور فعلی اشتباه است.'
                )
                return redirect('acc:edit')

        user.save()
        messages.success(
            request, 
            'اطلاعات پروفایل با موفقیت به‌روزرسانی شد.'
        )
        return redirect('acc:pro')

    return render(
        request, 
        'accaunts/signup.html',
        {
            'user':request.user
        }
    )


def authentication(request):
    create_user_and_shop_image()    
    user = check_user(request)
    user_authentication=check_user_authentication(request)

    if not user:
        return redirect('acc:login')
 
    if user_authentication:
        return redirect('acc:pro')

    if request.method == 'POST':
        data = request.POST.get
        profile = request.FILES.get('profile')
        ua=UserAuthentication.objects.create(
            user = user,
            phone=data('phone'),
            profile=profile,
            address=data('address'),
            age=data('age'),
            postal_code=data('postal_code'),
            national_code=data('national_code'),
            city=get_object_or_404(Citys,id=data('city')),
            province=get_object_or_404(ProvinceCategory,id=data('province')) ,
            gender = request.POST.get('gender')
        )
        
        gender = data('gender')
        if gender:
            ua.gender = gender
            ua.save()
        
        if not profile:
            create_user_and_shop_image()

        messages.success(
            request,
            'اطلاعات شما با موفقیت ثبت شد '
        )
        return redirect('acc:pro')
    
    return render(
        request,
        'accaunts/authentication.html',
        {
            'province':ProvinceCategory.objects.all(),
            'citys':Citys.objects.all(),
        }
    )


def edit_authentication_user(request):
    user = check_user(request)
    user_authentication = check_user_authentication(request)

    if not user:
        return redirect('acc:login')

    if not user_authentication:
        messages.error(
            request,
            'Error!'
        )
        return redirect('acc:authentication')
    
    # authed_with_cart = check_nation_cart(request)
    # if authed_with_cart:
    #     if authed_with_cart.is_verified == True:
    #         messages.success(
    #             request,
    #             'بعد اهراز هویت نمیتوانید اطلاعات شخصی را عوض کنید!'
    #         )
    #         return redirect('acc:pro')

    if request.method == 'POST':
        data = request.POST.get
        profile = request.FILES.get('profile')
        user_authentication.phone = data('phone')
        user_authentication.profile = profile
        user_authentication.address = data('address')
        user_authentication.age = data('age')
        user_authentication.postal_code = data('postal_code')
        user_authentication.national_code = data('national_code')
        user_authentication.gender = data('gender')
        user_authentication.city = get_object_or_404(Citys,id=data('city'))
        user_authentication.province = get_object_or_404(ProvinceCategory,id=data('province'))
        user_authentication.save()
        
        messages.success(
            request,
            'اطلاعات شما با موفقیت ثبت شد ! '
        )
        return redirect('acc:pro')
    
    return render(
        request,
        'accaunts/authentication.html',
        {
            'authed_user':user_authentication,
            'province':ProvinceCategory.objects.all(),
            'citys':Citys.objects.all(),
        }
    )

 
def get_user_auth_step(request):
    user = check_user(request)
    user_authentication = check_user_authentication(request)
    nation_cart = check_nation_cart(request)

    if user and not user_authentication and nation_cart:
        return 1
    
    elif user_authentication and not nation_cart:
        return 2
    
    elif nation_cart:
        return 3


from walet.views import get_or_create_wallet
from reservations.models import Reservation

def profile(request):
    user = check_user(request)
    user_authentication = check_user_authentication(request)
    if not user:
        messages.error(
            request,
            'ورود به حساب کاربری'
        )
        return redirect('acc:login')

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    
    is_business_account = False

    is_seller=Seller.objects.filter(user = user)
    is_author=AuthorModel.objects.filter(user_authentication__user = user)
    is_collab=ShopCollaborator.objects.filter(user=user)
    is_supporter=Supporter.objects.filter(user__user=user)
    user_face=UserFace.objects.filter(user=user,active=True)
    is_created_password = user_face.exists()
    is_face_registered = user_face.first().face_image or '' if user_face else ''

    if is_seller or is_author or is_collab or is_supporter:
        is_business_account=True

    return render(
        request,
        'accaunts/profile.html',
        {
            'chats':chat_homes_view(request.user)[:4],
            'step': get_user_auth_step(request),
            'is_authenticated_user':check_user_authentication(request),
            'is_NationalIDAuthenticated':check_nation_cart(request),
            'is_business_account':is_business_account,
            'is_seller':is_seller,
            'is_author':is_author,
            'is_collab':is_collab,
            'is_supporter':is_supporter,
            'group_cart':GroupCart.objects.filter(users = user),
            'is_created_password':is_created_password,
            'is_face_registered':is_face_registered,
            'count_reservations':Reservation.objects.filter(order__user = user,paid = True,canceled=False).count()
        }
    )


# def authentication_with_nation_cart_image(request):
#     user=check_user(request)
#     nation_cart = check_nation_cart(request)
    
#     if not user:
#         return redirect('acc:login')
    
#     if request.method == 'POST':
#         image=request.FILES.get('image')

#         model_img=NationalIDAuthentication.objects.create(
#             national_id_image = image,
#             user = user
#         )
#         return redirect('acc:authentication_with_nation_cart_image')
 
#     else:
#         if nation_cart:
#             if not check_user_authentication(request):
#                 response=views.ocr_authenticate_from_image(request)

#                 if response == 'IMAGE NOT FUOND':
#                     messages.error(
#                         request,
#                         'عکس یافت نشد. لطفا مجدد تلاش کنید'
#                     )
#                     model_img.delete()
#                     return redirect('acc:authentication_with_nation_cart_image')
                
#                 elif response == 'CANT READ IMAGE':
#                     model_img.delete()
#                     messages.error(
#                         request,
#                         'عکس قابل خوانا نیست'
#                     )
#                     return redirect('acc:authentication_with_nation_cart_image')
                
#                 elif response == 'AUTH BE SUCCESS FULL':
#                     messages.success(
#                         request,
#                         'اهراز هویت با موفقیت تکمیل شد!'
#                     )
#                     return redirect('acc:authentication_with_nation_cart_image')
                
#                 else:
#                     messages.warning(
#                         'خطا در سرور! لطفا مجدد تلاش نمایید'
#                     )
#                     model_img.delete()
#                     model_img.save()
#                     return redirect('acc:authentication_with_nation_cart_image')
                
#             else:
#                 response=views.compare_all_ocr_fields(request)
#                 if response == 'IMAGE NOT FUOND':
#                     messages.error(
#                         request,
#                         'عکس پیدا نشد!'
#                     )
#                     return redirect('')
                
#                 elif response == 'CANT READ IMAGE':
#                     messages.error(
#                         request,
#                         'عکس خوانا نیست!'
#                     )
#                     return redirect('acc:authentication_with_nation_cart_image')
                
#                 else:
#                     messages.info(
#                         request,
#                         f'{response}'
#                     )
#                     return redirect('acc:authentication_with_nation_cart_image')

#         else:
#             return render(
#                 request,
#                 'accaunts/auth_with_cart.html'
#             )    
        

    # <!-- {% if is_NationalIDAuthenticated %}
    # <a href="{% url 'acc:authentication_with_nation_cart_image' %}" class="block p-3 pr-12 text-[#0bffffaa] hover:text-[#0bffff] hover:bg-[#0b142144] rounded-lg transition-all duration-300 sidebar-item">
    #     <i class="bi bi-person-vcard ml-2"></i>
    #     اهراز هویت با کارت ملی
    # </a>
    # {% endif %} -->