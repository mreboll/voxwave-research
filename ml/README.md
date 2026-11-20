# VoxWave · pipeline de IA

Modelo de voz que detecta los cambios asociados al Parkinson, controla los atajos de grabación (sala,
micrófono, época, edad), se valida fuera de su corpus y se usa para vigilar la deriva frente a la
referencia personal de cada usuario. Prototipo de investigación: monitorización, no diagnóstico.

- Resultados e interpretación: [RESULTADOS.md](RESULTADOS.md)
- Paper: [../paper/VoxWave_paper.pdf](../paper/VoxWave_paper.pdf)
- Contrato de datos para la demo del equipo: [export/CONTRATO.md](export/CONTRATO.md)

## Instalación

Python 3.12+ (desarrollado en 3.14, Windows; CPU es suficiente para todo salvo el fine-tuning y los
modelos grandes, que se ejecutan en GPU con [Modal](https://modal.com)).

```bash
cd ml
python -m venv .venv
.venv/Scripts/python.exe -m pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m pytest -q tests      # 17 tests
```

Los datos no están en el repositorio: ver [../docs/guides/datasets.md](../docs/guides/datasets.md).

## Reglas de evaluación (no cambiarlas sin motivo)

- **Validación por hablante**: 5 folds de `make_folds.py` (estratificados por grupo × tercil de edad,
  semilla 42). `folds.csv` no se publica (deriva de NeuroVoz): se regenera igual con el script.
- Excluidos 6 IDs con audio pero sin metadata: HC_0068, HC_0069, HC_0084, PD_0059, PD_0068, PD_0069.
- Probabilidad por grabación → media por hablante. AUROC con IC bootstrap de hablantes (2.000).
- Hiperparámetros fijados de antemano; nunca se ajustan sobre los folds de test.
- **Todo modelo nuevo debe reportar**: AUROC, subconjunto emparejado por edad, ventana nov-dic 2016,
  correlación con el modelo «solo canal» y, si es posible, el control de solo silencio.
- Salida estándar: `results/scores/<modelo>.csv` con `patient_id, score` (no se publica).

## Orden de ejecución

Desde `ml/src` con `../.venv/Scripts/python.exe <script>`:

| # | Script | Qué hace | Salida |
|---|---|---|---|
| 1 | `make_folds.py` | Folds por hablante | `folds.csv` |
| 2 | `extract_egemaps.py` | eGeMAPS v02 por grabación (voz y solo silencio) | `features/egemaps_*.csv` |
| 3 | `extract_channel.py` | 8 descriptores de canal (suelo de ruido, SNR, espectro del silencio) | `features/channel.csv` |
| 4 | `train_baseline.py` | Ángulo 1: LogReg/XGBoost por tarea + controles | `results/baseline_summary.json` |
| 5 | `confound_analysis.py` | Modelo solo canal, residualización del canal en el fold, test de incremento | `results/confound_summary.json` |
| 6 | `rank_dials.py` → `severity_analysis.py` | Diales: d ajustada, ρ parcial con UPDRS/H&Y, ICC, MDC95, R² de canal | `results/dials_*.csv`, `severity_summary.json` |
| 7 | `extract_ssl.py microsoft/wavlm-base-plus` → `train_ssl.py wavlm-base-plus` | Ángulo 2: WavLM congelado (**modelo principal**: media de capas + canal descontado) | `results/ssl_*_summary.json` |
| 8 | `dadsqa.py` → `evaluate_dadsqa.py` | Ángulo 3: DA-DSQA sin reentrenar (Whisper large-v3; lento en CPU) | `results/dadsqa_summary.json` |
| 9 | `clean_audio.py`, `extract_variants.py`, `silence_after_cleaning.py`, `hygiene_analysis.py` | ¿Limpiar la señal quita el atajo? (no) | `results/hygiene_summary.json` |
| 10 | `improve_models.py [wavlm-large whisper-large-v3]`, `improve_layers.py` | Fusión, objetivo ordinal, modelos grandes, capas predeclaradas | `results/improve_summary.json`, `layers_summary.json` |
| 11 | `uci_tracking.py`, `calibrate_alerts.py` | Comprobación longitudinal (UCI) y calibración de la alerta | `results/uci/` |
| 12 | `demo_timeline.py` → `export_model.py` → `export_contract.py` | Timeline simulado de 90 días, modelo final, contrato de datos | `results/demo/`, `models/`, `export/` |
| 13 | `external_mdvr.py`, `external_italian.py` | Validación externa sin reentrenar | `results/external_*.json` |
| 14 | `multi_corpus.py` | Entrenamiento con los tres corpus (deja-uno-fuera y CV conjunta) | `results/multi_corpus.json` |
| 15 | `make_figures.py`, `make_figures_en.py` | Figuras (castellano / inglés para el paper) | `results/figures*/` |

### Pasos en GPU (Modal)

Requieren `python -m modal setup` y subir los audios a un volumen **privado**. Comprueba antes que la
licencia de cada dataset lo permite (NeuroVoz: solo uso de investigación, sin redistribución). Borra
el volumen al terminar.

| Script | Uso |
|---|---|
| `modal_app.py` | Fine-tuning SupCon por fold (`--model-name microsoft/wavlm-base-plus` o `facebook/hubert-base-ls960`); el código de entrenamiento está en `finetune_ssl.py` (`--smoke` lo prueba en CPU) |
| `modal_embed.py` | Embeddings de WavLM Large y Whisper large-v3 (`--model-name ...`) |
| `modal_external.py` | Rasgos para la validación externa (`--dataset mdvr` o `italian`); después se puntúa en local con `external_*.py` |
| `modal_api.py` | Despliega la API de puntuación (`python -m modal deploy src/modal_api.py`) |

Con Git Bash en Windows, exporta `MSYS_NO_PATHCONV=1` antes de `modal volume put`, o las rutas remotas
como `/audios` se convierten en `C:/Program Files/Git/audios`.

### API local

```bash
.venv/Scripts/python.exe -m uvicorn serve:app --port 8000 --app-dir src
```

`POST /api/score` (WAV) devuelve el índice vocal, los 6 diales y el control de calidad;
`GET /api/timeline` devuelve el timeline simulado. Contrato completo en `export/CONTRATO.md`.

## Qué hay en el repositorio y qué no

| Incluido | No incluido (se regenera) |
|---|---|
| Código (`src/`), tests, `requirements.txt` | `features/` (rasgos por grabación) |
| Resúmenes agregados `results/*.json`, ranking de diales, figuras | `results/scores/` (puntuaciones por paciente) |
| `export/CONTRATO.md`, timeline simulado, referencia de diales | `export/patient_*.csv`, `folds.csv`, `models/` |
| | `.venv/`, datos de `../data` y `../data_external` |

Motivo: la licencia de NeuroVoz (CC BY-NC-ND 4.0) no permite redistribuir sus derivados.
