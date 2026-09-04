import { beforeEach, describe, expect, it } from 'vitest';
import {
  LocalStorageNovedadRepository,
  NOVEDADES_STORAGE_KEY,
} from './LocalStorageNovedadRepository';

const datosFinales = {
  titulo: 'Condición genérica',
  descripcion: 'Descripción ficticia completa.',
  disciplina: 'Disciplina Alfa',
  tipo: 'Observación',
  turno: 'Turno A',
  prioridad: 'alta' as const,
  fechaOcurrencia: '2026-09-03T12:00:00.000Z',
};

function crearRepositorio() {
  return new LocalStorageNovedadRepository(
    window.localStorage,
    () => new Date('2026-09-03T14:00:00.000Z'),
    () => 'id-prueba-001',
  );
}

describe('LocalStorageNovedadRepository', () => {
  beforeEach(() => window.localStorage.clear());

  it('crea el almacenamiento versionado al iniciar', () => {
    crearRepositorio();
    expect(window.localStorage.getItem(NOVEDADES_STORAGE_KEY)).not.toBeNull();
  });

  it('carga datos semilla solo cuando no existe almacenamiento previo', () => {
    const repositorio = crearRepositorio();
    expect(repositorio.listar()).toHaveLength(2);
    expect(repositorio.listarBorradores()).toHaveLength(1);
    expect(repositorio.listarFinalizadas()).toHaveLength(1);
  });

  it('guarda un borrador validado', () => {
    const repositorio = crearRepositorio();
    const guardado = repositorio.guardarBorrador({ descripcion: '  Registro de prueba  ' });
    expect(guardado.id).toBe('id-prueba-001');
    expect(guardado.descripcion).toBe('Registro de prueba');
    expect(guardado.estado).toBe('borrador');
    expect(repositorio.listar()).toHaveLength(3);
  });

  it('actualiza un borrador sin duplicarlo', () => {
    const repositorio = crearRepositorio();
    const cantidadInicial = repositorio.listar().length;
    repositorio.actualizarBorrador('demo-borrador-001', {
      descripcion: 'Descripción actualizada',
      titulo: 'Título actualizado',
    });
    expect(repositorio.listar()).toHaveLength(cantidadInicial);
    expect(repositorio.obtenerPorId('demo-borrador-001')?.titulo).toBe('Título actualizado');
  });

  it('finaliza un borrador y lo cambia a pendiente', () => {
    const repositorio = crearRepositorio();
    const finalizada = repositorio.finalizar('demo-borrador-001', datosFinales);
    expect(finalizada.estado).toBe('pendiente');
    expect(finalizada.fechaFinalizacion).toBe('2026-09-03T14:00:00.000Z');
    expect(repositorio.listarBorradores()).toHaveLength(0);
    expect(repositorio.listarFinalizadas()).toHaveLength(2);
  });

  it('conserva los datos al crear otra instancia', () => {
    const primero = crearRepositorio();
    primero.guardarBorrador({ descripcion: 'Persistencia local ficticia' });
    const segundo = crearRepositorio();
    expect(segundo.obtenerPorId('id-prueba-001')?.descripcion).toBe(
      'Persistencia local ficticia',
    );
  });

  it('elimina borradores y rechaza eliminar una novedad finalizada', () => {
    const repositorio = crearRepositorio();
    repositorio.eliminarBorrador('demo-borrador-001');
    expect(repositorio.obtenerPorId('demo-borrador-001')).toBeUndefined();
    expect(() => repositorio.eliminarBorrador('demo-registrada-001')).toThrow(
      'No se puede eliminar una novedad finalizada.',
    );
  });

  it('restablece los datos ficticios conocidos', () => {
    const repositorio = crearRepositorio();
    repositorio.eliminarBorrador('demo-borrador-001');
    repositorio.limpiarDatosDeDemostracion();
    expect(repositorio.listar()).toHaveLength(2);
  });
});
