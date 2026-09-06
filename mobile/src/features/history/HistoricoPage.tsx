import { useMemo, useState } from 'react';
import {
  IonBadge,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonItem,
  IonList,
  IonNote,
  IonSearchbar,
  IonSelect,
  IonSelectOption,
} from '@ionic/react';
import type { EstadoNovedad, PrioridadNovedad } from '../../domain/novedad';
import { AppPage } from '../../shared/components/AppPage';
import { rutaHistorico } from '../../shared/constants/routes';
import { useNovedades } from '../../state/useNovedades';
import {
  FILTROS_INICIALES,
  filtrarYOrdenarNovedades,
  obtenerDisciplinas,
  type FiltrosHistorico,
} from './historyFilters';
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

export function HistoricoPage() {
  const { novedades } = useNovedades();
  const [filtros, setFiltros] = useState<FiltrosHistorico>(FILTROS_INICIALES);

  const disciplinas = useMemo(() => obtenerDisciplinas(novedades), [novedades]);
  const finalizadas = useMemo(
    () => novedades.filter((novedad) => novedad.estado !== 'borrador'),
    [novedades],
  );
  const visibles = useMemo(
    () => filtrarYOrdenarNovedades(novedades, filtros),
    [filtros, novedades],
  );
  const hayFiltros = JSON.stringify(filtros) !== JSON.stringify(FILTROS_INICIALES);

  const actualizarFiltro = <K extends keyof FiltrosHistorico>(
    campo: K,
    valor: FiltrosHistorico[K],
  ) => setFiltros((actuales) => ({ ...actuales, [campo]: valor }));

  return (
    <AppPage titulo="Histórico" subtitulo="Bitácora local" volverA="/inicio">
      <IonSearchbar
        aria-label="Buscar novedades"
        placeholder="Buscar por título o descripción"
        value={filtros.texto}
        debounce={150}
        onIonInput={(event) => actualizarFiltro('texto', event.detail.value ?? '')}
      />

      <IonList inset className="filter-list history-filters">
        <IonItem>
          <IonSelect
            label="Disciplina"
            labelPlacement="stacked"
            value={filtros.disciplina}
            onIonChange={(event) => actualizarFiltro('disciplina', event.detail.value as string)}
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
          <IonSelect
            label="Prioridad"
            labelPlacement="stacked"
            value={filtros.prioridad}
            onIonChange={(event) => actualizarFiltro(
              'prioridad',
              event.detail.value as PrioridadNovedad | 'todas',
            )}
          >
            <IonSelectOption value="todas">Todas</IonSelectOption>
            <IonSelectOption value="alta">Alta</IonSelectOption>
            <IonSelectOption value="media">Media</IonSelectOption>
            <IonSelectOption value="baja">Baja</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect
            label="Estado"
            labelPlacement="stacked"
            value={filtros.estado}
            onIonChange={(event) => actualizarFiltro(
              'estado',
              event.detail.value as EstadoNovedad | 'todos',
            )}
          >
            <IonSelectOption value="todos">Todos</IonSelectOption>
            <IonSelectOption value="pendiente">Pendiente</IonSelectOption>
            <IonSelectOption value="en_revision">En revisión</IonSelectOption>
            <IonSelectOption value="cerrada">Cerrada</IonSelectOption>
          </IonSelect>
        </IonItem>
      </IonList>

      <div className="history-toolbar">
        <IonNote>
          {visibles.length} de {finalizadas.length} registros visibles
        </IonNote>
        <IonButton
          size="small"
          fill="clear"
          disabled={!hayFiltros}
          onClick={() => setFiltros(FILTROS_INICIALES)}
        >
          Limpiar filtros
        </IonButton>
      </div>

      {finalizadas.length === 0 && (
        <div className="empty-state">No existen novedades finalizadas.</div>
      )}

      {finalizadas.length > 0 && visibles.length === 0 && (
        <div className="empty-state">
          No hay coincidencias con los filtros seleccionados.
        </div>
      )}

      <section className="history-list" aria-label="Listado de novedades">
        {visibles.map((novedad) => (
          <IonCard key={novedad.id} className="history-card">
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
              <p>{novedad.descripcion}</p>
              <div className="history-meta">
                <span><strong>Disciplina:</strong> {novedad.disciplina || 'Sin clasificar'}</span>
                <span><strong>Turno:</strong> {novedad.turno || 'Sin informar'}</span>
                <span><strong>Finalización:</strong> {formatearFecha(novedad.fechaFinalizacion)}</span>
              </div>
              <IonButton
                expand="block"
                fill="outline"
                className="ion-margin-top"
                routerLink={rutaHistorico(novedad.id)}
              >
                Ver detalle
              </IonButton>
            </IonCardContent>
          </IonCard>
        ))}
      </section>
    </AppPage>
  );
}
