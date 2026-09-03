export const RUTAS = {
  login: '/login',
  inicio: '/inicio',
  nueva: '/nueva',
  borradores: '/borradores',
  historico: '/historico',
} as const;

export function rutaBorrador(id: string): string {
  return `/borradores/${encodeURIComponent(id)}`;
}

export function rutaHistorico(id: string): string {
  return `/historico/${encodeURIComponent(id)}`;
}
