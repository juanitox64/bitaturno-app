import {
  IonBadge,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonItem,
  IonList,
  IonSearchbar,
  IonSelect,
  IonSelectOption,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { ModulePendingNotice } from '../../shared/components/ModulePendingNotice';
import { useNovedades } from '../../state/useNovedades';

export function HistoricoPage() {
  const { finalizadas } = useNovedades();
  // TODO: implementar filtros, orden y navegación al detalle.

  return (
    <AppPage titulo="Histórico" subtitulo="Bitácora local" volverA="/inicio">
      <ModulePendingNotice>
        Los controles y datos tipados están disponibles; falta implementar filtrado y navegación final.
      </ModulePendingNotice>

      <IonSearchbar aria-label="Buscar novedades" placeholder="Buscar por título" />
      <IonList inset className="filter-list">
        <IonItem>
          <IonSelect label="Disciplina" labelPlacement="stacked" value="todas">
            <IonSelectOption value="todas">Todas</IonSelectOption>
            <IonSelectOption value="alfa">Disciplina Alfa</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect label="Prioridad" labelPlacement="stacked" value="todas">
            <IonSelectOption value="todas">Todas</IonSelectOption>
            <IonSelectOption value="alta">Alta</IonSelectOption>
            <IonSelectOption value="media">Media</IonSelectOption>
            <IonSelectOption value="baja">Baja</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect label="Estado" labelPlacement="stacked" value="todos">
            <IonSelectOption value="todos">Todos</IonSelectOption>
            <IonSelectOption value="pendiente">Pendiente</IonSelectOption>
            <IonSelectOption value="en_revision">En revisión</IonSelectOption>
            <IonSelectOption value="cerrada">Cerrada</IonSelectOption>
          </IonSelect>
        </IonItem>
      </IonList>

      <section aria-label="Listado de novedades">
        {finalizadas.length === 0 && (
          <div className="empty-state">No existen novedades finalizadas.</div>
        )}
        {finalizadas.map((novedad) => (
          <IonCard key={novedad.id}>
            <IonCardHeader>
              <IonBadge>{novedad.estado.replace('_', ' ')}</IonBadge>
              <IonCardTitle>{novedad.titulo}</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <p>{novedad.descripcion}</p>
              <small>Detalle navegable pendiente de conexión.</small>
            </IonCardContent>
          </IonCard>
        ))}
      </section>
    </AppPage>
  );
}
