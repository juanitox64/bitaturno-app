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
import { useNavigate } from 'react-router-dom';
import type { PrioridadNovedad } from '../../domain/novedad';
import { AppPage } from '../../shared/components/AppPage';
import { rutaBorrador } from '../../shared/constants/routes';
import {
  ErrorValidacionNovedad,
  validarBorrador,
} from '../../shared/validation/novedadValidation';
import { useNovedades } from '../../state/useNovedades';

export function NuevaNovedadPage() {
  const navigate = useNavigate();
  const { borradores, guardarBorrador } = useNovedades();
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [fechaOcurrencia, setFechaOcurrencia] = useState('');
  const [prioridad, setPrioridad] = useState<PrioridadNovedad>('media');
  const [errores, setErrores] = useState<Record<string, string>>({});
  const [mensaje, setMensaje] = useState('');
  const [guardando, setGuardando] = useState(false);

  const guardar = (event: FormEvent) => {
    event.preventDefault();
    if (guardando) return;

    const datos = {
      titulo,
      descripcion,
      fechaOcurrencia,
      prioridad,
    };
    const validacion = validarBorrador(datos);
    setErrores(validacion);
    setMensaje('');
    if (Object.keys(validacion).length > 0) return;

    try {
      setGuardando(true);
      const novedad = guardarBorrador(datos);
      navigate(rutaBorrador(novedad.id), { replace: true });
    } catch (error) {
      if (error instanceof ErrorValidacionNovedad) {
        setErrores(error.campos);
      } else {
        setMensaje(error instanceof Error ? error.message : 'No fue posible guardar el borrador.');
      }
    } finally {
      setGuardando(false);
    }
  };

  return (
    <AppPage titulo="Nueva novedad" subtitulo="Paso 1 de 2" volverA="/inicio">
      <p className="module-meta">
        Registre una descripción inicial. La clasificación completa puede agregarse después.
      </p>

      <form onSubmit={guardar} noValidate>
        <IonList inset className="form-list">
          <IonItem>
            <IonInput
              label="Título"
              labelPlacement="stacked"
              value={titulo}
              maxlength={100}
              onIonInput={(event) => setTitulo(event.detail.value ?? '')}
              helperText="Opcional mientras el registro sea borrador."
            />
          </IonItem>
          <IonItem>
            <IonTextarea
              label="Descripción inicial *"
              labelPlacement="stacked"
              value={descripcion}
              maxlength={500}
              counter
              autoGrow
              placeholder="Describa una situación ficticia"
              className={errores.descripcion ? 'ion-invalid ion-touched' : ''}
              errorText={errores.descripcion}
              onIonInput={(event) => {
                setDescripcion(event.detail.value ?? '');
                if (errores.descripcion) setErrores({});
              }}
            />
          </IonItem>
          <IonItem>
            <IonInput
              label="Fecha de ocurrencia"
              labelPlacement="stacked"
              type="datetime-local"
              value={fechaOcurrencia}
              onIonInput={(event) => setFechaOcurrencia(event.detail.value ?? '')}
            />
          </IonItem>
          <IonItem>
            <IonSelect
              label="Prioridad"
              labelPlacement="stacked"
              value={prioridad}
              onIonChange={(event) => setPrioridad(event.detail.value as PrioridadNovedad)}
            >
              <IonSelectOption value="baja">Baja</IonSelectOption>
              <IonSelectOption value="media">Media</IonSelectOption>
              <IonSelectOption value="alta">Alta</IonSelectOption>
            </IonSelect>
          </IonItem>
        </IonList>

        <IonNote className="module-meta">
          Borradores actuales: {borradores.length}
        </IonNote>
        {mensaje && <p className="form-error" role="alert">{mensaje}</p>}

        <IonButton type="submit" expand="block" disabled={guardando}>
          {guardando ? 'Guardando…' : 'Guardar borrador'}
        </IonButton>
        <IonButton type="button" expand="block" fill="outline" routerLink="/borradores">
          Ver borradores
        </IonButton>
      </form>
    </AppPage>
  );
}
