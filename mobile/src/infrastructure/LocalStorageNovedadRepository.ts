import type { NovedadRepository } from '../domain/NovedadRepository';
import {
  ESTADOS_NOVEDAD,
  PRIORIDADES_NOVEDAD,
  type DatosNovedad,
  type Novedad,
} from '../domain/novedad';
import {
  exigirDatosValidos,
  normalizarDatosNovedad,
} from '../shared/validation/novedadValidation';

export const NOVEDADES_STORAGE_KEY = 'bitaturno:novedades:v1';

export interface StorageNovedades {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

type Reloj = () => Date;
type GeneradorId = () => string;

const datosSemilla: ReadonlyArray<Novedad> = [
  {
    id: 'demo-borrador-001',
    titulo: 'Inspección visual en Zona 1',
    descripcion: 'Condición ficticia pendiente de clasificación.',
    disciplina: '',
    tipo: '',
    turno: 'Turno A',
    prioridad: 'media',
    estado: 'borrador',
    fechaOcurrencia: '2026-09-03T10:18:00.000Z',
    fechaCreacion: '2026-09-03T10:20:00.000Z',
    fechaActualizacion: '2026-09-03T10:20:00.000Z',
  },
  {
    id: 'demo-registrada-001',
    titulo: 'Revisión de condición en EQ-001',
    descripcion: 'Registro genérico finalizado para la demostración.',
    disciplina: 'Disciplina Alfa',
    tipo: 'Observación',
    turno: 'Turno A',
    prioridad: 'alta',
    estado: 'pendiente',
    fechaOcurrencia: '2026-09-03T11:15:00.000Z',
    fechaCreacion: '2026-09-03T11:16:00.000Z',
    fechaActualizacion: '2026-09-03T11:18:00.000Z',
    fechaFinalizacion: '2026-09-03T11:18:00.000Z',
  },
];

function clonarSemillas(): Novedad[] {
  return datosSemilla.map((novedad) => ({ ...novedad }));
}

function esNovedad(valor: unknown): valor is Novedad {
  if (!valor || typeof valor !== 'object') return false;
  const candidato = valor as Partial<Novedad>;
  return (
    typeof candidato.id === 'string'
    && typeof candidato.titulo === 'string'
    && typeof candidato.descripcion === 'string'
    && typeof candidato.estado === 'string'
    && ESTADOS_NOVEDAD.includes(candidato.estado as Novedad['estado'])
    && typeof candidato.prioridad === 'string'
    && PRIORIDADES_NOVEDAD.includes(candidato.prioridad as Novedad['prioridad'])
  );
}

function idPredeterminado(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `demo-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export class LocalStorageNovedadRepository implements NovedadRepository {
  constructor(
    private readonly storage: StorageNovedades = window.localStorage,
    private readonly reloj: Reloj = () => new Date(),
    private readonly generarId: GeneradorId = idPredeterminado,
  ) {
    if (this.storage.getItem(NOVEDADES_STORAGE_KEY) === null) {
      this.escribir(clonarSemillas());
    }
  }

  listar(): Novedad[] {
    const contenido = this.storage.getItem(NOVEDADES_STORAGE_KEY);
    if (!contenido) return [];
    try {
      const datos: unknown = JSON.parse(contenido);
      return Array.isArray(datos)
        ? datos.filter(esNovedad).map((item) => ({ ...item }))
        : [];
    } catch {
      return [];
    }
  }

  obtenerPorId(id: string): Novedad | undefined {
    const encontrada = this.listar().find((novedad) => novedad.id === id);
    return encontrada ? { ...encontrada } : undefined;
  }

  guardarBorrador(datos: DatosNovedad): Novedad {
    exigirDatosValidos(datos, 'borrador');
    const fecha = this.reloj().toISOString();
    const nueva: Novedad = {
      id: this.generarId(),
      ...normalizarDatosNovedad(datos),
      estado: 'borrador',
      fechaCreacion: fecha,
      fechaActualizacion: fecha,
    };
    const novedades = this.listar();
    novedades.push(nueva);
    this.escribir(novedades);
    return { ...nueva };
  }

  actualizarBorrador(id: string, datos: DatosNovedad): Novedad {
    exigirDatosValidos(datos, 'borrador');
    const novedades = this.listar();
    const indice = novedades.findIndex((novedad) => novedad.id === id);
    if (indice < 0) throw new Error('El borrador solicitado no existe.');
    if (novedades[indice].estado !== 'borrador') {
      throw new Error('Solo se pueden actualizar borradores.');
    }
    const actualizada: Novedad = {
      ...novedades[indice],
      ...normalizarDatosNovedad(datos),
      id,
      estado: 'borrador',
      fechaCreacion: novedades[indice].fechaCreacion,
      fechaActualizacion: this.reloj().toISOString(),
    };
    novedades[indice] = actualizada;
    this.escribir(novedades);
    return { ...actualizada };
  }

  finalizar(id: string, datos: DatosNovedad): Novedad {
    exigirDatosValidos(datos, 'finalizar');
    const novedades = this.listar();
    const indice = novedades.findIndex((novedad) => novedad.id === id);
    if (indice < 0) throw new Error('El borrador solicitado no existe.');
    if (novedades[indice].estado !== 'borrador') {
      throw new Error('Solo se pueden finalizar borradores.');
    }
    const fecha = this.reloj().toISOString();
    const finalizada: Novedad = {
      ...novedades[indice],
      ...normalizarDatosNovedad(datos),
      id,
      estado: 'pendiente',
      fechaCreacion: novedades[indice].fechaCreacion,
      fechaActualizacion: fecha,
      fechaFinalizacion: fecha,
    };
    novedades[indice] = finalizada;
    this.escribir(novedades);
    return { ...finalizada };
  }

  eliminarBorrador(id: string): void {
    const novedades = this.listar();
    const encontrada = novedades.find((novedad) => novedad.id === id);
    if (!encontrada) throw new Error('El borrador solicitado no existe.');
    if (encontrada.estado !== 'borrador') {
      throw new Error('No se puede eliminar una novedad finalizada.');
    }
    this.escribir(novedades.filter((novedad) => novedad.id !== id));
  }

  listarBorradores(): Novedad[] {
    return this.listar().filter((novedad) => novedad.estado === 'borrador');
  }

  listarFinalizadas(): Novedad[] {
    return this.listar().filter((novedad) => novedad.estado !== 'borrador');
  }

  limpiarDatosDeDemostracion(): void {
    this.escribir(clonarSemillas());
  }

  private escribir(novedades: Novedad[]): void {
    this.storage.setItem(NOVEDADES_STORAGE_KEY, JSON.stringify(novedades));
  }
}
