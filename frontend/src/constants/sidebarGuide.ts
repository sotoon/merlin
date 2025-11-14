type TourStep = {
  element: string;
  intro: string;
  step: number;
};

export const SIDEBAR_TOUR_STEPS: Record<string, TourStep[]> = {
  notes: [
    {
      step: 1,
      element: '#sidebar-notes-goals',
      intro: 'اهداف خود و اعضای تیمتان را در این قسمت تعریف و پیگیری کنید.',
    },
    {
      step: 2,
      element: '#sidebar-notes-forms',
      intro: 'فرم‌های ارزیابی عملکرد در این قسمت قرار دارند.',
    },
    {
      step: 3,
      element: '#sidebar-notes-my-forms',
      intro:
        'نتایج فرم‌های ارزیابی خود و اعضای تیمتان را در این بخش مشاهده کنید.',
    },
  ],
  promotion: [
    {
      step: 1,
      element: '#sidebar-promotion-promotion',
      intro: 'پروپوزال‌های ارتقا در این بخش قرار دارند.',
    },
    {
      step: 2,
      element: '#sidebar-promotion-mapping',
      intro: 'پروپوزال‌های مپینگ در این بخش قرار دارند.',
    },
    {
      step: 3,
      element: '#sidebar-promotion-evaluation',
      intro: 'خودارزیابی‌ها در این بخش قرار دارند.',
    },
  ],
  feedback: [
    {
      step: 1,
      element: '#sidebar-feedback-feedback-request',
      intro: 'درخواست‌های بازخورد در این قسمت قرار دارند.',
    },
    {
      step: 2,
      element: '#sidebar-feedback-adhoc-feedback',
      intro: 'بازخوردهای مستقیم در این قسمت قرار دارند.',
    },
    {
      step: 3,
      element: '#sidebar-feedback-message',
      intro: 'پیام‌های شما در این قسمت قرار دارند.',
    },
  ],
  personal: [
    {
      step: 1,
      element: '#sidebar-personal-meetings',
      intro: 'جلسات خود را در این قسمت ثبت و مدیریت کنید.',
    },
    {
      step: 2,
      element: '#sidebar-personal-templates',
      intro: 'قالب‌های آماده برای یادداشت‌ها در این بخش قرار دارند.',
    },
  ],
  'my-team': [
    {
      step: 1,
      element: '#sidebar-my-team-my-team',
      intro: 'اطلاعات تیم خود را در این قسمت مشاهده کنید.',
    },
    {
      step: 2,
      element: '#sidebar-my-team-one-on-one',
      intro: 'جلسات یک به یک با اعضای تیمتان در این بخش قرار دارند.',
    },
  ],
};
