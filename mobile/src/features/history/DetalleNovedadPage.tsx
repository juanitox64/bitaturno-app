import {
  IonBadge,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonItem,
  IonLabel,
  IonList,
} from '@ionic/react';
import { useParams } from 'react-router-dom';
import type { EstadoNovedad } from '../../domain/novedad';
import { AppPage } from '../../shared/components/AppPage';
import { useNovedades } from '../../state/useNovedades';
import './history.css';

function colorEstado(estado: EstadoNovedad): string {
  if (estado === 'cerrada') return 'success';
  if (estado === 'en_revision') return 'tertiary';
  return 'warning';
}

function formatearFecha(valor?: string): string {
  if (!valor) return 'Sin fecha';
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no válida';
  return fecha.toLocaleString('es-CL');
}

export function DetalleNovedadPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { obtenerPorId } = useNovedades();
  const encontrada = obtenerPorId(id);
  const novedad = encontrada?.estado === 'borrador' ? undefined : encontrada;

  return (
    <AppPage titulo="Detalle de novedad" subtitulo="Bitácora local" volverA="/historico">
      {!novedad ? (
        <>
          <div className="empty-state">
            No se encontró una novedad finalizada para el identificador solicitado.
          </div>
          <IonButton expand="block" routerLink="/historico">
            Volver al histórico
          </IonButton>
        </>
      ) : (
        <IonCard className="detail-card">
          <IonCardHeader>
            <div className="history-card-heading">
              <IonBadge color={colorEstado(novedad.estado)}>
                {novedad.estado.replace('_', ' ')}
              </IonBadge>
              <span className={`priority-chip priority-${novedad.prioridad}`}>
                {novedad.prioridad}
              </span>
            </div>
            <IonCardTitle>{novedad.titulo}</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <p className="detail-description">{novedad.descripcion}</p>
            <IonList className="detail-list">
              <IonItem>
                <IonLabel><strong>Disciplina</strong><p>{novedad.disciplina || 'Sin clasificar'}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Tipo</strong><p>{novedad.tipo || 'Sin clasificar'}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Turno</strong><p>{novedad.turno || 'Sin informar'}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Prioridad</strong><p>{novedad.prioridad}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Estado</strong><p>{novedad.estado.replace('_', ' ')}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Fecha de ocurrencia</strong><p>{formatearFecha(novedad.fechaOcurrencia)}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Fecha de creación</strong><p>{formatearFecha(novedad.fechaCreacion)}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Última actualización</strong><p>{formatearFecha(novedad.fechaActualizacion)}</p></IonLabel>
              </IonItem>
              <IonItem>
                <IonLabel><strong>Fecha de finalización</strong><p>{formatearFecha(novedad.fechaFinalizacion)}</p></IonLabel>
              </IonItem>
            </IonList>
          </IonCardContent>
        </IonCard>
      )}
    </AppPage>
  );
}
