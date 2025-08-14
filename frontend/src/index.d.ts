import type { components, operations } from '~/types/schema';

type AllSchemas = components['schemas'];
type AllOperations = operations;

declare global {
  export type Schema<T extends keyof AllSchemas> = AllSchemas[T];
  export type Operation<T extends keyof AllOperations> = AllOperations[T];
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
