import {
  createContext,
  useCallback,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';
import type { NovedadRepository } from '../domain/NovedadRepository';
import type { DatosNovedad, Novedad } from '../domain/novedad';
import { LocalStorageNovedadRepository } from '../infrastructure/LocalStorageNovedadRepository';

export interface NovedadesContextValue {
  novedades: Novedad[];
  borradores: Novedad[];
  finalizadas: Novedad[];
  obtenerPorId(id: string): Novedad | undefined;
  guardarBorrador(datos: DatosNovedad): Novedad;
  actualizarBorrador(id: string, datos: DatosNovedad): Novedad;
  finalizar(id: string, datos: DatosNovedad): Novedad;
  eliminarBorrador(id: string): void;
  reiniciarDemostracion(): void;
}

export const NovedadesContext = createContext<NovedadesContextValue | null>(null);

interface NovedadesProviderProps extends PropsWithChildren {
  repository?: NovedadRepository;
}

export function NovedadesProvider({ children, repository }: NovedadesProviderProps) {
  const [repositoryInstance] = useState<NovedadRepository>(
    () => repository ?? new LocalStorageNovedadRepository(),
  );
  const [novedades, setNovedades] = useState<Novedad[]>(
    () => repositoryInstance.listar(),
  );

  const refrescar = useCallback(() => {
    setNovedades(repositoryInstance.listar());
  }, [repositoryInstance]);

  const obtenerPorId = useCallback(
    (id: string) => repositoryInstance.obtenerPorId(id),
    [repositoryInstance],
  );

  const guardarBorrador = useCallback((datos: DatosNovedad) => {
    const novedad = repositoryInstance.guardarBorrador(datos);
    refrescar();
    return novedad;
  }, [refrescar, repositoryInstance]);

  const actualizarBorrador = useCallback((id: string, datos: DatosNovedad) => {
    const novedad = repositoryInstance.actualizarBorrador(id, datos);
    refrescar();
    return novedad;
  }, [refrescar, repositoryInstance]);

  const finalizar = useCallback((id: string, datos: DatosNovedad) => {
    const novedad = repositoryInstance.finalizar(id, datos);
    refrescar();
    return novedad;
  }, [refrescar, repositoryInstance]);

  const eliminarBorrador = useCallback((id: string) => {
    repositoryInstance.eliminarBorrador(id);
    refrescar();
  }, [refrescar, repositoryInstance]);

  const reiniciarDemostracion = useCallback(() => {
    repositoryInstance.limpiarDatosDeDemostracion();
    refrescar();
  }, [refrescar, repositoryInstance]);

  const value = useMemo<NovedadesContextValue>(() => ({
    novedades,
    borradores: novedades.filter((novedad) => novedad.estado === 'borrador'),
    finalizadas: novedades.filter((novedad) => novedad.estado !== 'borrador'),
    obtenerPorId,
    guardarBorrador,
    actualizarBorrador,
    finalizar,
    eliminarBorrador,
    reiniciarDemostracion,
  }), [
    actualizarBorrador,
    eliminarBorrador,
    finalizar,
    guardarBorrador,
    novedades,
    obtenerPorId,
    reiniciarDemostracion,
  ]);

  return (
    <NovedadesContext.Provider value={value}>
      {children}
    </NovedadesContext.Provider>
  );
}
