import type { components } from '~/types/schema';

type AllSchemas = components['schemas'];

declare global {
  export type Schema<T extends keyof AllSchemas> = AllSchemas[T];
  export interface AuthStore {
    readonly tokens: Readonly<AuthTokens>;
    readonly setTokens: (tokens: Partial<AuthTokens>) => void;
    readonly removeTokens: () => void;
  }
  export interface AuthTokens {
    access: string | null;
    refresh: string | null;
  }
}
