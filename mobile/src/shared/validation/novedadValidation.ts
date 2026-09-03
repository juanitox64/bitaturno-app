import type { DatosNovedad, PrioridadNovedad } from '../../domain/novedad';

export class ErrorValidacionNovedad extends Error {
  constructor(public readonly campos: Record<string, string>) {
    super(Object.values(campos).join(' '));
    this.name = 'ErrorValidacionNovedad';
  }
}

export function normalizarDatosNovedad(datos: DatosNovedad): Required<DatosNovedad> {
  return {
    titulo: datos.titulo?.trim() ?? '',
    descripcion: datos.descripcion?.trim() ?? '',
    disciplina: datos.disciplina?.trim() ?? '',
    tipo: datos.tipo?.trim() ?? '',
    turno: datos.turno?.trim() ?? '',
    prioridad: (datos.prioridad ?? 'media') as PrioridadNovedad,
    fechaOcurrencia: datos.fechaOcurrencia?.trim() ?? '',
  };
}

export function validarBorrador(datos: DatosNovedad): Record<string, string> {
  const normalizados = normalizarDatosNovedad(datos);
  if (!normalizados.descripcion) {
    return { descripcion: 'Ingrese una descripción para guardar el borrador.' };
  }
  return {};
}

export function validarFinalizacion(datos: DatosNovedad): Record<string, string> {
  const normalizados = normalizarDatosNovedad(datos);
  const errores: Record<string, string> = {};
  const requeridos: Array<[keyof Required<DatosNovedad>, string]> = [
    ['titulo', 'El título es obligatorio.'],
    ['descripcion', 'La descripción es obligatoria.'],
    ['disciplina', 'La disciplina es obligatoria.'],
    ['tipo', 'El tipo es obligatorio.'],
    ['turno', 'El turno es obligatorio.'],
    ['prioridad', 'La prioridad es obligatoria.'],
  ];

  for (const [campo, mensaje] of requeridos) {
    if (!normalizados[campo]) errores[campo] = mensaje;
  }
  return errores;
}

export function exigirDatosValidos(
  datos: DatosNovedad,
  modo: 'borrador' | 'finalizar',
): void {
  const errores = modo === 'borrador'
    ? validarBorrador(datos)
    : validarFinalizacion(datos);
  if (Object.keys(errores).length > 0) {
    throw new ErrorValidacionNovedad(errores);
  }
}
