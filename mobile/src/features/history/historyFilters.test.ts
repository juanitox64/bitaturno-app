import { describe, expect, it } from 'vitest';

import type { Novedad } from '../../domain/novedad';

import {
  FILTROS_INICIALES,
  filtrarYOrdenarNovedades,
  obtenerDisciplinas,
} from './historyFilters';

const novedades: Novedad[] = [
  {
    id: 'borrador-1',
    titulo: 'Borrador oculto',
    descripcion: 'No debe aparecer',
    disciplina: 'Disciplina Alfa',
    tipo: 'Observación',
    turno: 'Turno A',
    prioridad: 'alta',
    estado: 'borrador',
    fechaOcurrencia: '2026-09-03T08:00:00.000Z',
    fechaCreacion: '2026-09-03T08:00:00.000Z',
    fechaActualizacion: '2026-09-03T08:00:00.000Z',
  },
  {
    id: 'pendiente-1',
    titulo: 'Revisión de equipo',
    descripcion: 'Registro de prioridad alta',
    disciplina: 'Disciplina Alfa',
    tipo: 'Observación',
    turno: 'Turno A',
    prioridad: 'alta',
    estado: 'pendiente',
    fechaOcurrencia: '2026-09-03T09:00:00.000Z',
    fechaCreacion: '2026-09-03T09:00:00.000Z',
    fechaActualizacion: '2026-09-03T10:00:00.000Z',
    fechaFinalizacion: '2026-09-03T10:00:00.000Z',
  },
  {
    id: 'cerrada-1',
    titulo: 'Inspección final',
    descripcion: 'Registro de prioridad baja',
    disciplina: 'Disciplina Beta',
    tipo: 'Incidencia',
    turno: 'Turno B',
    prioridad: 'baja',
    estado: 'cerrada',
    fechaOcurrencia: '2026-09-04T09:00:00.000Z',
    fechaCreacion: '2026-09-04T09:00:00.000Z',
    fechaActualizacion: '2026-09-04T11:00:00.000Z',
    fechaFinalizacion: '2026-09-04T11:00:00.000Z',
  },
];

describe('filtros del histórico', () => {
  it('excluye borradores y ordena desde el registro más reciente', () => {
    const resultado = filtrarYOrdenarNovedades(novedades, FILTROS_INICIALES);

    expect(resultado.map((item) => item.id)).toEqual([
      'cerrada-1',
      'pendiente-1',
    ]);
  });

  it('busca sin distinguir mayúsculas ni tildes', () => {
    const resultado = filtrarYOrdenarNovedades(novedades, {
      ...FILTROS_INICIALES,
      texto: 'inspeccion',
    });

    expect(resultado.map((item) => item.id)).toEqual(['cerrada-1']);
  });

  it('combina disciplina, prioridad y estado', () => {
    const resultado = filtrarYOrdenarNovedades(novedades, {
      ...FILTROS_INICIALES,
      disciplina: 'Disciplina Alfa',
      prioridad: 'alta',
      estado: 'pendiente',
    });

    expect(resultado.map((item) => item.id)).toEqual(['pendiente-1']);
  });

  it('obtiene disciplinas únicas solo desde registros finalizados', () => {
    expect(obtenerDisciplinas(novedades)).toEqual([
      'Disciplina Alfa',
      'Disciplina Beta',
    ]);
  });
});