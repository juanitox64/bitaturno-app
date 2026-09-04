import {
  IonButton,
  IonCard,
  IonCardContent,
  IonIcon,
  IonItem,
  IonLabel,
  IonList,
} from '@ionic/react';
import {
  addCircleOutline,
  clipboardOutline,
  documentTextOutline,
  logOutOutline,
  refreshOutline,
} from 'ionicons/icons';
import { useNavigate } from 'react-router-dom';
import { useDemoSession } from '../auth/demoSession';
import { AppPage } from '../../shared/components/AppPage';
import { useNovedades } from '../../state/useNovedades';

export function InicioPage() {
  const { usuario, cerrar } = useDemoSession();
  const { borradores, finalizadas, reiniciarDemostracion } = useNovedades();
  const navigate = useNavigate();

  const salir = () => {
    cerrar();
    navigate('/login', { replace: true });
  };

  return (
    <AppPage
      titulo="Mi jornada"
      subtitulo="BitaTurno móvil"
      acciones={(
        <IonButton aria-label="Cerrar sesión" onClick={salir}>
          <IonIcon slot="icon-only" icon={logOutOutline} />
        </IonButton>
      )}
    >
      <section className="welcome-panel">
        <p className="eyebrow">Sesión demostrativa</p>
        <h1>Hola, {usuario}</h1>
        <p>Base híbrida local para registrar novedades con datos ficticios.</p>
      </section>

      <section className="metric-grid" aria-label="Resumen de novedades">
        <IonCard>
          <IonCardContent><strong>{borradores.length}</strong><span>Borradores</span></IonCardContent>
        </IonCard>
        <IonCard>
          <IonCardContent><strong>{finalizadas.length}</strong><span>Finalizadas</span></IonCardContent>
        </IonCard>
      </section>

      <IonButton expand="block" routerLink="/nueva" className="primary-action">
        <IonIcon slot="start" icon={addCircleOutline} />
        Nueva novedad
      </IonButton>

      <h2>Accesos de la jornada</h2>
      <IonList className="action-list" inset>
        <IonItem button detail routerLink="/borradores">
          <IonIcon slot="start" icon={clipboardOutline} />
          <IonLabel><strong>Mis borradores</strong><p>Continúe registros incompletos</p></IonLabel>
        </IonItem>
        <IonItem button detail routerLink="/historico">
          <IonIcon slot="start" icon={documentTextOutline} />
          <IonLabel><strong>Histórico</strong><p>Consulte novedades finalizadas</p></IonLabel>
        </IonItem>
      </IonList>

      <IonButton fill="clear" expand="block" onClick={reiniciarDemostracion}>
        <IonIcon slot="start" icon={refreshOutline} />
        Restablecer datos ficticios
      </IonButton>
    </AppPage>
  );
}
