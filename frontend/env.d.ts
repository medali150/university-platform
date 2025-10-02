interface ImportMetaEnv {
  readonly NEXT_PUBLIC_API_URL: string
  readonly TOKEN_REFRESH_MARGIN_MS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}