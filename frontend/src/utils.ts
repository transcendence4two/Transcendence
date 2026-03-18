/**
 * Converts a MinIO direct URL (http://localhost:9000/avatars/...)
 * to a relative path (/avatars/...) served through the HTTPS nginx proxy.
 */
export function normalizeAvatarUrl(url?: string | null): string {
  if (!url) return "";
  const trimmed = url.trim();
  try {
    const parsed = new URL(trimmed);
    return parsed.pathname;
  } catch {
    return trimmed;
  }
}
