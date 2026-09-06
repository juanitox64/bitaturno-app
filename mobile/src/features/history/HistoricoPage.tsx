import { useMemo, useState } from 'react';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonInput,
  IonItem,
  IonLabel,
  IonList,
  IonSelect,
  IonSelectOption,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { useNovedades } from '../../state/useNovedades';
import {
  FILTROS_INICIALES,
  filtrarYOrdenarNovedades,
  obtenerDisciplinas,
} from './historyFilters';
import './history.css';

export function HistoricoPage() {
  const { finalizadas } = useNovedades();
  const [filtros, setFiltros] = useState(FILTROS_INICIALES);

  const disciplinas = useMemo(
    () => obtenerDisciplinas(finalizadas),
    [finalizadas],
  );

  const resultados = useMemo(
    () => filtrarYOrdenarNovedades(finalizadas, filtros),
    [finalizadas, filtros],
  );

  const actualizarFiltro = <K extends keyof typeof FILTROS_INICIALES>(
    clave: K,
    valor: (typeof FILTROS_INICIALES)[K],
  ) => {
    setFiltros((prev) => ({ ...prev, [clave]: valor }));
  };

  return (
    <AppPage titulo="Histórico" subtitulo="Novedades finalizadas" volverA="/inicio">
      <div className="history-toolbar">
        <IonItem>
          <IonLabel position="floating">Buscar</IonLabel>
          <IonInput
            value={filtros.texto}
            onIonInput={(event) => actualizarFiltro('texto', event.detail.value ?? '')}
          />
        </IonItem>

        <IonItem>
          <IonLabel>Disciplina</IonLabel>
          <IonSelect
            value={filtros.disciplina}
            onIonChange={(event) => actualizarFiltro('disciplina', event.detail.value ?? 'todas')}
          >
            <IonSelectOption value="todas">Todas</IonSelectOption>
            {disciplinas.map((disciplina) => (
              <IonSelectOption key={disciplina} value={disciplina}>
                {disciplina}
              </IonSelectOption>
            ))}
          </IonSelect>
        </IonItem>

        <IonItem>
          <IonLabel>Prioridad</IonLabel>
          <IonSelect
            value={filtros.prioridad}
            onIonChange={(event) => actualizarFiltro('prioridad', event.detail.value ?? 'todas')}
          >
            <IonSelectOption value="todas">Todas</IonSelectOption>
            <IonSelectOption value="alta">Alta</IonSelectOption>
            <IonSelectOption value="media">Media</IonSelectOption>
            <IonSelectOption value="baja">Baja</IonSelectOption>
          </IonSelect>
        </IonItem>

        <IonItem>
          <IonLabel>Estado</IonLabel>
          <IonSelect
            value={filtros.estado}
            onIonChange={(event) => actualizarFiltro('estado', event.detail.value ?? 'todos')}
          >
            <IonSelectOption value="todos">Todos</IonSelectOption>
            <IonSelectOption value="pendiente">Pendiente</IonSelectOption>
            <IonSelectOption value="en_revision">En revisión</IonSelectOption>
            <IonSelectOption value="cerrada">Cerrada</IonSelectOption>
          </IonSelect>
        </IonItem>
      </div>

      <IonButton expand="block" fill="clear" onClick={() => setFiltros(FILTROS_INICIALES)}>
        Limpiar filtros
      </IonButton>

      {resultados.length === 0 ? (
        <div className="empty-state">No hay novedades con los filtros actuales.</div>
      ) : (
        <IonList inset className="history-list">
          {resultados.map((novedad) => (
            <IonCard key={novedad.id} className="history-card">
              <IonCardHeader>
                <div className="history-card-heading">
                  <IonCardTitle>{novedad.titulo}</IonCardTitle>
                  <span className={`priority-chip priority-${novedad.prioridad}`}>
                    {novedad.prioridad}
                  </span>
                </div>
              </IonCardHeader>
              <IonCardContent>
                <p>{novedad.descripcion}</p>
                <div className="history-meta">
                  <span><strong>Disciplina:</strong> {novedad.disciplina || 'Sin clasificar'}</span>
                  <span><strong>Turno:</strong> {novedad.turno}</span>
                  <span><strong>Estado:</strong> {novedad.estado}</span>
                  <span><strong>Fecha:</strong> {new Date(novedad.fechaFinalizacion ?? novedad.fechaActualizacion).toLocaleDateString('es-CL')}</span>
                </div>
                <IonButton size="small" fill="outline" routerLink={`/historico/${novedad.id}`}>
                  Ver detalle
                </IonButton>
              </IonCardContent>
            </IonCard>
          ))}
        </IonList>
      )}
    </AppPage>
  );
}

export default HistoricoPage;