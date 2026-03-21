export function isTokenValid(token: string | null): boolean {
  if (!token) return false;
  try {
    const base64Payload = token.split('.')[1];
    if (!base64Payload) return false;
    const payload = JSON.parse(
      atob(base64Payload.replace(/-/g, '+').replace(/_/g, '/'))
    );
    return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now();
  } catch {
    return false;
  }
}
