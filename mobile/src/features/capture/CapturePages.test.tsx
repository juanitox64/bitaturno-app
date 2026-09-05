import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { NovedadesProvider } from '../../state/NovedadesProvider';
import { BorradoresPage } from './BorradoresPage';
import { CompletarNovedadPage } from './CompletarNovedadPage';
import { NuevaNovedadPage } from './NuevaNovedadPage';

function conDatos(elemento: React.ReactElement, ruta = '/') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <NovedadesProvider>{elemento}</NovedadesProvider>
    </MemoryRouter>,
  );
}

describe('módulo de captura y borradores', () => {
  beforeEach(() => window.localStorage.clear());

  it('presenta el formulario de creación y la acción de guardado', () => {
    conDatos(<NuevaNovedadPage />);
    expect(screen.getByText('Nueva novedad')).toBeInTheDocument();
    expect(screen.getByText('Guardar borrador')).toBeInTheDocument();
    expect(screen.getByText(/Registre una descripción inicial/i)).toBeInTheDocument();
  });

  it('lista el borrador ficticio de la base local', () => {
    conDatos(<BorradoresPage />);
    expect(screen.getByText('Inspección visual en Zona 1')).toBeInTheDocument();
    expect(screen.getByText('Continuar registro')).toBeInTheDocument();
  });

  it('carga el borrador solicitado en la pantalla de edición', () => {
    conDatos(
      <Routes>
        <Route path="/borradores/:id" element={<CompletarNovedadPage />} />
      </Routes>,
      '/borradores/demo-borrador-001',
    );
    expect(screen.getByText('Completar novedad')).toBeInTheDocument();
    expect(screen.getByText('Guardar cambios')).toBeInTheDocument();
    expect(screen.getByText('Finalizar registro')).toBeInTheDocument();
  });

  it('informa cuando el identificador no existe', () => {
    conDatos(
      <Routes>
        <Route path="/borradores/:id" element={<CompletarNovedadPage />} />
      </Routes>,
      '/borradores/no-existe',
    );
    expect(screen.getByText(/no se encontró el borrador solicitado/i)).toBeInTheDocument();
  });
});
