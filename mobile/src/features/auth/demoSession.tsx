import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';

const SESSION_KEY = 'bitaturno:demo-session:v1';

interface DemoSession {
  usuario: string | null;
  iniciar(usuario: string): void;
  cerrar(): void;
}

const DemoSessionContext = createContext<DemoSession | null>(null);

function leerUsuario(): string | null {
  if (typeof sessionStorage === 'undefined') return null;
  return sessionStorage.getItem(SESSION_KEY);
}

export function DemoSessionProvider({ children }: PropsWithChildren) {
  const [usuario, setUsuario] = useState<string | null>(leerUsuario);

  const iniciar = useCallback((nombre: string) => {
    const normalizado = nombre.trim();
    sessionStorage.setItem(SESSION_KEY, normalizado);
    setUsuario(normalizado);
  }, []);

  const cerrar = useCallback(() => {
    sessionStorage.removeItem(SESSION_KEY);
    setUsuario(null);
  }, []);

  const value = useMemo(() => ({ usuario, iniciar, cerrar }), [cerrar, iniciar, usuario]);
  return (
    <DemoSessionContext.Provider value={value}>
      {children}
    </DemoSessionContext.Provider>
  );
}

export function useDemoSession(): DemoSession {
  const context = useContext(DemoSessionContext);
  if (!context) {
    throw new Error('useDemoSession debe utilizarse dentro de DemoSessionProvider.');
  }
  return context;
}
