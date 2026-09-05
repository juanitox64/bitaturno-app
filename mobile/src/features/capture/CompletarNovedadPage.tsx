import { useState } from 'react';
import {
  IonAlert,
  IonButton,
  IonInput,
  IonItem,
  IonList,
  IonSelect,
  IonSelectOption,
  IonTextarea,
  IonToast,
} from '@ionic/react';
import { useNavigate, useParams } from 'react-router-dom';
import type { DatosNovedad, Novedad, PrioridadNovedad } from '../../domain/novedad';
import { AppPage } from '../../shared/components/AppPage';
import { rutaHistorico } from '../../shared/constants/routes';
import {
  ErrorValidacionNovedad,
  validarFinalizacion,
} from '../../shared/validation/novedadValidation';
import { useNovedades } from '../../state/useNovedades';

export function CompletarNovedadPage() {
  const { id = '' } = useParams<{ id: string }>();
  const { obtenerPorId } = useNovedades();
  const borrador = obtenerPorId(id);
  const editable = borrador?.estado === 'borrador';

  if (!borrador) {
    return (
      <AppPage titulo="Completar novedad" subtitulo="Paso 2 de 2" volverA="/borradores">
        <div className="empty-state">No se encontró el borrador solicitado.</div>
        <IonButton expand="block" routerLink="/borradores">Volver a borradores</IonButton>
      </AppPage>
    );
  }

  if (!editable) {
    return (
      <AppPage titulo="Completar novedad" subtitulo="Registro no editable" volverA="/historico">
        <div className="empty-state">
          La novedad ya fue finalizada y debe consultarse desde el histórico.
        </div>
        <IonButton expand="block" routerLink={rutaHistorico(borrador.id)}>
          Ver detalle
        </IonButton>
      </AppPage>
    );
  }

  // La `key` fuerza a React a remontar el formulario cada vez que cambia el
  // borrador, reiniciando su estado sin necesidad de un useEffect + setState.
  return <FormularioCompletarNovedad key={borrador.id} borrador={borrador} />;
}

