import type { ReactElement } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useDemoSession } from '../../features/auth/demoSession';

interface ProtectedRouteProps {
  children: ReactElement;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { usuario } = useDemoSession();
  const location = useLocation();
  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: location.pathname }} />;
  }
  return children;
}
