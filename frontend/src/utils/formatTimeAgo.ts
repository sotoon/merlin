const UNITS: Intl.RelativeTimeFormatUnit[] = [
  'second',
  'minute',
  'hour',
  'day',
  'week',
  'month',
  'year',
];

const CUTOFFS = [60, 3600, 86400, 86400 * 7, 86400 * 30, 86400 * 365, Infinity];

/**
 * Convert a date to a relative time string
 * @param date Date or timestamp in milliseconds
 * @param lang Language code (defaults to navigator.language)
 * @returns Relative time string
 */
export function formatTimeAgo(
  date: Date | number,
  lang = navigator.language,
): string {
  const timeMs = typeof date === 'number' ? date : date.getTime();
  const deltaSeconds = Math.round((timeMs - Date.now()) / 1000);

  const unitIndex = CUTOFFS.findIndex(
    (cutoff) => cutoff > Math.abs(deltaSeconds),
  );
  const divisor = unitIndex ? CUTOFFS[unitIndex - 1] : 1;

  const rtf = new Intl.RelativeTimeFormat(lang);

  return rtf.format(Math.floor(deltaSeconds / divisor), UNITS[unitIndex]);
}
