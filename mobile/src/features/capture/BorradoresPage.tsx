import { useMemo, useState } from 'react';
import {
  IonBadge,
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonNote,
  IonSearchbar,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { rutaBorrador } from '../../shared/constants/routes';
import { useNovedades } from '../../state/useNovedades';

export function BorradoresPage() {
  const { borradores } = useNovedades();
  const [busqueda, setBusqueda] = useState('');

  const visibles = useMemo(() => {
    const termino = busqueda.trim().toLocaleLowerCase('es');
    if (!termino) return borradores;
    return borradores.filter((borrador) => (
      `${borrador.titulo} ${borrador.descripcion}`
        .toLocaleLowerCase('es')
        .includes(termino)
    ));
  }, [borradores, busqueda]);

  return (
    <AppPage titulo="Mis borradores" subtitulo="Trabajo pendiente" volverA="/inicio">
      <IonSearchbar
        aria-label="Buscar borradores"
        placeholder="Buscar por título o descripción"
        value={busqueda}
        debounce={150}
        onIonInput={(event) => setBusqueda(event.detail.value ?? '')}
      />

      <IonNote className="module-meta">
        {visibles.length} de {borradores.length} borradores visibles
      </IonNote>

      {borradores.length === 0 && (
        <div className="empty-state">
          No existen borradores. Cree una nueva novedad para comenzar.
        </div>
      )}

      {borradores.length > 0 && visibles.length === 0 && (
        <div className="empty-state">
          No hay borradores que coincidan con la búsqueda.
        </div>
      )}

      {visibles.map((borrador) => (
        <IonCard key={borrador.id}>
          <IonCardHeader>
            <IonBadge color="warning">Borrador</IonBadge>
            <IonCardTitle>{borrador.titulo || 'Sin título'}</IonCardTitle>
          </IonCardHeader>
          <IonCardContent>
            <p>{borrador.descripcion}</p>
            <small>Actualizado: {new Date(borrador.fechaActualizacion).toLocaleString('es-CL')}</small>
            <IonButton
              expand="block"
              fill="outline"
              className="ion-margin-top"
              routerLink={rutaBorrador(borrador.id)}
            >
              Continuar registro
            </IonButton>
          </IonCardContent>
        </IonCard>
      ))}

      <IonButton expand="block" routerLink="/nueva">
        Crear otro borrador
      </IonButton>
    </AppPage>
  );
}
