import type { components } from '~/types/schema';

declare interface AuthTokens {
  access: string | null;
  refresh: string | null;
}

declare interface AuthStore {
  readonly tokens: Readonly<AuthTokens>;
  readonly setTokens: (tokens: Partial<AuthTokens>) => void;
  readonly removeTokens: () => void;
}

type AllSchemas = components['schemas'];

declare global {
  export type Schema<T extends keyof AllSchemas> = AllSchemas[T];
}
