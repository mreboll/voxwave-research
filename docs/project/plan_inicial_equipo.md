# Plan inicial del equipo (punto de partida de la investigación)

Este es el encargo con el que arrancó la parte de IA del proyecto (noviembre de 2026). Se conserva tal
cual porque explica las decisiones de diseño. Lo que se hizo finalmente, y qué cambió respecto al plan,
está en `ml/RESULTADOS.md` y en el paper (`paper/VoxWave_paper.pdf`).

---

Quick direction for the Parkinson's voice project. Heads up first: in NeuroVoz everyone was recorded
once, so you can't learn "getting worse" straight from it. What you can do is find which voice features
go with higher severity (UPDRS / H-Y), then have the app track those features daily against each
person's own baseline. So the job is: find the voice dials that mean Parkinson's, then watch them drift.

Everyone runs their own AI on a different angle. Shared rules:

- Split train/test by patient, not by file (each person has ~27 recordings, otherwise the accuracy is fake).
- Everyone uses the same 5 folds: one person makes folds.csv (patient id -> fold) and shares it.
- Every model outputs a "patient_id, score" CSV so the demo can plug it in.
- Use the sentences + pa-ta-ka recordings first. A May 2026 benchmark found vowels nearly useless on
  NeuroVoz (AUROC 0.53 vs 0.77 sentences, 0.75 pa-ta-ka).
- Run a "silence only" version of your model. A Sept 2026 paper got Parkinson's signal out of NeuroVoz
  silence, so if silence predicts it too, you're learning the room, not the disease.
- Watch age: PD folks are ~7 years older, so the model might just learn "old voice".

1. **Classic:** openSMILE eGeMAPS features (it's feature extraction, minutes, not training) ->
   logistic regression / XGBoost for PD vs healthy. Then rank which features track UPDRS: those are the
   "dials" the app watches daily. This is the baseline everyone has to beat. Shortcut:
   audio_features.csv in the dataset already has 17 precomputed voice features.
2. **Deep learning:** pretrained speech model (WavLM Base+ or HuBERT from Hugging Face), frozen, pull
   embeddings, logistic regression on top. Stretch: a 2025 paper fine-tuned wav2vec2/HuBERT with
   contrastive learning and hit ~0.92 AUROC on NeuroVoz (https://pmc.ncbi.nlm.nih.gov/articles/PMC12292552/).
3. **Tracking:** try DA-DSQA (https://huggingface.co/jaesungbae/da-dsqa, 2026), a tiny probe on Whisper
   large-v3 that gives a speech-severity score. Then build the daily logic: first 2 weeks = your
   baseline, alert only when the score keeps sliding for weeks, log pill timing (levodopa wear-off
   swings the voice more than months of disease). For real over-time data, UCI Parkinson's
   Telemonitoring is a free download: 42 patients, ~5,900 home recordings over 6 months (features, no
   audio). For the demo, fake a 90-day timeline sliding from a mild NeuroVoz patient to a severe one.
4. **Demo + business:** web app people actually see. Record voice in the browser (MediaRecorder API),
   show waveform, score, and a trend chart with pill markers. Pitch angles: neurologists see patients
   every 3-6 months and nobody watches in between; a phone is zero extra hardware. Pharma trials are
   who pays. Nobody has FDA clearance for voice-only Parkinson's progression tracking yet. Frame it as
   monitoring, not diagnosis, and say the 90-day timeline is simulated.

---

**Qué pasó con cada punto** (resumen; detalle en `ml/RESULTADOS.md`):

- Reglas compartidas: cumplidas. `ml/src/make_folds.py` genera `folds.csv` de forma determinista; el
  control de silencio confirmó el atajo (AUROC 0,83) y se añadieron controles de canal, edad y época.
- Ángulo 1: hecho (eGeMAPS 0,89 sin corregir; 0,84 con el canal descontado) y ranking de diales.
- Ángulo 2: hecho y superado. WavLM congelado con el canal descontado es el modelo principal (0,91).
  El fine-tuning contrastivo llega a 0,96, pero aprende la sala.
- Ángulo 3: DA-DSQA evaluado sin reentrenar (0,83 en frases). Lógica de seguimiento implementada y
  calibrada; UCI muestra que las vocales sostenidas no siguen la progresión; timeline de 90 días
  simulado.
- Ángulo 4: la demo web la desarrolla otro compañero (vox-wave-demo). Este repositorio aporta el modelo
  y el contrato de datos (`ml/export/CONTRATO.md`).
- La cifra de «3-6 meses entre visitas» no tiene fuente pública verificada; se reformuló como
  «revisiones espaciadas, a menudo de varios meses».
