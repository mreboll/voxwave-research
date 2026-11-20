# Datos: cómo conseguirlos y dónde ponerlos

**Ningún audio ni metadato de los datasets está en este repositorio.** NeuroVoz tiene licencia CC BY-NC-ND 4.0
y un acuerdo de uso que prohíbe redistribuir el material y sus derivados; por eso tampoco se publican
los rasgos por grabación, las puntuaciones por paciente, `folds.csv` ni los modelos entrenados. Todo se
regenera con los scripts de `ml/src/` una vez descargados los datos.

Las carpetas `data/` y `data_external/` están en `.gitignore`. La estructura esperada es:

```
voxwave-research/
  data/                          NeuroVoz
    audios/                      2.976 .wav  (p. ej. PD_PIDIO_0004.wav)
    metadata/metadata_pd.csv
    metadata/metadata_hc.csv
    transcriptions/ grbas/ audio_features/   (incluidos en la descarga; no se usan en el modelo)
  data_external/
    mdvr_kcl/extracted/26-29_09_2017_KCL/{ReadText,SpontaneousDialogue}/{HC,PD}/*.wav
    italianpvs/<15 Young Healthy Control | 22 Elderly Healthy Control | 28 People with Parkinson's disease>/...
    uci_telemonitoring/parkinsons_updrs.data
```

## NeuroVoz (castellano; desarrollo del modelo)

- Fuente: Zenodo, DOI 10.5281/zenodo.10777657 (código: github.com/BYO-UPM/Neurovoz_Dababase).
- Licencia: **CC BY-NC-ND 4.0**, uso de investigación no comercial, con acuerdo de uso: no reidentificar,
  no redistribuir, citar el corpus.
- Cita: Mendes-Laureano J, et al. NeuroVoz: a Castillian Spanish corpus of parkinsonian speech.
  *Scientific Data* 11, 1367 (2024).
- Colocar: descomprimir de forma que existan `data/audios/` y `data/metadata/`.
- Notas: 108 hablantes con metadata (53 PD / 55 HC). Seis IDs con audio pero sin metadata se excluyen
  (ver `ml/README.md`). PD y HC se grabaron en épocas distintas: ver `ml/RESULTADOS.md`, sección 1.

## MDVR-KCL (inglés; validación externa limpia)

- Fuente: Zenodo, DOI 10.5281/zenodo.2867216 (un ZIP de 606 MB, `26_29_09_2017_KCL.zip`).
- Licencia: **CC BY 4.0**. Cita: Jaeger H, Trivedi D, Stadtschnitzer M (2019), MDVR-KCL, Zenodo.
- Colocar: `data_external/mdvr_kcl/extracted/` (descomprimir ahí el ZIP).
- Notas: 37 hablantes; mismo móvil, misma sala y misma semana para todos. Un archivo viene mal nombrado
  (`ID22hc_0_0_0.wav`); el parser lo admite. No publica edades.

## ItalianPVS (italiano; validación externa)

- Guía paso a paso (requiere cuenta IEEE gratuita): `docs/guides/guia_italianpvs.md`.
- Licencia: **CC BY 4.0**. Cita: Dimauro G, et al. *IEEE Access* 5:22199-22208 (2017).
- **Las carpetas llevan nombres reales de personas.** `ml/src/external_italian.py` asigna
  identificadores anónimos y nunca escribe nombres en los resultados. No subas copias con los nombres
  originales a ningún servicio.
- Notas: 10 PD grabados a 44,1 kHz y el resto a 16 kHz (se remuestrea todo a 16 kHz). En esta versión no
  hay UPDRS ni H&Y.

## UCI Parkinson's Telemonitoring (inglés; comprobación longitudinal)

```bash
mkdir -p data_external/uci_telemonitoring
curl -L -o data_external/uci_telemonitoring/parkinsons_updrs.data \
  https://archive.ics.uci.edu/ml/machine-learning-databases/parkinsons/telemonitoring/parkinsons_updrs.data
```

- Licencia: CC BY 4.0. Cita: Tsanas A, et al. *IEEE Trans Biomed Eng* 57(4):884-893 (2010).
- Notas: solo rasgos de vocal sostenida y UPDRS interpolado entre 3 visitas.

## Candidatos para el futuro (por solicitud)

- **PC-GITA** (español colombiano, UPDRS y H&Y completos; incluye grabaciones en condiciones clínicas
  reales): solicitud al GITA Lab (Universidad de Antioquia).
- **EWA-DB** (eslovaco, H&Y I-II): solicitud vinculada a *Scientific Data* (2024).
- **Speech Accessibility Project** (inglés, multisesión, con acuerdo de uso).

Ver `docs/research/gemini_02_pitch_regulacion_datasets.md` y `gemini_03_biomarcadores_robustos.md`.
