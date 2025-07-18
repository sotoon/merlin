export const ONE_ON_ONE_PLACEHOLDERS = {
  personal_summary: `در مورد چی صحبت کردیم؟
  • خستگی ذهنی بعد از تحویل چند پروژه پشت سر هم
  • سختی در حفظ تمرکز و پیش بردن چند کار همزمان
  • برنامه‌ریزی برای مرخصی کوتاه برای استراحت
  
  چه مشاهده و مصداق‌هایی داریم؟
  • در دو هفته اخیر، پیش نرفتن کارها با اولویت‌هایی که مشخص کرده بودیم
  • کندی در پاسخ‌گویی به تغییراتی که نیاز به بهبود بود
  • خود فرد اشاره کرده تکراری بودن تسک‌ها و کارهای سمتش باعث خستگی و کاهش انگیزه‌اش شده
  
  وصل می‌شه به:
  تگ: تعادل کار-زندگی`,

  career_summary: `در مورد چی صحبت کردیم؟
  • علاقه‌مندی به یادگیری مهارت لیدرشیپ در پروژه‌های کوچک
  • آمادگی برای هدایت یک sub-project در فصل آینده
  • نیاز به یادگیری ابزار X برای مدیریت تسک‌ها
  
  چه مشاهده و مصداق‌هایی داریم؟
  • در جلسه پلنینگ اخیر، خودش داوطلب شد که هدایت برنامه‌ریزی رو انجام بده
  • در جلسه‌ی رترو ایده‌ی خوبی برای بهبود روند داده بود
  
  وصل می‌شه به:
  تگ: آمادگی و داوطلب شدن مسئولیت‌های جدید`,

  communication_summary: `در مورد چی صحبت کردیم؟
  • چالش در ارتباط با اینسیدنت اخیر و چگونگی پیش‌بردش
  • نحوه مدیریت تعارض در جلسه‌های بین تیمی
  
  چه مشاهده و مصداق‌هایی داریم؟
  • در جلسه بررسی اینسیدنت، پاسخ‌گویی به سوالات مبهم و بدون شفافیت
  • چند مورد سوءتفاهم بین خودش و PM
  • خود فرد گفت گاهی نمی‌دونه چطور درخواست‌ها رو به شکل درست مطرح کنه
  
  وصل می‌شه به:
  تگ: تعامل مناسب با ذی‌نفعان`,

  performance_summary: `در مورد چی صحبت کردیم؟
  • بررسی کیفیت تحویل‌ها در پلنینگ اخیر
  • تفاوت بین تخمین اولیه و زمان واقعی انجام تسک‌ها
  • دقت در مستندسازی فنی تسک
  
  چه مشاهده و مصداق‌هایی داریم؟
  • رسیدن یک تسک با تأخیر پنج روزه به دلیل ابهام در نیازمندی‌ها
  • مستندات قبلی فقط ۳۰٪ پوشش داشته
  
  وصل می‌شه به:
  تگ: کیفیت خروجی و تحویل کار`,

  actions: `اقدامات تعریف شده:
  • برای شفاف‌سازی نیازمندی‌ها → مشارکت در جلسه‌ی ریفاینمنت
  • تهیه چک‌لیست ساده برای تحویل مستندات
  • معرفی به عنوان مسئول sub-project Z برای ماه آینده → پیگیری با تیم لیدر
  • ثبت‌نام در دوره آنلاین Project Management Basics → پیگیری با خود فرد
  • گرفتن بازخورد از اعضای تیم بعد از ۲ هفته → جمع‌آوری
  • شرکت در جلسه هفتگی تیم محصول برای هم‌راستایی بیشتر
  • تنظیم یک مستند استاندارد برای ارائه تغییرات به مشتری`,

  extra_notes: `یادداشت‌های اضافی:
  • نکات مهم که در بخش‌های دیگر جا نگرفت
  • موارد خاص یا استثنایی
  • پیشنهادات برای جلسات آینده
  • یادآوری‌های مهم`,
} as const;

// Helper function to get placeholder by field name
export function getPlaceholder(
  fieldName: keyof typeof ONE_ON_ONE_PLACEHOLDERS,
): string {
  return ONE_ON_ONE_PLACEHOLDERS[fieldName];
}
