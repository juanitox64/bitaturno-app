import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { DemoSessionProvider } from './demoSession';
import { LoginPage } from './LoginPage';

describe('LoginPage', () => {
  beforeEach(() => window.sessionStorage.clear());

  it('renderiza el acceso demostrativo y su aviso de privacidad', () => {
    render(
      <MemoryRouter>
        <DemoSessionProvider>
          <LoginPage />
        </DemoSessionProvider>
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: 'BitaTurno' })).toBeInTheDocument();
    expect(screen.getByText(/demostración académica/i)).toBeInTheDocument();
    expect(screen.getByText(/la contraseña no se almacena/i)).toBeInTheDocument();
  });
});
