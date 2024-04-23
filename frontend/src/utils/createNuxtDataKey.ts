/**
 * Create a key to use for Nuxt data (`useFetch`, `useLazyFetch`, etc.) from a hierarchical data key
 * @param dataKey a data key or array of hierarchical keys
 * @returns Unique key in the form of `dataKey[0]:dataKey[1]:...:dataKey[n]`
 */
export const createNuxtDataKey = (dataKey: string | unknown[]): string =>
  Array.isArray(dataKey) ? dataKey.map((k) => k ?? '').join(':') : dataKey;
