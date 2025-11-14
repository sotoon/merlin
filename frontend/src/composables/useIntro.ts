import introJs from 'intro.js';
import type { TourStep } from 'intro.js/src/packages/tour/steps.d.ts';

function createGuiderTitle() {
  return `<img 
        src="/merlin.jpg" 
        alt="Merlin" 
        style="width: 35px; height: 35px; border-radius: 50%; margin-right: auto; margin-left: -34px;" 
    />`;
}

export function useIntro(
  steps: Omit<TourStep, 'title' | 'position' | 'scrollTo'>[],
  guideKey: string,
) {
  const intro = inject('intro') as typeof introJs;

  const start = () => {
    if (localStorage.getItem(guideKey)) {
      return;
    }
    const introInstance = intro.tour();
    introInstance.setOptions({
      steps: steps.map((step) => ({
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
    });
    introInstance.onComplete(() => {
      localStorage.setItem(guideKey, 'true');
    });
    introInstance.onExit(() => {
      localStorage.setItem(guideKey, 'true');
    });
    introInstance.start();
  };

  return {
    start,
  };
}
