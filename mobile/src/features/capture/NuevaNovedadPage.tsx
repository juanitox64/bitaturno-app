import { useState, type FormEvent } from 'react';
import {
  IonButton,
  IonInput,
  IonItem,
  IonList,
  IonNote,
  IonSelect,
  IonSelectOption,
  IonTextarea,
} from '@ionic/react';
import { AppPage } from '../../shared/components/AppPage';
import { ModulePendingNotice } from '../../shared/components/ModulePendingNotice';
import { useNovedades } from '../../state/useNovedades';

export function NuevaNovedadPage() {
  const { borradores } = useNovedades();
  const [mensaje, setMensaje] = useState('');

  const pendienteDeImplementacion = (event: FormEvent) => {
    event.preventDefault();
    // TODO: validar y conectar el guardado real del borrador.
    setMensaje('Formulario listo para conectar. Aún no se guardaron datos.');
  };

  return (
    <AppPage titulo="Nueva novedad" subtitulo="Paso 1 de 2" volverA="/inicio">
      <ModulePendingNotice>
        Los campos y el acceso al repositorio están preparados; falta conectar el guardado real.
      </ModulePendingNotice>

      <form onSubmit={pendienteDeImplementacion}>
        <IonList inset className="form-list">
          <IonItem>
            <IonInput label="Título" labelPlacement="stacked" name="titulo" />
          </IonItem>
          <IonItem>
            <IonTextarea
              label="Descripción inicial *"
              labelPlacement="stacked"
              name="descripcion"
              autoGrow
              placeholder="Describa una situación ficticia"
            />
          </IonItem>
          <IonItem>
            <IonInput
              label="Fecha de ocurrencia"
              labelPlacement="stacked"
              name="fechaOcurrencia"
              type="datetime-local"
            />
          </IonItem>
          <IonItem>
            <IonSelect label="Prioridad" labelPlacement="stacked" name="prioridad" value="media">
              <IonSelectOption value="baja">Baja</IonSelectOption>
              <IonSelectOption value="media">Media</IonSelectOption>
              <IonSelectOption value="alta">Alta</IonSelectOption>
            </IonSelect>
          </IonItem>
        </IonList>
        <IonNote className="module-meta">Borradores disponibles desde la capa común: {borradores.length}</IonNote>
        {mensaje && <p className="module-message" role="status">{mensaje}</p>}
        <IonButton type="submit" expand="block">Guardar borrador</IonButton>
        <IonButton type="button" expand="block" fill="outline" routerLink="/borradores">
          Ver borradores
        </IonButton>
      </form>
    </AppPage>
  );
}
