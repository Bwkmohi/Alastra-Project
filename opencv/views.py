import pytesseract
from accaunts.models import NationalIDAuthentication,UserAuthentication
import pytesseract, cv2, re
from fuzzywuzzy import fuzz
# pytesseract نصب اپ و در C:\Program Files\Tesseract-OCR باید قرار بگیره 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
from accaunts.check_auth import check_user



# استخراج متن از تصویر کارت ملی
def ocr_authenticate_from_image(request):
    user = check_user(request) 

    if not user:
        return 'ERROR'

    try:
        image_model = NationalIDAuthentication.objects.get(user=user)
        image_path = image_model.national_id_image.path
    except NationalIDAuthentication.DoesNotExist:
        return 'IMAGE NOT FUOND'
    
    image = cv2.imread(image_path)
    if image is None:
        return 'CANT READ IMAGE'


    text = pytesseract.image_to_string(image, lang='fas')
    print(" متن :", text)
    print(" متن :", text)
    print(" متن :", text)
    print(" متن :", text)
    print(" متن :", text)


    national_code = re.search(r'\d{10}', text)

    user_authentication = UserAuthentication.objects.create(
        user=user,
        national_code=national_code.group() if national_code else "0000000000",
        address="شناسایی نشده", 
        city="نامشخص",
        postal_code="00000"
    )
 
    image_model.user_authentication = user_authentication
    image_model.is_verified = True
    image_model.save()

    return 'AUTH BE SUCCESS FULL'


 



def addd(request):
    user = check_user(request)
    result = []

    try:
        image_model = NationalIDAuthentication.objects.get(user=user)
        image_path = image_model.national_id_image.path
    except NationalIDAuthentication.DoesNotExist:
        return 'IMAGE NOT FUOND'

    image = cv2.imread(image_path)
    if image is None:
        return 'CANT READ IMAGE'

    text = pytesseract.image_to_string(image, lang='fas')
    print("Text:\n", text)

    # print(re.search(r'محم', text),'mohammad march isssss')
    name_match = re.search(r'نام\s*[:\-]?\s*(\w+)', text)
    last_name_match = re.search(r'نام خانوادگی\s*[:\-]?\s*(\w+)', text)
    national_code_match = re.search(r'\d{10}', text)
    year_match = re.search(r'13[0-9]{2}', text)

    print('name_match',name_match)
    print('last_name_match',last_name_match)
    print('national_code_match',national_code_match)


    extracted_name = name_match.group(1) if name_match else ""
    extracted_last_name = last_name_match.group(1) if last_name_match else ""
    extracted_national_code = national_code_match.group(0) if national_code_match else ""
    extracted_year = int(year_match.group(0)) if year_match else None
    
    print(extracted_name,extracted_last_name,extracted_national_code,extracted_year)

    auth = UserAuthentication.objects.get(user=user)

    

    # نام
    name_score = fuzz.ratio(extracted_name, user.first_name)
    result.append(f"{'success' if name_score >= 85 else 'faild'} نام ({extracted_name} ↔ {user.first_name})")

    # نام خانوادگی
    last_name_score = fuzz.ratio(extracted_last_name, user.last_name)
    result.append(f"{'success' if last_name_score >= 85 else 'faild'} نام خانوادگی ({extracted_last_name} ↔ {user.last_name})")

    # کد ملی
    code_ok = extracted_national_code == auth.national_code
    result.append(f"{'success' if code_ok else 'faild'} کد ملی ({extracted_national_code} ↔ {auth.national_code})")

    # سال تولد
    year_ok = extracted_year == auth.age.year if extracted_year else False
    result.append(f"{'success' if year_ok else 'faild'} سال تولد ({extracted_year} ↔ {auth.age.year})")

    # آیا تمام فیلدها مطابقت داشتن؟
    all_match = code_ok and year_ok
    user_match= name_score >= 85 and last_name_score >= 85

    print(user_match,'user_match')
    print(all_match,'all_match')
    print('code_ok',code_ok)

    image_model.user_authentication = all_match
    user = user_match
    image_model.save()

    result.append(" احراز کامل شد." if all_match else "عدم انتقاب در اطلاعات ")
    return result


def compare_all_ocr_fields(request):
    user = check_user(request)
    result = []

    try:
        image_model = NationalIDAuthentication.objects.get(user=user)
        image_path = image_model.national_id_image.path
    except NationalIDAuthentication.DoesNotExist:
        return 'IMAGE NOT FUOND'

    image = cv2.imread(image_path)
    if image is None:
            return 'CANT READ IMAGE'
    # بررسی متن استخراج شده و تنظیمات بهتر
    text = pytesseract.image_to_string(image, lang='fas')
    text = text.replace("\n", " ").replace("\r", "")
    print("Extracted Text after OCR:\n", text)

    # تلاش برای استخراج کلمات خاص
    name_match = re.search(r'نام\s*[:\-]?\s*([^\s:؛]+)', text)
    last_name_match = re.search(r'نام خانوادگی\s*[:\-]?\s*([^\s:؛]+)', text)
    national_code_match = re.search(r'\d{10}', text)
    year_match = re.search(r'13[0-9]{2}', text)

    print('name_match:', name_match)
    print('last_name_match:', last_name_match)
    print('national_code_match:', national_code_match)



    extracted_name = name_match.group(1) if name_match else ""
    extracted_last_name = last_name_match.group(1) if last_name_match else ""
    extracted_national_code = national_code_match.group(0) if national_code_match else ""
    extracted_year = int(year_match.group(0)) if year_match else None
    
    print(extracted_name,extracted_last_name,extracted_national_code)

    auth = UserAuthentication.objects.get(user=user)

    # مور ی املی‌دان. شماره ملی,  َ باس تسش رل هید  محمد  : ایرانی  هدس روج اله شمه مس  2 ایا

    # نام
    name_score = fuzz.ratio(extracted_name, user.first_name)
    result.append(f"{'success' if name_score >= 85 else 'faild'} نام ({extracted_name} ↔ {user.first_name})")

    # نام خانوادگی
    last_name_score = fuzz.ratio(extracted_last_name, user.last_name)
    result.append(f"{'success' if last_name_score >= 85 else 'faild'} نام خانوادگی ({extracted_last_name} ↔ {user.last_name})")

    # کد ملی
    code_ok = extracted_national_code == auth.national_code
    result.append(f"{'success' if code_ok else 'faild'} کد ملی ({extracted_national_code} ↔ {auth.national_code})")

    # سال تولد
    year_ok = extracted_year == auth.age.year if extracted_year else False
    result.append(f"{'success' if year_ok else 'faild'} سال تولد ({extracted_year} ↔ {auth.age.year})")

    # آیا تمام فیلدها مطابقت داشتن؟
    all_match = code_ok and year_ok
    user_match= name_score >= 85 and last_name_score >= 85

    print(user_match,'user_match')
    print(all_match,'all_match')
    print('code_ok',code_ok)

    image_model.user_authentication = all_match
    user = user_match
    image_model.save()

    result.append(" احراز کامل شد." if all_match else "عدم انتقاب در اطلاعات ")
    return result

