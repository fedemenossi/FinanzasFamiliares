export {};

declare global {
  interface Window {
    __AFFIA_CONFIG__?: {
      NEXT_PUBLIC_API_URL?: string;
    };
  }
}
