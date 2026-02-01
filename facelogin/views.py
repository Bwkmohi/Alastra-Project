from .models import UserFace
from django.shortcuts import render,redirect
from django.core.files.storage import default_storage
from accaunts.check_auth import check_user
from django.contrib import messages
from django.utils import timezone
# import deepface
from datetime import timedelta
import base64
from django.core.files.base import ContentFile
from siteinfo.systemsendmail import send_quick_mail
 

# برسی زمان وارد کردن رمز عبور
def check_time(request):
    user_pass = get_userface(request)
    if user_pass:
        if user_pass.active == True:
            time_passed = timezone.now() - user_pass.entred_password_at
            if user_pass.auto_lock_time:
                if time_passed > timedelta(minutes=user_pass.auto_lock_time):
                    return True
                return False
            return False
        return False
    return False



def get_userface(request):
    try:
        return UserFace.objects.get(user=check_user(request),)
    except UserFace.DoesNotExist:
        return False


 
def change_password(request):
    userface=get_userface(request)

    if not userface:
        return redirect('create_password')

    if not request.user.is_authenticated:
        return redirect('acc:pro')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_passwor2')

        if new_password != new_password2:
            messages.warning(
                request,
                'اشتباه در تکرار رمز عبور جدید!'
            )
            return redirect('change_password')

        if old_password == new_password:
            messages.warning(
                request,
                'رمز قبلی نمیتواند با رمز جدید مساوی باشد!'
            )
            return redirect('change_password')
        
        if old_password != userface.password:
            messages.error(
                request,
                'عدم انتباق رمز عبور قبلی'
            )
            return redirect('change_password')
        
        userface.password = new_password
        userface.is_entered = True
        userface.save()
        
        messages.success(
            request,
            'تغیر رمز عبور موفقیت امیز بود'
        )
        return redirect('acc:pro')
    
    return render(
        request,
        'facelogin/change_password.html',
    )



def create_password(request):
    user = check_user(request)

    if not user:
        return redirect('index')

    if get_userface(request):
        if get_userface(request).password:
            messages.warning(
                request,
                'شما قبلا برای خود پسورد ایجاد کرده اید!'
            )
            return redirect('acc:pro')

    if request.method == 'POST':
        auto_lock_time = request.POST.get('autoLockTime')
        auto_lock_time_int = int(auto_lock_time)

        if UserFace.objects.filter(user=user).exists():
            messages.warning(
                request,
                'شما قبلا برای خود رمز عبور ایجاد کردید'
            )
            return redirect('list_user_password')


        UserFace.objects.create(
            user=user,
            password=request.POST.get('password'),
            auto_lock_time=int(auto_lock_time_int),
            entred_password_at=timezone.now(),
            is_entered = True
        ) 
        messages.success(
            request,
            'رمز شما با موفقیت ساخته شد!'
        )
        return redirect('face_register') 


    return render(
        request,
        'facelogin/create_password.html'
    )
 


#  برسی زمان ورود رمز و وارد کردن رمز
def check_secure_and_enter_password(request,redirect_url):
    userface = get_userface(request)
    user = check_user(request)

    # اول برسی میکنه که ایا زمان اش رسیده است؟
    if redirect_url == 'self_function_checking':
        if userface:
            if userface.is_entered == False and userface.active == True:
                check_time(request)
                return True
        
            elif userface.is_entered == True:
                if check_time(request) == True: 
                    userface.is_entered = False
                    userface.save()
                    return False
        else:return redirect('create_password')

    elif request.method == 'POST':
        redirect_url_path=f'{redirect_url}'.replace('%','/')

        try:
            user_face_model=UserFace.objects.get(
                user=user,
                password__iexact=request.POST.get('password'),
            )

            user_face_model.entred_password_at=timezone.now()
            user_face_model.is_entered=True
            user_face_model.save()

            messages.success(
                request,
                'ورود موفق.'
            )
            return redirect(redirect_url_path)
        
        except UserFace.DoesNotExist:
            messages.error(
                request,
                'رمز نادرست است!'
            )
            return redirect('enter_password',redirect_url=f'{redirect_url}')
    # اگر زمانش رسیده است میبرد برای وارد کردن رمز عبور
    else:
        if userface:
            if userface.active == False:
                return redirect(f'{redirect_url}'.replace('%','/'))    
        else:return redirect(f'{redirect_url}'.replace('%','/'))

        if not user:return redirect('acc:login')
        
        return render(
            request,
            'facelogin/enter_password.html',
            {
                'redirect_path':redirect_url
            }
        )



