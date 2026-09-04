import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { DemoSessionProvider } from '../auth/demoSession';
import { LocalStorageNovedadRepository } from '../../infrastructure/LocalStorageNovedadRepository';
import { NovedadesProvider } from '../../state/NovedadesProvider';
import { InicioPage } from './InicioPage';

describe('InicioPage', () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.sessionStorage.clear();
    window.sessionStorage.setItem('bitaturno:demo-session:v1', 'usuario.demo');
  });

  it('renderiza los contadores y accesos principales', () => {
    const repository = new LocalStorageNovedadRepository(window.localStorage);
    render(
      <MemoryRouter>
        <DemoSessionProvider>
          <NovedadesProvider repository={repository}>
            <InicioPage />
          </NovedadesProvider>
        </DemoSessionProvider>
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: /hola, usuario.demo/i })).toBeInTheDocument();
    expect(screen.getByText('Borradores')).toBeInTheDocument();
    expect(screen.getByText('Finalizadas')).toBeInTheDocument();
    expect(screen.getByText('Nueva novedad')).toBeInTheDocument();
  });
});
