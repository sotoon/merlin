import introJs from 'intro.js';
import type { TourStep } from 'intro.js/src/packages/tour/steps.d.ts';
import type { MaybeRef } from 'vue';

function createGuiderTitle() {
  return `<img 
        src="/merlin.jpg" 
        alt="Merlin" 
        style="width: 35px; height: 35px; border-radius: 50%; margin-right: auto; margin-left: -34px;" 
    />`;
}

export function useIntro(
  steps: MaybeRef<Omit<TourStep, 'title' | 'position' | 'scrollTo'>[]>,
  guideKey: string,
  options?: { disableScrolling?: boolean },
) {
  const intro = inject('intro') as typeof introJs;
  const introInstance = intro.tour();

  introInstance.onComplete(() => {
    localStorage.setItem(guideKey, 'true');
  });
  introInstance.onExit(() => {
    localStorage.setItem(guideKey, 'true');
  });

  watch(
    () => unref(steps),
    (currentSteps) => {
      introInstance.setOptions({
        steps: currentSteps.map((step) => ({
          ...step,
          position: 'top',
          scrollTo: 'element',
          title: createGuiderTitle(),
        })),
        nextLabel: 'بعدی',
        prevLabel: 'قبلی',
        doneLabel: 'پایان',
        showBullets: false,
        buttonClass: 'intro-button',
        scrollToElement: !options?.disableScrolling,
      });
    },
    { immediate: true, deep: true },
  );

  const start = () => {
    if (localStorage.getItem(guideKey) || unref(steps).length === 0) {
      return;
    }
    introInstance.start();
  };

  return {
    start,
  };
}
