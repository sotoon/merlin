declare interface AuthTokens {
  access: string | null;
  refresh: string | null;
}

declare interface AuthStore {
  readonly tokens: Readonly<AuthTokens>;
  readonly setTokens: (tokens: Partial<AuthTokens>) => void;
  readonly removeTokens: () => void;
}
