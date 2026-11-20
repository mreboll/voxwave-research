# Prompt para Gemini Deep Research: datasets para validar VoxWave

Copia todo lo que hay debajo de la línea y pégalo en Gemini con Deep Research. Guarda la respuesta como
`VoxWave/Datasets validacion Parkinson.md`.

---

Necesito un inventario verificado de **datasets públicos o solicitables de habla en enfermedad de
Parkinson** que sirvan para dos cosas: (A) **validación externa** de un modelo entrenado en NeuroVoz
(castellano, frases leídas y diadococinesia pa-ta-ka) y (B) **validación longitudinal** (la misma
persona grabada muchas veces a lo largo de semanas o meses).

Para cada dataset dame, con enlace a la fuente primaria (página oficial, Zenodo, IEEE DataPort,
PhysioNet, GitHub o el paper que lo describe):

1. Nombre, institución, año e idioma.
2. Número de PD y de controles, y si hay **escalas clínicas por persona**: MDS-UPDRS (total, parte III
   o ítem 3.1 de habla), Hoehn & Yahr, años de evolución y estado de medicación ON/OFF.
3. **Tareas de habla**: frases leídas, párrafo, habla espontánea, pa-ta-ka u otras diadococinesias,
   vocales sostenidas. Indica si hay frases leídas o pa-ta-ka, que es lo que usa nuestro modelo.
4. **Condiciones de grabación**: ¿PD y controles se grabaron en la misma sala, con el mismo equipo y en
   la misma época? Cualquier dato sobre micrófono, móvil o sala. Es crítico: en NeuroVoz el silencio
   solo predice el diagnóstico porque los grupos se grabaron en épocas distintas.
5. **Longitudinal**: ¿hay varias sesiones por persona? ¿Cuántas, con qué intervalo y durante cuánto
   tiempo? ¿Hay grabaciones diarias o semanales desde casa con móvil? ¿Se registró la hora de la toma
   de levodopa?
6. **Acceso y licencia exactos**: descarga abierta, registro, formulario o acuerdo firmado; licencia
   (CC BY, CC BY-NC, CC BY-NC-ND u otra); si permite uso comercial; plazo de respuesta si se conoce.
7. Tamaño de la descarga y formato (WAV o solo rasgos).

Incluye como mínimo, verificando cada uno: MDVR-KCL (King's College London), ItalianPVS, PC-GITA,
EWA-DB, mPower (Sage Bionetworks), WATCH-PD, PPMI (si tiene audio), GITA longitudinal, el corpus checo
de Rusz (Praga), Parkinson's Voice Initiative, Oxford/Little, PDSpeech, PARCZ, y cualquier otro
publicado entre 2020 y 2026 con audio y escalas clínicas.

Termina con una tabla comparativa y una recomendación ordenada:
- Qué dataset descargar **hoy mismo** para una validación externa rápida, en español u otro idioma, con
  frases o pa-ta-ka y con PD y controles grabados en las mismas condiciones.
- Qué dataset o estudio es la mejor opción para validar **seguimiento longitudinal**, aunque haya que
  solicitarlo.

No inventes cifras ni licencias. Si un dato no está en una fuente verificable, escribe «no consta».
