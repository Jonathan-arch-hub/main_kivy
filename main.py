from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.clipboard import Clipboard
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import instaloader
import requests
from io import BytesIO
import re
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# تسجيل خط عربي
LabelBase.register(name='Arabic', fn_regular='NotoNaskhArabic-VariableFont_wght.ttf')

def ar(text):
    """دالة معالجة النص العربي"""
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text

class InstagramInfoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.L = instaloader.Instaloader()
        self.current_profile = None
        self.current_profile_pic_url = None
        self.current_username = ""

    def build(self):
        # التخطيط الرئيسي
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # شريط العنوان
        title_label = Label(
            text=ar("Instagram Info Pro"),
            font_name='Arabic',
            font_size='30sp',
            size_hint=(1, 0.1),
            color=(0.9, 0.1, 0.1, 1)
        )
        main_layout.add_widget(title_label)
        
        # تخطيط المحتوى
        content_layout = BoxLayout(orientation='horizontal', spacing=10)
        
        # الجانب الأيسر (معلومات المستخدم)
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        
        # شريط البحث
        search_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        self.username_input = TextInput(
            hint_text=ar("أدخل اسم مستخدم Instagram"),
            font_name='Arabic',
            font_size='16sp',
            size_hint=(0.7, 1),
            multiline=False
        )
        self.search_btn = Button(
            text=ar("بحث"),
            font_name='Arabic',
            font_size='16sp',
            size_hint=(0.3, 1),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.search_btn.bind(on_press=self.fetch_user_info)
        search_layout.add_widget(self.username_input)
        search_layout.add_widget(self.search_btn)
        left_panel.add_widget(search_layout)
        
        # منطقة التمرير للمعلومات
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.info_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.info_layout.bind(minimum_height=self.info_layout.setter('height'))
        
        self.scroll_view.add_widget(self.info_layout)
        left_panel.add_widget(self.scroll_view)
        
        # الجانب الأيمن (صورة الملف الشخصي)
        right_panel = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=10)
        
        # صورة الملف الشخصي
        self.profile_image = Image(
            source='',  # سيتم تعيينها لاحقاً
            size_hint=(1, 0.7),
            allow_stretch=True
        )
        right_panel.add_widget(self.profile_image)
        
        # زر تنزيل الصورة
        self.download_btn = Button(
            text=ar("📥 تنزيل الصورة"),
            font_name='Arabic',
            font_size='16sp',
            size_hint=(1, 0.1),
            background_color=(0.9, 0.3, 0.2, 1)
        )
        self.download_btn.bind(on_press=self.download_profile_pic)
        right_panel.add_widget(self.download_btn)
        
        # زر نسخ جميع المعلومات
        self.copy_all_btn = Button(
            text=ar("نسخ جميع المعلومات"),
            font_name='Arabic',
            font_size='16sp',
            size_hint=(1, 0.1),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.copy_all_btn.bind(on_press=self.copy_all_info)
        right_panel.add_widget(self.copy_all_btn)
        
        content_layout.add_widget(left_panel)
        content_layout.add_widget(right_panel)
        main_layout.add_widget(content_layout)
        
        # عرض رسالة ترحيبية
        self.show_welcome_message()
        
        return main_layout
    
    def show_welcome_message(self):
        """عرض رسالة ترحيبية"""
        welcome_text = ar("""
        مرحباً بك في Instagram Info Pro
        
        أدخل اسم مستخدم Instagram في الحقل أعلاه
        ثم انقر على زر 'بحث' لاستعراض المعلومات
        
        المميزات:
        • عرض معلومات الملف الشخصي
        • تحميل صورة الملف الشخصي
        • نسخ المعلومات إلى الحافظة
        • دعم كامل للغة العربية
        """)
        
        welcome_label = Label(
            text=welcome_text,
            font_name='Arabic',
            font_size='16sp',
            size_hint_y=None,
            height=300,
            text_size=(400, None),
            halign='center',
            valign='middle'
        )
        self.info_layout.add_widget(welcome_label)
    
    def clear_info_layout(self):
        """مسح المعلومات السابقة"""
        self.info_layout.clear_widgets()
    
    def create_info_section(self, title, content, copyable=True):
        """إنشاء قسم للمعلومات"""
        section_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
        
        # العنوان
        title_label = Label(
            text=ar(title),
            font_name='Arabic',
            font_size='14sp',
            size_hint=(1, 0.4),
            color=(0.2, 0.4, 0.8, 1)
        )
        section_layout.add_widget(title_label)
        
        # المحتوى
        content_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6))
        content_label = Label(
            text=ar(str(content)),
            font_name='Arabic',
            font_size='16sp',
            size_hint=(0.8, 1)
        )
        content_layout.add_widget(content_label)
        
        # زر النسخ إذا كان قابلاً للنسخ
        if copyable:
            copy_btn = Button(
                text=ar("📋"),
                font_name='Arabic',
                font_size='14sp',
                size_hint=(0.2, 1),
                background_color=(0.3, 0.5, 0.9, 1)
            )
            copy_btn.bind(on_press=lambda x: self.copy_to_clipboard(str(content)))
            content_layout.add_widget(copy_btn)
        
        section_layout.add_widget(content_layout)
        return section_layout
    
    def fetch_user_info(self, instance):
        """جلب معلومات المستخدم"""
        username = self.username_input.text.strip()
        if not username:
            self.show_error(ar("يرجى إدخال اسم مستخدم"))
            return
        
        # مسح المعلومات السابقة
        self.clear_info_layout()
        
        # عرض رسالة تحميل
        loading_label = Label(
            text=ar("جاري جلب المعلومات..."),
            font_name='Arabic',
            font_size='18sp',
            color=(0.8, 0.5, 0.1, 1)
        )
        self.info_layout.add_widget(loading_label)
        
        # تأخير التنفيذ لتجنب تجميد الواجهة
        Clock.schedule_once(lambda dt: self._fetch_user_info_async(username), 0.1)
    
    def _fetch_user_info_async(self, username):
        """جلب المعلومات بشكل غير متزامن"""
        try:
            # جلب معلومات الملف الشخصي
            profile = instaloader.Profile.from_username(self.L.context, username)
            self.current_profile = profile
            self.current_username = username
            
            # مسح رسالة التحميل
            self.clear_info_layout()
            
            # المعلومات الأساسية
            self.info_layout.add_widget(self.create_info_section("المتابعون", f"{profile.followers:,}"))
            self.info_layout.add_widget(self.create_info_section("المتابعين", f"{profile.followees:,}"))
            self.info_layout.add_widget(self.create_info_section("المنشورات", f"{profile.mediacount:,}"))
            
            # المعلومات الإضافية
            fullname = profile.full_name if profile.full_name else "غير متوفر"
            self.info_layout.add_widget(self.create_info_section("الاسم الكامل", fullname))
            
            private_status = "نعم" if profile.is_private else "لا"
            self.info_layout.add_widget(self.create_info_section("حساب خاص", private_status))
            
            verified_status = "نعم" if profile.is_verified else "لا"
            self.info_layout.add_widget(self.create_info_section("حساب مؤكد", verified_status))
            
            # البايو
            bio = profile.biography if profile.biography else "لا يوجد وصف"
            self.info_layout.add_widget(self.create_info_section("الوصف (البايو)", bio))
            
            # استخراج الهاشتاجات
            hashtags = re.findall(r'#\w+', bio)
            hashtags_text = ', '.join(hashtags[:5]) + ('...' if len(hashtags) > 5 else '')
            if hashtags:
                self.info_layout.add_widget(self.create_info_section("الهاشتاجات", hashtags_text))
            
            # الرابط الخارجي
            external_url = profile.external_url if profile.external_url else "غير متوفر"
            self.info_layout.add_widget(self.create_info_section("رابط خارجي", external_url))
            
            # تحميل صورة الملف الشخصي
            if profile.profile_pic_url:
                self.current_profile_pic_url = profile.profile_pic_url
                Clock.schedule_once(lambda dt: self._load_profile_image(profile.profile_pic_url), 0.1)
            
            self.show_success(ar(f"تم جلب معلومات {username} بنجاح"))
            
        except instaloader.exceptions.ProfileNotExistsException:
            self.show_error(ar("المستخدم غير موجود"))
        except instaloader.exceptions.ConnectionException:
            self.show_error(ar("مشكلة في الاتصال بالإنترنت"))
        except Exception as e:
            self.show_error(ar(f"حدث خطأ: {str(e)}"))
    
    def _load_profile_image(self, url):
        """تحميل صورة الملف الشخصي"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # حفظ الصورة مؤقتاً وعرضها
                with open('temp_profile_pic.jpg', 'wb') as f:
                    f.write(response.content)
                self.profile_image.source = 'temp_profile_pic.jpg'
                self.profile_image.reload()
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
    
    def download_profile_pic(self, instance):
        """تنزيل صورة الملف الشخصي"""
        if not self.current_profile_pic_url:
            self.show_error(ar("لا توجد صورة للتنزيل"))
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.current_username}_profile_{timestamp}.jpg"
            
            response = requests.get(self.current_profile_pic_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                self.show_success(ar(f"تم تنزيل الصورة كـ: {filename}"))
            else:
                self.show_error(ar("فشل في تنزيل الصورة"))
                
        except Exception as e:
            self.show_error(ar(f"حدث خطأ أثناء التنزيل: {str(e)}"))
    
    def copy_to_clipboard(self, text):
        """نسخ النص إلى الحافظة"""
        Clipboard.copy(text)
        self.show_success(ar("تم النسخ إلى الحافظة"))
    
    def copy_all_info(self, instance):
        """نسخ جميع المعلومات"""
        if not self.current_profile:
            self.show_error(ar("لا توجد معلومات للنسخ"))
            return
        
        try:
            info_text = f"معلومات حساب Instagram: {self.current_username}\n"
            info_text += "=" * 50 + "\n"
            info_text += f"المتابعون: {self.current_profile.followers:,}\n"
            info_text += f"المتابعين: {self.current_profile.followees:,}\n"
            info_text += f"المنشورات: {self.current_profile.mediacount:,}\n"
            info_text += f"الاسم الكامل: {self.current_profile.full_name}\n"
            info_text += f"حساب خاص: {'نعم' if self.current_profile.is_private else 'لا'}\n"
            info_text += f"حساب مؤكد: {'نعم' if self.current_profile.is_verified else 'لا'}\n"
            info_text += f"الوصف: {self.current_profile.biography}\n"
            info_text += f"رابط خارجي: {self.current_profile.external_url}\n"
            
            self.copy_to_clipboard(info_text)
            self.show_success(ar("تم نسخ جميع المعلومات إلى الحافظة"))
            
        except Exception as e:
            self.show_error(ar(f"حدث خطأ أثناء النسخ: {str(e)}"))
    
    def show_error(self, message):
        """عرض رسالة خطأ"""
        self.clear_info_layout()
        error_label = Label(
            text=message,
            font_name='Arabic',
            font_size='18sp',
            color=(0.9, 0.1, 0.1, 1),
            size_hint_y=None,
            height=100
        )
        self.info_layout.add_widget(error_label)
    
    def show_success(self, message):
        """عرض رسالة نجاح"""
        success_label = Label(
            text=message,
            font_name='Arabic',
            font_size='16sp',
            color=(0.1, 0.7, 0.1, 1),
            size_hint_y=None,
            height=50
        )
        self.info_layout.add_widget(success_label)

if __name__ == '__main__':
    InstagramInfoApp().run()
