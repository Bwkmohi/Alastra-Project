import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def validate_national_card_info(user_auth, extracted_text):
    errors = []
 
    if user_auth.national_code not in extracted_text:
        errors.append("کد ملی با تصویر مطابقت ندارد")
 
    full_name = f"{user_auth.user.first_name} {user_auth.user.last_name}"
    if full_name.strip() not in extracted_text:
        errors.append("نام و نام خانوادگی با تصویر مطابقت ندارد")
 
    if user_auth.age and str(user_auth.age.year) not in extracted_text:
        errors.append("تاریخ تولد با تصویر مطابقت ندارد")

    return errors