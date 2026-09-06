import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { NovedadesProvider } from '../../state/NovedadesProvider';
import { DetalleNovedadPage } from './DetalleNovedadPage';
import { HistoricoPage } from './HistoricoPage';

function conDatos(elemento: React.ReactElement, ruta = '/') {
  return render(
    <MemoryRouter initialEntries={[ruta]}>
      <NovedadesProvider>{elemento}</NovedadesProvider>
    </MemoryRouter>,
  );
}

describe('histórico y detalle', () => {
  beforeEach(() => window.localStorage.clear());

  it('muestra registros finalizados y excluye el borrador de demostración', () => {
    conDatos(<HistoricoPage />);
    expect(screen.getByText('Revisión de condición en EQ-001')).toBeInTheDocument();
    expect(screen.queryByText('Inspección visual en Zona 1')).not.toBeInTheDocument();
  });

  it('muestra la información completa de una novedad finalizada', () => {
    conDatos(
      <Routes>
        <Route path="/historico/:id" element={<DetalleNovedadPage />} />
      </Routes>,
      '/historico/demo-registrada-001',
    );
    expect(screen.getByText('Revisión de condición en EQ-001')).toBeInTheDocument();
    expect(screen.getByText('Disciplina Alfa')).toBeInTheDocument();
    expect(screen.getByText('Turno A')).toBeInTheDocument();
  });

  it('informa un identificador inexistente sin romper la vista', () => {
    conDatos(
      <Routes>
        <Route path="/historico/:id" element={<DetalleNovedadPage />} />
      </Routes>,
      '/historico/no-existe',
    );
    expect(screen.getByText(/no se encontró una novedad finalizada/i)).toBeInTheDocument();
  });
});
