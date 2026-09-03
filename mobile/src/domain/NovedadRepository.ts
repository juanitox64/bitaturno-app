import type { DatosNovedad, Novedad } from './novedad';

export interface NovedadRepository {
  listar(): Novedad[];
  obtenerPorId(id: string): Novedad | undefined;
  guardarBorrador(datos: DatosNovedad): Novedad;
  actualizarBorrador(id: string, datos: DatosNovedad): Novedad;
  finalizar(id: string, datos: DatosNovedad): Novedad;
  eliminarBorrador(id: string): void;
  listarBorradores(): Novedad[];
  listarFinalizadas(): Novedad[];
  limpiarDatosDeDemostracion(): void;
}
