import { IonApp } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { DemoSessionProvider } from '../features/auth/demoSession';
import { NovedadesProvider } from '../state/NovedadesProvider';
import { AppRoutes } from './routes';

export function App() {
  return (
    <IonApp>
      <IonReactRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <DemoSessionProvider>
          <NovedadesProvider>
            <AppRoutes />
          </NovedadesProvider>
        </DemoSessionProvider>
      </IonReactRouter>
    </IonApp>
  );
}
