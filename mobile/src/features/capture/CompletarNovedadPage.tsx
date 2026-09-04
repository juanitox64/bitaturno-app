import { useParams } from 'react-router-dom';
import {
  IonButton,
  IonInput,
  IonItem,
  IonList,
  IonSelect,
  IonSelectOption,
  IonTextarea,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { ModulePendingNotice } from '../../shared/components/ModulePendingNotice';
import { useNovedades } from '../../state/useNovedades';

export function CompletarNovedadPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { obtenerPorId } = useNovedades();
  const borrador = obtenerPorId(id);
  // TODO: conectar actualización, finalización y eliminación con validación y confirmación.

  return (
    <AppPage titulo="Completar novedad" subtitulo="Paso 2 de 2" volverA="/borradores">
      <ModulePendingNotice>
        La ruta identifica el borrador, pero las acciones de actualización y finalización siguen pendientes.
      </ModulePendingNotice>

      {!borrador ? (
        <div className="empty-state">No se encontró el borrador solicitado.</div>
      ) : (
        <IonList inset className="form-list">
          <IonItem>
            <IonInput label="Título *" labelPlacement="stacked" value={borrador.titulo} />
          </IonItem>
          <IonItem>
            <IonTextarea label="Descripción *" labelPlacement="stacked" value={borrador.descripcion} autoGrow />
          </IonItem>
          <IonItem>
            <IonInput label="Disciplina *" labelPlacement="stacked" value={borrador.disciplina} />
          </IonItem>
          <IonItem>
            <IonInput label="Tipo *" labelPlacement="stacked" value={borrador.tipo} />
          </IonItem>
          <IonItem>
            <IonInput label="Turno *" labelPlacement="stacked" value={borrador.turno} />
          </IonItem>
          <IonItem>
            <IonSelect label="Prioridad *" labelPlacement="stacked" value={borrador.prioridad}>
              <IonSelectOption value="baja">Baja</IonSelectOption>
              <IonSelectOption value="media">Media</IonSelectOption>
              <IonSelectOption value="alta">Alta</IonSelectOption>
            </IonSelect>
          </IonItem>
        </IonList>
      )}
      <IonButton expand="block" disabled>Finalizar registro</IonButton>
      <IonButton expand="block" fill="outline" disabled>Guardar cambios</IonButton>
    </AppPage>
  );
}
