[app]

# عنوان التطبيق
title = instagram_info
# اسم الحزمة (يجب أن يكون فريداً)
package.name = myapp

# النطاق (استخدم اسمك العكسي)
package.domain = org.example

# المسار الرئيسي
source.dir = .

# الملف الرئيسي
source.main = main.py

# الإصدار
version = 0.1

# المتطلبات (المكتبات)
requirements = python3,kivy

# نظام التشغيل المستهدف
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]

# مستوى التسجيل
log_level = 2
