/**
 * Call `refreshNuxtData` for each key matching the given hierarchical data key
 * @param dataKey Data key or array of keys
 * @returns Promise that resolves when all keys have been invalidated
 */
export const invalidateNuxtData = (
  dataKey: string | unknown[],
): Promise<void> => {
  const key = createNuxtDataKey(dataKey);
  const availableKeys = Object.keys(useNuxtApp().payload.data);
  const invalidateKeys = availableKeys.filter((k) => k.startsWith(key));

  return refreshNuxtData(invalidateKeys);
};
