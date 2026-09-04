import type { PropsWithChildren, ReactNode } from 'react';
import {
  IonButton,
  IonButtons,
  IonContent,
  IonHeader,
  IonPage,
  IonTitle,
  IonToolbar,
} from '@ionic/react';
import { useNavigate } from 'react-router-dom';

interface AppPageProps extends PropsWithChildren {
  titulo: string;
  subtitulo?: string;
  volverA?: string;
  acciones?: ReactNode;
}

export function AppPage({ titulo, subtitulo, volverA, acciones, children }: AppPageProps) {
  const navigate = useNavigate();
  return (
    <IonPage>
      <IonHeader translucent>
        <IonToolbar>
          {volverA && (
            <IonButtons slot="start">
              <IonButton aria-label="Volver" onClick={() => navigate(volverA)}>
                Volver
              </IonButton>
            </IonButtons>
          )}
          <IonTitle>
            <span className="toolbar-title">{titulo}</span>
            {subtitulo && <small>{subtitulo}</small>}
          </IonTitle>
          {acciones && <IonButtons slot="end">{acciones}</IonButtons>}
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen className="app-content">
        <div className="content-shell">{children}</div>
      </IonContent>
    </IonPage>
  );
}
