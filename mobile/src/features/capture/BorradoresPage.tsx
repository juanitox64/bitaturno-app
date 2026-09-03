import {
  IonBadge,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { ModulePendingNotice } from '../../shared/components/ModulePendingNotice';
import { rutaBorrador } from '../../shared/constants/routes';
import { useNovedades } from '../../state/useNovedades';

export function BorradoresPage() {
  const { borradores } = useNovedades();
  // TODO: completar búsqueda, recuperación editable y confirmación de eliminación.

  return (
    <AppPage titulo="Mis borradores" subtitulo="Trabajo pendiente" volverA="/inicio">
      <ModulePendingNotice>
        El listado básico usa datos tipados; faltan edición, eliminación confirmada y estados finales.
      </ModulePendingNotice>

      {borradores.length === 0 && (
        <div className="empty-state">No existen borradores en la demostración.</div>
      )}
      {borradores.map((borrador) => (
        <IonCard key={borrador.id}>
          <IonCardHeader>
            <IonBadge color="warning">Borrador</IonBadge>
            <IonCardTitle>{borrador.titulo || 'Sin título'}</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <p>{borrador.descripcion}</p>
            <IonButton size="small" fill="outline" routerLink={rutaBorrador(borrador.id)}>
              Continuar
            </IonButton>
          </IonCardContent>
        </IonCard>
      ))}
      <IonButton expand="block" routerLink="/nueva">Crear otro borrador</IonButton>
    </AppPage>
  );
}
