import { IonIcon, IonNote } from '@ionic/react';
import { constructOutline } from 'ionicons/icons';

interface ModulePendingNoticeProps {
  children: string;
}

export function ModulePendingNotice({ children }: ModulePendingNoticeProps) {
  return (
    <div className="pending-notice" role="note">
      <IonIcon icon={constructOutline} aria-hidden="true" />
      <div>
        <strong>Funcionalidad en integración</strong>
        <IonNote>{children}</IonNote>
      </div>
    </div>
  );
}
