## Schnellstart

### Installation

```bash
npm install @seitenbau-dev/formulardesigner
```

### Grundlegende Integration

```tsx
import { FormularDesigner } from '@seitenbau-dev/formulardesigner';
import { FormularDesignerHandle } from '@seitenbau-dev/formulardesigner/types';
import { useRef, useState } from 'react';

const modules = []; // Ihre Module (siehe unten)

function App() {
  const designerRef = useRef<HTMLDivElement & FormularDesignerHandle>(null);
  const [form, setForm] = useState(getEmptyForm());
  const [isDirty, setIsDirty] = useState(false);

  return <FormularDesigner modules={modules} form={form} ref={designerRef} onFormChange={setIsDirty} />;
}

function getEmptyForm() {
  return {
    id: 'form-1',
    sections: [{ fieldGroups: [], title: '' }],
    engineVersion: '2',
  };
}
```

### Zugriff auf das Formular-Modell

Über die `ref` können Sie das aktuelle Formular-Modell abrufen:

```tsx
const handleDownload = () => {
  if (!designerRef.current) return;
  const model = designerRef.current.getModel();
  const json = JSON.stringify(model, null, 2);
  // json speichern oder über API senden
};
```

### Dirty-State zurücksetzen

Nach erfolgreichem Laden oder Speichern eines Formulars können Sie den Dirty-State zurücksetzen:

```tsx
designerRef.current.setDirtyForm(false);
```

## Beispielanwendung starten

Dieses Repository enthält eine Beispielanwendung unter `example/`. Im Root-Verzeichnis kann nach Installation der Abhängigkeiten nachfolgendes Run-Skript ausgeführt werden:

```bash
npm install

npm run start:example
```

Die Beispielanwendung ist dann unter `http://localhost:5173` erreichbar.