def froget_password(request):
    user = check_user(request)
    userface = get_userface(request)

    if not user:
        return redirect('acc:lg:login')

    if not userface:
        return redirect('acc:login')
    
    send_quick_mail(
        subject='درخواست بازیابی رمز عبور',
        message=f'''
        <h2>
        سلام {user.get_full_name()}، <br>

        <h1> رمز عبور شما: {userface.password} </h1>
        <br><br><br>
        اگر این درخواست را شما ارسال نکرده‌اید، این ایمیل را نادیده بگیرید.
        <br>
        با تشکر،
        تیم پشتیبانی        
        </h2>

        ''',
        to_email=user.email
    )

    messages.success(
        request,
        'رمز عبور به ایمیل شما ارسال شد!'
    )
    return redirect('acc:pro')



def edit_password_data(request):
    user = check_user(request)
    userface = get_userface(request)

    if not user:return redirect('acc:lg:login')

    if not userface:return redirect('acc:login')
    
    if request.method == 'POST':
        auto_lock_time = request.POST.get('auto_lock_time')
        active = bool(request.POST.get('active'))

        userface.auto_lock_time = auto_lock_time
        userface.active = active
        userface.save()
        
        return redirect('acc:pro')

    return render(
        request,
        'facelogin/edit_password_data.html',
        {
            'active':userface.active,
            'auto_lock_time':userface.auto_lock_time
        }
    )
    

#  ثبت چهره
def face_register(request):
    user = check_user(request)
    userface = get_userface(request)

    if not user:
        return redirect('acc:login')
    
    if not userface:
        return redirect('create_password')

    if request.method == 'POST':
        image_data = request.POST.get('face_image')

        if image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # png
            decoded_img = base64.b64decode(imgstr)
            file_name = 'temp_uploaded.' + ext
            uploaded_path = default_storage.save(file_name, ContentFile(decoded_img))
            
        if userface:
            userface.face_image = uploaded_path    
            userface.save()
        else:
            UserFace.objects.create(
                user = user,
                face_image = uploaded_path,
                entred_password_at = timezone.now(),
                is_is_entered = True
            )
        messages.success(
            request,
            'چهره با موفقیت ثبت شد!'
        )
    return render(
        request, 
        'facelogin/face_enter.html'
    )


# ورود با چهره 
def face_enter(request):
    user = check_user(request)
    user_face = get_userface(request)

    if not user:
        return redirect('acc:login')
    
    if not user_face:
        return redirect('create_password')

    if request.method == 'POST':
        image_data = request.POST.get('face_image')
        if image_data:
            # image_data به شکل data:image/png;base64,iVBORw0...
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]  # png
            decoded_img = base64.b64decode(imgstr)
            file_name = 'temp_uploaded.' + ext
            # ذخیره فایل موقت
            uploaded_path = default_storage.save(file_name, ContentFile(decoded_img))
            # result = deepface.verify(img1_path=user_face.face_image.path, img2_path=default_storage.path(uploaded_path), enforce_detection=False)

            # if result["verified"]:
            #     user_face.is_entered = True
            #     user_face.save()
            #     messages.success(request, 'ورود موفقیت آمیز!')
            #     return redirect('پ')

            messages.warning(
                request, 
                'چهره با هیچ حسابی مطابقت ندارد.'
            )
            return redirect('face_enter')
    
    return render(
        request, 
        'facelogin/face_enter.html'
    )
