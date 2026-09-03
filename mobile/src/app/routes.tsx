import { IonRouterOutlet } from '@ionic/react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { LoginPage } from '../features/auth/LoginPage';
import { BorradoresPage } from '../features/capture/BorradoresPage';
import { CompletarNovedadPage } from '../features/capture/CompletarNovedadPage';
import { NuevaNovedadPage } from '../features/capture/NuevaNovedadPage';
import { DetalleNovedadPage } from '../features/history/DetalleNovedadPage';
import { HistoricoPage } from '../features/history/HistoricoPage';
import { InicioPage } from '../features/home/InicioPage';
import { ProtectedRoute } from '../shared/components/ProtectedRoute';

function protegida(elemento: React.ReactElement) {
  return <ProtectedRoute>{elemento}</ProtectedRoute>;
}

export function AppRoutes() {
  return (
    <IonRouterOutlet>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/inicio" element={protegida(<InicioPage />)} />
        <Route path="/nueva" element={protegida(<NuevaNovedadPage />)} />
        <Route path="/borradores" element={protegida(<BorradoresPage />)} />
        <Route path="/borradores/:id" element={protegida(<CompletarNovedadPage />)} />
        <Route path="/historico" element={protegida(<HistoricoPage />)} />
        <Route path="/historico/:id" element={protegida(<DetalleNovedadPage />)} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </IonRouterOutlet>
  );
}
