import { useState, type FormEvent } from 'react';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonContent,
  IonInput,
  IonItem,
  IonList,
  IonNote,
  IonPage,
  IonText,
} from '@ionic/react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useDemoSession } from './demoSession';

interface LocationState {
  desde?: string;
}

export function LoginPage() {
  const { usuario: sesionActiva, iniciar } = useDemoSession();
  const navigate = useNavigate();
  const location = useLocation();
  const [usuario, setUsuario] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  if (sesionActiva) return <Navigate to="/inicio" replace />;

  const ingresar = (event: FormEvent) => {
    event.preventDefault();
    if (!usuario.trim() || !password) {
      setError('Ingrese un usuario y una contraseña ficticios.');
      return;
    }
    iniciar(usuario);
    setPassword('');
    const state = location.state as LocationState | null;
    navigate(state?.desde ?? '/inicio', { replace: true });
  };

  return (
    <IonPage>
      <IonContent fullscreen className="login-content">
        <div className="login-shell">
          <div className="brand-block">
            <div className="brand-mark" aria-hidden="true">BT</div>
            <p className="eyebrow">Registro de jornada</p>
            <h1>BitaTurno</h1>
            <p>Captura, completa y consulta novedades desde una experiencia híbrida.</p>
          </div>

          <IonCard className="login-card">
            <IonCardContent>
              <div className="demo-badge">Demostración académica: use datos ficticios</div>
              <form onSubmit={ingresar} noValidate>
                <IonList lines="none">
                  <IonItem>
                    <IonInput
                      label="Usuario"
                      labelPlacement="stacked"
                      autocomplete="username"
                      placeholder="usuario.demo"
                      value={usuario}
                      onIonInput={(event) => setUsuario(event.detail.value ?? '')}
                      required
                    />
                  </IonItem>
                  <IonItem>
                    <IonInput
                      label="Contraseña"
                      labelPlacement="stacked"
                      autocomplete="current-password"
                      type="password"
                      value={password}
                      onIonInput={(event) => setPassword(event.detail.value ?? '')}
                      required
                    />
                  </IonItem>
                </IonList>
                {error && <IonText color="danger"><p className="form-error">{error}</p></IonText>}
                <IonButton expand="block" type="submit" className="primary-action">
                  Ingresar a la demostración
                </IonButton>
              </form>
            </IonCardContent>
          </IonCard>
          <IonNote className="privacy-note">
            Las credenciales no se transmiten y la contraseña no se almacena.
          </IonNote>
        </div>
      </IonContent>
    </IonPage>
  );
}
