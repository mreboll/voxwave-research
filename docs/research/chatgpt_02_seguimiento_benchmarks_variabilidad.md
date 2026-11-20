# Investigación (ChatGPT, 2026-11-20, 2.ª consulta): DA-DSQA en NeuroVoz, benchmark mayo 2026, UCI Telemonitoring, variabilidad

## 1. DA-DSQA (arXiv 2603.15988v3, 16-jun-2026)
- NeuroVoz solo como evaluación externa (no entrena ni calibra). Entrena con SAP (etiquetado y sin etiquetar) + LibriSpeech.
- NeuroVoz en su tabla: español, etiqueta H-Y, 1,7 h, 98 hablantes; no detallan tareas.
- Métricas vs H-Y (§5.2, Tabla 2):

| Modelo | Spearman | Pearson |
|---|---|---|
| Baseline | 0,575 | 0,601 |
| DA-DSQA L-coarse | 0,617 | 0,630 |
| HuBERT probe | 0,705 | 0,706 |

- Los autores sospechan sobreajuste del HuBERT probe a habla de Parkinson.
- Ojo: correlaciones con H-Y sobre todos los hablantes (PD+HC), probablemente con el mismo confusor de canal.

## 2. Benchmark mayo 2026: arXiv 2605.14066, "A Benchmark for Early-stage PD Detection from Speech"
- NeuroVoz 108 (53 PD / 55 HC), igual que nuestro folds.csv.
- Tareas: /a/, pa-ta-ka, frases. Modelos: BDHPD, InceptionPD, RECA-PD.
- AUROC (Tabla 2, configuración AllPD, media ± sd de 5 semillas): /a/ 0,53±0,03 (InceptionPD); frases 0,77±0,01 (RECA-PD); pa-ta-ka 0,75±0,03 (RECA-PD).
- División: 5 folds por hablante, estratificada por dataset, diagnóstico y sexo; 6 PD temprano + 6 HC por fold de val/test; checkpoint por AUC de validación; umbral por F1 de validación.
- Preprocesado: mono, 16 kHz, WAV de 16 bits, normalización de pico (SoX), máximo 10 s.

## 3. UCI Parkinson's Telemonitoring
- https://archive.ics.uci.edu/dataset/189/parkinsons+telemonitoring (ZIP: https://archive.ics.uci.edu/static/public/189/parkinsons%2Btelemonitoring.zip)
- 5875 filas, 42 PD (28 H / 14 M), unos 6 meses, grabaciones aproximadamente semanales, 6 fonaciones /a/ por sesión, 24 kHz y 16 bits. Solo rasgos, sin audio.
- Columnas: subject#, age, sex, test_time (días desde el inicio), motor_UPDRS, total_UPDRS, Jitter(%), Jitter(Abs), Jitter:RAP, Jitter:PPQ5, Jitter:DDP, Shimmer, Shimmer(dB), Shimmer:APQ3/APQ5/APQ11, Shimmer:DDA, NHR, HNR, RPDE, DFA, PPE.
- El UPDRS está interpolado linealmente entre las visitas clínicas (inicio, 3 meses y 6 meses), según Tsanas et al. Las etiquetas semanales no son mediciones independientes.
- Solo hay vocal sostenida, la tarea que menos información aporta en NeuroVoz.

## 4. Variabilidad (sin umbral universal publicado)
- mPower test-retest (JMIR 2021): ICC medio de rasgos de voz 0,33 a 1 h y 0,26 a 1 mes (/a/ grabada con móvil).
- Variabilidad intraindividual PD vs HC (2025, 24 PD + 8 HC, 195 muestras): sin diferencias significativas.
- Stegmann et al. 2020 (sanos y ELA), mediana del WSCV: vocal sostenida 79 %, frases 29 %, habla conectada 52 %. Las frases son las más estables.
- Recomendación: línea base de 14 días por paciente y por tarea; mediana + MAD; z robusto = (x - mediana) / (1,4826·MAD); alerta provisional con |z| ≥ 3 sostenido en varias sesiones (no validado clínicamente); MDC95 = 1,96·√2·SEM, con SEM = SD·√(1-ICC), usando el ICC del propio protocolo.
- ChatGPT NO cubrió el efecto ON/OFF de la levodopa sobre la voz (pendiente).
- Descartada una cifra anterior de 5,34–7,64 dB (sin fuente).

