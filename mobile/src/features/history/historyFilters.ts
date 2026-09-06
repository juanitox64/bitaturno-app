import type {
  EstadoNovedad,
  Novedad,
  PrioridadNovedad,
} from '../../domain/novedad';

export interface FiltrosHistorico {
  texto: string;
  disciplina: string;
  prioridad: PrioridadNovedad | 'todas';
  estado: EstadoNovedad | 'todos';
}

export const FILTROS_INICIALES: FiltrosHistorico = {
  texto: '',
  disciplina: 'todas',
  prioridad: 'todas',
  estado: 'todos',
};

function normalizar(texto: string): string {
  return texto
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLocaleLowerCase('es');
}

function fechaComparable(novedad: Novedad): number {
  const fecha = novedad.fechaFinalizacion
    || novedad.fechaActualizacion
    || novedad.fechaCreacion;
  const valor = Date.parse(fecha);
  return Number.isNaN(valor) ? 0 : valor;
}

export function filtrarYOrdenarNovedades(
  novedades: ReadonlyArray<Novedad>,
  filtros: FiltrosHistorico,
): Novedad[] {
  const texto = normalizar(filtros.texto);

  return novedades
    .filter((novedad) => novedad.estado !== 'borrador')
    .filter((novedad) => {
      if (!texto) return true;
      return normalizar(`${novedad.titulo} ${novedad.descripcion}`).includes(texto);
    })
    .filter((novedad) => (
      filtros.disciplina === 'todas'
      || novedad.disciplina === filtros.disciplina
    ))
    .filter((novedad) => (
      filtros.prioridad === 'todas'
      || novedad.prioridad === filtros.prioridad
    ))
    .filter((novedad) => (
      filtros.estado === 'todos'
      || novedad.estado === filtros.estado
    ))
    .sort((a, b) => fechaComparable(b) - fechaComparable(a));
}

export function obtenerDisciplinas(novedades: ReadonlyArray<Novedad>): string[] {
  return Array.from(new Set(
    novedades
      .filter((novedad) => novedad.estado !== 'borrador')
      .map((novedad) => novedad.disciplina.trim())
      .filter(Boolean),
  )).sort((a, b) => a.localeCompare(b, 'es'));
}
