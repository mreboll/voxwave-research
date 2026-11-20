# Siguientes pasos

Lo que falta para que VoxWave pase de prototipo a algo validado, ordenado por impacto. Cada frente dice
qué hacer, con qué código del repositorio empezar y qué cuenta como «hecho». Contexto de cada punto en
[ml/RESULTADOS.md](ml/RESULTADOS.md) (sección 8) y en la sección 6 del [paper](paper/VoxWave_paper.pdf).

## 1. Piloto longitudinal (lo más importante)

NeuroVoz graba a cada persona una sola vez: el seguimiento solo está validado por simulación.

- **Qué:** sesiones diarias de ~30 s (dos frases y pa-ta-ka) con el móvil propio durante ≥ 3 meses,
  registrando la hora de la dosis, el estado ON/OFF declarado y las discinesias; UPDRS en consulta al
  principio y al final.
- **Para qué:** medir la variabilidad intra-persona real por tarea y por dial, el MDC con datos propios
  y recalibrar los umbrales del aviso (hoy z ≥ 1,5 durante 3 semanas, calibrado con un AR(1) simulado).
- **Código:** `ml/src/tracking.py` (regla), `calibrate_alerts.py` (calibración), `serve.py` (puntuación
  por grabación). Hace falta un formato de sesión; parte de `timeline_90d_sessions.csv`
  (`ml/export/CONTRATO.md`, sección 3).
- **Requisitos:** comité de ética, consentimiento y protección de datos (los audios son datos de salud).
- **Hecho cuando:** ICC test-retest y MDC por dial publicados con datos reales y regla recalibrada.

## 2. Datos externos con el canal controlado

- Solicitar **PC-GITA** (español colombiano, UPDRS y H&Y; incluye grabaciones en condiciones clínicas
  reales) y **EWA-DB** (eslovaco). Ver [docs/guides/datasets.md](docs/guides/datasets.md).
- Idealmente, grabar pacientes y controles en la misma sala y el mismo periodo.
- **Código:** copiar el patrón de `external_mdvr.py` / `external_italian.py` (ventanas de 5 s con ≥ 60 %
  de voz, sin reentrenar).
- **Hecho cuando:** AUROC externo con su control de solo canal cerca de 0,5.

## 3. Entrenamiento multi-corpus controlando la edad

`multi_corpus.py` muestra que entrenar con los tres corpus transfiere entre idiomas (sin castellano →
NeuroVoz 0,83), pero introduce un atajo de edad (ancianos frente a jóvenes sanos en ItalianPVS: 0,81).

- Necesita la edad de cada hablante (MDVR-KCL no la publica) para residualizarla igual que el canal.
- **Hecho cuando:** mantiene la transferencia y el control ancianos-jóvenes queda cerca de 0,5.

## 4. Fine-tuning robusto al canal

El fine-tuning SupCon (`finetune_ssl.py`, `modal_app.py`) llega a 0,96 pero aprende la sala (0,67 tras
descontar el canal).

- Probar aumento de datos con respuestas al impulso de sala y ruido, y proyección ortogonal del
  subespacio de canal sobre los embeddings.
- **Regla de aceptación:** solo vale si los controles de silencio y de canal se quedan cerca del azar.

## 5. Referencias por tarea y avisos por dial

- Línea base separada por tarea (frases, pa-ta-ka) y aviso por dial, con pesos estimados de medidas
  repetidas (hoy fijados desde la literatura: 1,0 F0 y rango tonal, 0,7 ritmo y pausas, 0,3 HNR).
- Depende del piloto (punto 1).

## 6. Producto y regulación

- Un producto comercial **no puede** usar modelos entrenados con NeuroVoz (CC BY-NC-ND): reentrenar con
  datos del piloto o corpus de licencia abierta (ItalianPVS, MDVR-KCL).
- Textos de la app según la guía FDA General Wellness (enero de 2026): no nombrar la enfermedad en
  avisos. Detalle en `ml/export/CONTRATO.md` (sección 4) y `docs/research/gemini_02_pitch_regulacion_datasets.md`.

## Reglas para cualquier experimento nuevo

1. Folds por hablante de `make_folds.py`; no ajustar nada sobre los folds de test.
2. Reportar siempre: AUROC con IC, emparejado por edad, ventana nov-dic 2016, correlación con el modelo
   de solo canal y, si se puede, el control de solo silencio.
3. Añadir el resultado a `ml/RESULTADOS.md` y un test si se añade lógica nueva (`ml/tests/`).
