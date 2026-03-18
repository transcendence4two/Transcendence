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
