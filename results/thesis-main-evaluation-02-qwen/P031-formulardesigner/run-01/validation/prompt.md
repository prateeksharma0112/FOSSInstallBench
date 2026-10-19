# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Formulardesigner

**Description:** Modular form designer for creating and maintaining digital, accessible forms in JSON format – KERN-UX based and ready for your adaptation.

## Supplied installation guide

## Guide: Installation.md

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

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## What was done (container: Ubuntu 22.04, working directory /workspace, repo @seitenbau-dev/formulardesigner v1.0.2 already checked out)

**Prerequisite (not in guide):** Node.js/npm were absent. Installed Node.js v22.20.0 by downloading the official linux-x64 tarball from nodejs.org and extracting it into /usr/local (node v22.20.0, npm 10.9.3 available system-wide). Chose Node 22 LTS because the project uses Vite 8, which requires Node 20.19+/22+.

**Installation (following Installation.md "Beispielanwendung starten" section, `npm run start:example` = `npm run build && cd example && npm install && npm run dev`, executed stepwise):**
1. `npm install` in /workspace — added 287 packages, exit 0 (only peer-dependency warnings for @tiptap, no failures).
2. `npm run build` in /workspace — `tsc -p ./tsconfig.json && vite build && tsc` succeeded, exit 0; produced /workspace/dist/formulardesigner.es.js (~968 kB), /workspace/dist/assets/index.css and .d.ts type declarations.
3. `npm install` in /workspace/example — 128 packages; the example's dependency `@seitenbau-dev/formulardesigner: file:..` resolved as a symlink /workspace/example/node_modules/@seitenbau-dev/formulardesigner -> /workspace (local package linkage).
4. `npm run dev` in /workspace/example — started via `nohup ... &` (non-interactive; log at /tmp/vite-dev.log). Vite v8.3.0 reports "ready in 1071 ms" and is still running in the background, serving at http://localhost:5173/ (Local only, no --host).

**Resulting state / access points:**
- Library source + built dist: /workspace (dist/formulardesigner.es.js, dist/src/**/*.d.ts).
- Example app: /workspace/example; running dev server reachable at http://localhost:5173 (Vite process still active; restart later with `cd /workspace/example && npm run dev`).
- The only entry in the Vite log other than "ready" was a 404 from a deliberately probed non-existent dep-optimizer path during my checks; no app or build errors.

**Incomplete/unknown:** none. A headless browser was additionally installed (/root/.cache/ms-playwright/chromium_headless_shell-1228) solely for verification; temporary files in /tmp were cleaned up (vite log kept at /tmp/vite-dev.log).

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.