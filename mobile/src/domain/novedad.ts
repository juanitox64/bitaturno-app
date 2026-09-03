export type EstadoNovedad =
  | 'borrador'
  | 'pendiente'
  | 'en_revision'
  | 'cerrada';

export type PrioridadNovedad = 'baja' | 'media' | 'alta';

export interface Novedad {
  id: string;
  titulo: string;
  descripcion: string;
  disciplina: string;
  tipo: string;
  turno: string;
  prioridad: PrioridadNovedad;
  estado: EstadoNovedad;
  fechaOcurrencia: string;
  fechaCreacion: string;
  fechaActualizacion: string;
  fechaFinalizacion?: string;
}

export interface DatosNovedad {
  titulo?: string;
  descripcion?: string;
  disciplina?: string;
  tipo?: string;
  turno?: string;
  prioridad?: PrioridadNovedad;
  fechaOcurrencia?: string;
}

export const ESTADOS_NOVEDAD: ReadonlyArray<EstadoNovedad> = [
  'borrador',
  'pendiente',
  'en_revision',
  'cerrada',
];

export const PRIORIDADES_NOVEDAD: ReadonlyArray<PrioridadNovedad> = [
  'baja',
  'media',
  'alta',
];
