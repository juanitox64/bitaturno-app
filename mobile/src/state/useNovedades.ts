import { useContext } from 'react';
import { NovedadesContext } from './NovedadesProvider';

export function useNovedades() {
  const context = useContext(NovedadesContext);
  if (!context) {
    throw new Error('useNovedades debe utilizarse dentro de NovedadesProvider.');
  }
  return context;
}
