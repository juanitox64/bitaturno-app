import { useNavigate, useParams } from 'react-router-dom';
import { AppPage } from '../../shared/components/AppPage';
import { useNovedades } from '../../state/useNovedades';
import './history.css';

function formatearFecha(valor?: string): string {
  if (!valor) return 'Sin fecha';
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return 'Fecha no válida';
  return fecha.toLocaleString('es-CL');
}

export function DetalleNovedadPage() {
  const navigate = useNavigate();
  const { id = '' } = useParams<{ id: string }>();
  const { obtenerPorId } = useNovedades();
  const encontrada = obtenerPorId(id);
  const novedad = encontrada && encontrada.estado !== 'borrador' ? encontrada : undefined;

  return (
    <AppPage titulo="Detalle de novedad" subtitulo="Bitácora local" volverA="/historico">
      {!novedad ? (
        <>
          <div className="empty-state">
            No se encontró una novedad finalizada para el identificador solicitado.
          </div>
          <button type="button" className="secondary-action" onClick={() => navigate('/historico', { replace: true })}>
            Volver al histórico
          </button>
        </>
      ) : (
        <article className="detail-card">
          <header className="history-card-heading">
            <span className={`priority-chip priority-${novedad.prioridad}`}>
              {novedad.prioridad}
            </span>
            <span className="detail-state">{novedad.estado.replace('_', ' ')}</span>
          </header>

          <h2>{novedad.titulo}</h2>
          <p className="detail-description">{novedad.descripcion}</p>

          <ul className="detail-list">
            <li><strong>Disciplina</strong><span>{novedad.disciplina || 'Sin clasificar'}</span></li>
            <li><strong>Tipo</strong><span>{novedad.tipo || 'Sin clasificar'}</span></li>
            <li><strong>Turno</strong><span>{novedad.turno || 'Sin informar'}</span></li>
            <li><strong>Prioridad</strong><span>{novedad.prioridad}</span></li>
            <li><strong>Estado</strong><span>{novedad.estado.replace('_', ' ')}</span></li>
            <li><strong>Fecha de ocurrencia</strong><span>{formatearFecha(novedad.fechaOcurrencia)}</span></li>
            <li><strong>Fecha de creación</strong><span>{formatearFecha(novedad.fechaCreacion)}</span></li>
            <li><strong>Última actualización</strong><span>{formatearFecha(novedad.fechaActualizacion)}</span></li>
            <li><strong>Fecha de finalización</strong><span>{formatearFecha(novedad.fechaFinalizacion)}</span></li>
          </ul>
        </article>
      )}
    </AppPage>
  );
}