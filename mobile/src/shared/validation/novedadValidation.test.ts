import { describe, expect, it } from 'vitest';
import {
  ErrorValidacionNovedad,
  exigirDatosValidos,
  normalizarDatosNovedad,
  validarBorrador,
  validarFinalizacion,
} from './novedadValidation';

describe('validaciones comunes', () => {
  it('rechaza un borrador sin descripción', () => {
    expect(validarBorrador({ descripcion: '   ' })).toEqual({
      descripcion: 'Ingrese una descripción para guardar el borrador.',
    });
    expect(() => exigirDatosValidos({}, 'borrador')).toThrow(ErrorValidacionNovedad);
  });

  it('informa los campos faltantes al finalizar', () => {
    const errores = validarFinalizacion({ descripcion: 'Descripción ficticia' });
    expect(errores).toMatchObject({
      titulo: expect.any(String),
      disciplina: expect.any(String),
      tipo: expect.any(String),
      turno: expect.any(String),
    });
  });

  it('normaliza espacios y acepta datos finales completos', () => {
    const datos = normalizarDatosNovedad({
      titulo: '  Título  ',
      descripcion: '  Descripción  ',
      disciplina: 'Disciplina Alfa',
      tipo: 'Observación',
      turno: 'Turno A',
      prioridad: 'alta',
    });
    expect(datos.titulo).toBe('Título');
    expect(validarFinalizacion(datos)).toEqual({});
  });
});
