import { Navigate } from 'react-router-dom';
import { isTokenValid } from '../utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = localStorage.getItem('access_token');
  if (!isTokenValid(token)) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}