## 5. Repetibilidad intraindividual por rasgo (ChatGPT, 3.ª consulta)
Conclusión: la literatura NO publica SD intrasujeto, CV, ICC y MDC por rasgo para voz con móvil en casa. No se puede calcular un MDC a partir de ICC agregados → hay que estimarlo con nuestros propios datos.
- Myong et al. 2025 (PMC12614394): 20 PD + 20 HC, Galaxy S10 en el hospital, /a/ /i/ 10 s y /dadada/ /pa-ta-ka/ 5 s, 3 repeticiones. La Tabla 5 da medias ± SD ENTRE pacientes (no intrasujeto). Sin ICC ni MDC.
- mPower, Sahandi Far et al. 2021 (JMIR e26608): 49 676 grabaciones /a/ de 2184 participantes (PD autodeclarado). ICC 1-1 medio de los mejores rasgos de voz: 0,39 (1.ª repetición), 0,24 (5.ª repetición), 0,33 a 1 h, 0,26 a 1 mes; valores por rasgo en el suplemento (S5-S8, Fig. 3; incluye shimmer `shbd`). Hay efecto de aprendizaje.
- WATCH-PD, Johnson et al. 2024 (PMC11397844): 82 PD + 50 HC, 1 año, iPhone en casa cada 2 semanas + visitas clínicas. % de rasgos con ICC ≥ 0,6 (Tabla 4): /ahh/ 75,8 % casa-clínica y 78,2 % test-retest; pa-ta-ka 74,7 % y 80,6 %. Sin ICC por rasgo individual. Las frases se grabaron pero no se analizaron.
- Abola & Wolden 2025 (PMC12035574, Oxford PD dataset): la variabilidad intraindividual no difiere entre PD y HC (todos los d entre -0,30 y 0,34, n.s.). No sirve para fijar umbrales.
- Implicación: VoxWave debe medir su propio ICC/SEM/MDC por rasgo y tarea. En NeuroVoz se puede hacer con el ICC entre repeticiones de frases (rank_dials.py) y en un piloto con grabaciones diarias repetidas.

## 6. Levodopa ON/OFF, fluctuación intradía y progresión anual (Gemini; completo en VoxWave/"Medición Acústica Vocal en Parkinson.md")
- Efecto agudo de la levodopa, de pequeño a moderado y selectivo:
  - F0: SMD 0,39 (n = 67, metaanálisis de Pinho 2018).
  - Jitter: SMD 0,23 (n = 35).
  - Intensidad global: SMD 0,09, no significativo.
  - Sousa 2025 (n = 51, dosis supramáxima): sdF0 en lectura ES 0,47, pendiente de intensidad en vocal ES 0,49, media LTAS en lectura ES 0,35. Un modelo de 7 marcadores distingue OFF→ON de ON→OFF con AUC 0,86 (LOOCV).
- Las discinesias en ON suben el shimmer (dB) y alteran la velocidad de habla.
- DBS: heterogénea; a largo plazo empeora la fonación y la articulación.
- Sin datos: ningún estudio cuantifica curvas horarias ni el efecto wearing-off por rasgo con grabaciones en casa o con móvil. mPower etiquetó antes/después de la medicación (65 022 tareas) pero nunca se ha analizado en ese sentido. No hay SEM ni MDC publicados para voz con smartphone.
- Ruido de sesión a sesión en móvil: ICC del habla en WATCH-PD de 0,6-0,7. F0 es estable en móvil; HNR y shimmer son poco fiables.
- Progresión anual: PASADENA (n = 94 de placebo, censurados al empezar levodopa) VAI p < 0,01 y VSA p < 0,05, sin d publicada; WATCH-PD solo «cambios modestos» en habla; Rusz 2021 progresión «leve» (p = 0,03).
- Conclusión: el efecto ON/OFF y el ruido entre sesiones igualan o superan un año de progresión, así que mezclar sesiones ON y OFF borra la tendencia.
- Protocolo para la app:
  - Grabar en una ventana fija respecto a la dosis (o en un OFF práctico).
  - Registrar la hora de la última toma, el tipo de fármaco, el estado percibido (OFF, transición, ON, otro), las discinesias, el estado de la DBS y los resfriados.
  - Estratificar las sesiones OFF y ON en vez de mezclarlas o descartarlas.
  - Preferir rasgos robustos en móvil (F0, rango tonal, VAI) frente a HNR y shimmer.
  - Agregar varios días antes de inferir progresión.