function FormularioCompletarNovedad({ borrador }: { borrador: Novedad }) {
  const navigate = useNavigate();
  const { actualizarBorrador, finalizar, eliminarBorrador } = useNovedades();
  const id = borrador.id;

  const [datos, setDatos] = useState<DatosNovedad>(() => ({
    titulo: borrador.titulo,
    descripcion: borrador.descripcion,
    disciplina: borrador.disciplina,
    tipo: borrador.tipo,
    turno: borrador.turno,
    prioridad: borrador.prioridad,
    fechaOcurrencia: borrador.fechaOcurrencia,
  }));
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [mensaje, setMensaje] = useState('');
  const [confirmarEliminacion, setConfirmarEliminacion] = useState(false);

  const actualizarCampo = <K extends keyof DatosNovedad>(campo: K, valor: DatosNovedad[K]) => {
    setDatos((actuales) => ({ ...actuales, [campo]: valor }));
    setErrores((actuales) => {
      if (!actuales[campo]) return actuales;
      const copia = { ...actuales };
      delete copia[campo];
      return copia;
    });
  };

  const guardarCambios = () => {
    try {
      actualizarBorrador(id, datos);
      setErrores({});
      setMensaje('Cambios guardados correctamente.');
    } catch (error) {
      if (error instanceof ErrorValidacionNovedad) {
        setErrores(error.campos);
      } else {
        setMensaje(error instanceof Error ? error.message : 'No fue posible guardar los cambios.');
      }
    }
  };

  const finalizarRegistro = () => {
    const validacion = validarFinalizacion(datos);
    setErrores(validacion);
    if (Object.keys(validacion).length > 0) {
      setMensaje('Complete los campos obligatorios antes de finalizar.');
      return;
    }

    try {
      const finalizada = finalizar(id, datos);
      navigate(rutaHistorico(finalizada.id), { replace: true });
    } catch (error) {
      if (error instanceof ErrorValidacionNovedad) {
        setErrores(error.campos);
      } else {
        setMensaje(error instanceof Error ? error.message : 'No fue posible finalizar el registro.');
      }
    }
  };

  const confirmarYEliminar = () => {
    try {
      eliminarBorrador(id);
      navigate('/borradores', { replace: true });
    } catch (error) {
      setMensaje(error instanceof Error ? error.message : 'No fue posible eliminar el borrador.');
    }
  };

  return (
    <AppPage titulo="Completar novedad" subtitulo="Paso 2 de 2" volverA="/borradores">
      <IonList inset className="form-list">
        <IonItem>
          <IonInput
            label="Título *"
            labelPlacement="stacked"
            value={datos.titulo}
            className={errores.titulo ? 'ion-invalid ion-touched' : ''}
            errorText={errores.titulo}
            onIonInput={(event) => actualizarCampo('titulo', event.detail.value ?? '')}
          />
        </IonItem>
        <IonItem>
          <IonTextarea
            label="Descripción *"
            labelPlacement="stacked"
            value={datos.descripcion}
            autoGrow
            maxlength={500}
            counter
            className={errores.descripcion ? 'ion-invalid ion-touched' : ''}
            errorText={errores.descripcion}
            onIonInput={(event) => actualizarCampo('descripcion', event.detail.value ?? '')}
          />
        </IonItem>
        <IonItem>
          <IonSelect
            label="Disciplina *"
            labelPlacement="stacked"
            value={datos.disciplina}
            className={errores.disciplina ? 'ion-invalid ion-touched' : ''}
            onIonChange={(event) => actualizarCampo('disciplina', event.detail.value as string)}
          >
            <IonSelectOption value="Disciplina Alfa">Disciplina Alfa</IonSelectOption>
            <IonSelectOption value="Disciplina Beta">Disciplina Beta</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect
            label="Tipo *"
            labelPlacement="stacked"
            value={datos.tipo}
            className={errores.tipo ? 'ion-invalid ion-touched' : ''}
            onIonChange={(event) => actualizarCampo('tipo', event.detail.value as string)}
          >
            <IonSelectOption value="Observación">Observación</IonSelectOption>
            <IonSelectOption value="Incidencia">Incidencia</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect
            label="Turno *"
            labelPlacement="stacked"
            value={datos.turno}
            className={errores.turno ? 'ion-invalid ion-touched' : ''}
            onIonChange={(event) => actualizarCampo('turno', event.detail.value as string)}
          >
            <IonSelectOption value="Turno A">Turno A</IonSelectOption>
            <IonSelectOption value="Turno B">Turno B</IonSelectOption>
          </IonSelect>
        </IonItem>
        <IonItem>
          <IonSelect
            label="Prioridad *"
            labelPlacement="stacked"
            value={datos.prioridad}
            onIonChange={(event) => actualizarCampo(
              'prioridad',
              event.detail.value as PrioridadNovedad,
            )}
          >
            <IonSelectOption value="baja">Baja</IonSelectOption>
            <IonSelectOption value="media">Media</IonSelectOption>
            <IonSelectOption value="alta">Alta</IonSelectOption>
          </IonSelect>
        </IonItem>
      </IonList>

      {Object.keys(errores).length > 0 && (
        <div className="form-error" role="alert">
          <strong>Revise los campos obligatorios:</strong>
          <ul>
            {Object.values(errores).map((error) => <li key={error}>{error}</li>)}
          </ul>
        </div>
      )}

      <IonButton expand="block" onClick={guardarCambios}>
        Guardar cambios
      </IonButton>
      <IonButton expand="block" color="success" onClick={finalizarRegistro}>
        Finalizar registro
      </IonButton>
      <IonButton
        expand="block"
        fill="outline"
        color="danger"
        onClick={() => setConfirmarEliminacion(true)}
      >
        Eliminar borrador
      </IonButton>

      <IonAlert
        isOpen={confirmarEliminacion}
        header="Eliminar borrador"
        message="Esta acción eliminará el borrador local. ¿Desea continuar?"
        buttons={[
          { text: 'Cancelar', role: 'cancel' },
          { text: 'Eliminar', role: 'destructive', handler: confirmarYEliminar },
        ]}
        onDidDismiss={() => setConfirmarEliminacion(false)}
      />
      <IonToast
        isOpen={Boolean(mensaje)}
        message={mensaje}
        duration={2500}
        onDidDismiss={() => setMensaje('')}
      />
    </AppPage>
  );
}