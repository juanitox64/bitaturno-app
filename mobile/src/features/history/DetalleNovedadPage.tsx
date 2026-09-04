import { IonBadge, IonCard, IonCardContent, IonCardHeader, IonCardTitle } from '@ionic/react';
import { useParams } from 'react-router-dom';
import { AppPage } from '../../shared/components/AppPage';
import { ModulePendingNotice } from '../../shared/components/ModulePendingNotice';
import { useNovedades } from '../../state/useNovedades';

export function DetalleNovedadPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { obtenerPorId } = useNovedades();
  const novedad = obtenerPorId(id);
  // TODO: completar el renderizado, los estados vacíos y la revisión responsiva.

  return (
    <AppPage titulo="Detalle de novedad" subtitulo="Vista base" volverA="/historico">
      <ModulePendingNotice>
        La ruta y la consulta están conectadas; la ficha completa aún debe implementarse.
      </ModulePendingNotice>
      {!novedad ? (
        <div className="empty-state">No se encontró la novedad solicitada.</div>
      ) : (
        <IonCard>
          <IonCardHeader>
            <IonBadge>{novedad.estado.replace('_', ' ')}</IonBadge>
            <IonCardTitle>{novedad.titulo}</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <p>{novedad.descripcion}</p>
            <p className="module-meta">Identificador: {novedad.id}</p>
          </IonCardContent>
        </IonCard>
      )}
    </AppPage>
  );
}
