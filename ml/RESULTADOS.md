# VoxWave · resultados de los modelos de voz

Fecha: 2026-11-20. Corpus: NeuroVoz (108 pacientes con metadata: 53 PD, 55 HC; 1.794 grabaciones de
frases + pa-ta-ka). Evaluación por paciente con los 5 folds compartidos de `folds.csv`; las
probabilidades por grabación se promedian por paciente. Intervalos: bootstrap de pacientes, 95 %.
Hiperparámetros fijados de antemano, sin ajustarlos sobre los folds de test.

## 0. Resumen para la presentación

Figuras en `results/figures/` (PNG 16:9, se regeneran con `src/make_figures.py`):

| Figura | Mensaje |
|---|---|
| `1_auroc_controles.png` | La sala y la edad predicen Parkinson en NeuroVoz. Quitando cada una, la voz sigue separando: AUROC 0,91 con el canal descontado y 0,89 emparejado por edad. |
| `2_indice_vs_updrs.png` | El índice vocal sube con la gravedad motora: ρ = 0,61, y 0,49 controlando edad y sexo (p = 0,0008, 46 PD). |
| `3_diales.png` | Los diales que se vigilan: entonación más plana, ritmo más rápido, pausas más cortas. |
| `4_seguimiento_90d.png` | La lógica de seguimiento (simulada): referencia de 14 días, solo sesiones en ON, aviso con deriva sostenida (día 62). Abajo, qué parámetros cambian (rango tonal y entonación). |
| `5_validacion_externa.png` | Sin reentrenar, el modelo reconoce el Parkinson en inglés (Londres, misma sala para todos: 0,79) y en italiano (0,93), y sigue la valoración del habla del neurólogo. |

Cinco frases para contar:
1. **Hemos construido un modelo que detecta cambios en la voz asociados al Parkinson.** WavLM congelado
   con el efecto de la sala descontado: AUROC 0,91 (IC 0,86-0,96) en 107 personas, validado por
   paciente.
2. **Sigue la gravedad, no solo el diagnóstico**: su índice correlaciona con UPDRS más allá de la edad.
3. **Hemos encontrado y corregido un atajo** que la mayoría de trabajos sobre NeuroVoz no controlan:
   el silencio solo ya predice el diagnóstico (0,83). Los modelos con fine-tuning (0,94-0,96) también
   lo aprenden.
4. **La cifra prudente está entre 0,77** (benchmark independiente, mismas personas) **y 0,91**.
   **Fuera de España, sin reentrenar:** 0,79 en inglés (Londres, prueba limpia) y 0,93 en italiano.
   Y al revés: entrenado solo con inglés e italiano, reconoce el Parkinson en las voces españolas
   (0,83) y sigue su UPDRS. La señal se transfiere entre idiomas (sección 12).
5. **El seguimiento es frente a uno mismo**: un cambio de un día no significa nada; avisamos cuando la
   deriva se sostiene 3 semanas (~3 % de falsas alarmas en simulación). La validación longitudinal
   real es el siguiente paso (piloto).

## 1. Lo más importante: hay un confusor de grabación

PD y HC se grabaron en épocas distintas: PD sobre todo de enero a junio de 2016; HC a finales de 2016
y en 2018. Solo nov-dic 2016 tiene ambos grupos (7 PD y 25 HC).

| Modelo (frases + pa-ta-ka) | AUROC | IC 95 % | Emparejado por edad | Nov-dic 2016 | ρ con «solo canal» |
|---|---|---|---|---|---|
| Solo edad + sexo | 0,68 | 0,57-0,78 | 0,48 | 0,93 | 0,16 |
| Solo silencio (eGeMAPS) | 0,83 | 0,74-0,92 | 0,76 | 0,53 | 0,84 |
| Solo canal (ruido de fondo, SNR, espectro del silencio) | 0,78 | 0,69-0,87 | 0,72 | **0,23** | 1 |
| eGeMAPS, todos los rasgos | 0,89 | 0,82-0,95 | 0,82 | 0,87 | 0,77 |
| eGeMAPS, canal descontado | 0,84 | 0,76-0,91 | 0,83 | 0,97 | 0,26 |
| WavLM Base+ congelado (media de capas) | 0,96 | 0,92-0,99 | 0,92 | 0,98 | 0,64 |
| **WavLM, canal descontado (principal)** | **0,91** | 0,86-0,96 | 0,89 | 1,00 | **0,22** |
| WavLM fine-tuned (SupCon, Modal) | 0,96 | 0,93-0,99 | 0,94 | 0,97 | 0,59 |
| HuBERT fine-tuned (SupCon, Modal) | 0,94 | 0,89-0,98 | 0,91 | 0,94 | 0,67 |
| WavLM, solo silencio | 0,85 | 0,75-0,93 | 0,82 | 0,62 | - |

La última columna es la correlación (Spearman, por paciente) entre el score del modelo y el del
modelo que solo ve la sala. Cuanto más alta, más se apoya el modelo en la sala.

**Ojo con la ventana nov-dic 2016:** quita el efecto sala, pero no el de edad. En esa ventana la edad
sola separa los grupos (0,93), porque los HC grabados entonces eran más jóvenes. Por eso hacen falta
los dos análisis juntos (figura 1): el emparejado por edad quita la edad y la ventana quita la sala.

Lectura:
- **El silencio solo predice PD con AUROC 0,83-0,85.** Una parte grande de la señal es la sala y el
  equipo, como advertía el paper de septiembre de 2026.
- **Aun así, hay voz además del canal.** Las pruebas:
  - Dentro de la única ventana con ambos grupos, el canal ya no separa (0,23).
  - Los modelos de voz siguen separando en esa ventana (0,87-1,00). Con 7 PD, el IC es ancho:
    eGeMAPS con canal descontado va de 0,88 a 1,00.
  - La voz aporta información por encima del canal (test de razón de verosimilitud, p < 1e-8).
- **La edad no lo explica.** La edad sola da 0,68, y en el subconjunto emparejado por edad (±3 años)
  los modelos de voz mantienen 0,84-0,94.
- **Las vocales sirven poco**, como decía el benchmark de mayo: eGeMAPS en vocales da 0,76, y 0,63
  emparejado por edad.
- **Cifra a citar:** WavLM con canal descontado, AUROC 0,91 (0,86-0,96). El 0,96 sin descontar está
  inflado por el canal.
- **Comparación externa.** El benchmark de mayo de 2026 (arXiv 2605.14066) usa los mismos 108
  hablantes con 5 folds por hablante. Obtiene AUROC 0,77 en frases, 0,75 en pa-ta-ka y 0,53 en /a/.
  - Nuestros 0,89 (eGeMAPS) y 0,96 (WavLM) sin ajustar quedan muy por encima, lo que encaja con un
    resultado inflado por el canal.
  - Con el canal descontado (0,84 y 0,91) seguimos por encima. Posibles causas: modelos y folds
    distintos, y que la regresión lineal sobre descriptores de canal no elimina el canal entero. La
    cifra prudente para el pitch es «entre 0,77 y 0,91».
- **Fine-tuning (receta SupCon del paper de 2025, 5 folds en GPU de Modal):** WavLM llega a 0,96 y
  HuBERT a 0,94, emparejados por edad 0,94 y 0,91. Su índice también sigue a UPDRS (WavLM: ρ parcial
  0,44, p = 0,003). Pero su score correlaciona 0,59-0,67 con el modelo «solo canal», así que aprenden
  la sala igual que el modelo sin ajustar. El ~0,92 del paper (que no controla el canal) cae en ese
  mismo patrón. **No los usamos como modelo principal.** El siguiente paso sería fine-tuning con el
  canal descontado o adversarial.

### 1b. ¿Sirve limpiar la señal? (aportación propia: nadie lo ha publicado para NeuroVoz)

Cadena aplicada antes de extraer rasgos: filtro paso alto a 60 Hz → desreverberación WPE → reducción
de ruido → normalización de ganancia → VAD. Después repetimos los controles.

| Variante (eGeMAPS + regresión logística) | AUROC | Nov-dic 2016 |
|---|---|---|
| Voz, audio original | 0,89 | 0,86 |
| Voz, audio limpio | 0,90 | 0,91 |
| Silencio, audio original | 0,83 | 0,53 |
| **Mismos instantes de silencio, tras limpiar** | **0,80** | 0,80 |
| Descriptores de canal, audio original | 0,78 | 0,23 |
| Descriptores de canal, audio limpio | 0,84 | 0,72 |
| WavLM, audio original / limpio | 0,96 / 0,95 | 0,98 / 1,00 |

- **La limpieza no elimina el atajo.** El silencio sigue prediciendo el diagnóstico (0,80), como
  observan Jouaiti & Ma (2026) tras reducir el ruido.
- **Incluso crea uno nuevo.** Al normalizar la ganancia, el ruido residual queda escalado por lo
  fuerte que habla cada persona, así que el «silencio» limpio lleva información de la voz (hipofonía)
  y el canal limpio separa grupos dentro de la ventana (0,72).
- **El control del «primer segundo» no sirve en NeuroVoz.** Los archivos empiezan casi sin silencio
  (0,03-0,04 s), así que ese segundo es habla: da 0,87 en el original y 0,94 tras limpiar.
- **Conclusión:** en este corpus, descontar el canal dentro del modelo (ρ con «solo canal» de 0,64 a
  0,22) funciona mejor que limpiar la señal. Lo limpio se queda como diagnóstico, no como solución.

## 2. ¿Sigue el modelo a la gravedad? (dentro de PD)

Correlación de Spearman entre el score del paciente y UPDRS (n = 46) o H-Y (n = 51). La versión
«parcial» controla edad y sexo.

| Score | UPDRS | UPDRS parcial | H-Y |
|---|---|---|---|
| WavLM, canal descontado | 0,61 | **0,49 (p = 0,0008)** | 0,07 (n.s.) |
| WavLM, media de capas | 0,48 | 0,38 (p = 0,011) | n.s. |
| eGeMAPS, canal descontado | 0,38 | 0,29 (p = 0,054) | n.s. |
| eGeMAPS, todos los rasgos | 0,11 (n.s.) | 0,11 (n.s.) | n.s. |
| Ridge eGeMAPS → UPDRS | 0,32 (p = 0,03) | - | - |
| Solo edad | 0,45 | - | - |

- El score de WavLM con canal descontado sigue la gravedad motora más allá de la edad. Es el que usa la
  demo.
- Ningún modelo sigue a H-Y: es una escala de 5 niveles, y 39 de 52 pacientes están en 1-2 (34 en el
  estadio 2).
- Con 46 PD, |rho| < 0,3 no se distingue del azar. Hay que tomarlo como señal, no como predictor
  clínico.

## 3. Los diales para el seguimiento diario

Criterios fijados de antemano:
- Diferencia PD-HC ajustada por edad y sexo ≥ 0,35 DE.
- Fiabilidad de una sesión de 17 grabaciones ≥ 0,70 (ICC + Spearman-Brown).
- Menos del 30 % de su varianza explicada por el canal.
- Signo coherente con UPDRS.

Pasan 13 de 89 (`results/dials_selected.csv`). Los más interpretables:

| Dial | PD vs HC (DE) | Lectura |
|---|---|---|
| Duración media de tramos sonoros | +0,85 | Tramos sonoros más largos, con menos cortes entre sílabas |
| Duración de pausas y huecos sordos | -0,95 | Pausas más cortas: habla «apresurada» |
| Picos de sonoridad por segundo (ritmo silábico) | +0,77 | Más sílabas por segundo |
| Variación de entonación (F0, DE normalizada) | -0,46 | Voz más monótona, signo clásico de disartria hipocinética |
| Pendiente de caída de F0 | -0,69 | Menos movimiento de entonación |

Avisos:
- **Ningún rasgo aislado sobrevive a la corrección FDR frente a UPDRS.** Los diales describen la
  diferencia PD/HC; la gravedad la sigue mejor el score multivariante.
- **Los PD de NeuroVoz hablan más rápido.** Las frases miden 2,36 s frente a 2,75 s, contando solo el
  tramo con voz. Es compatible con la aceleración del habla en Parkinson, pero también con la
  diferencia de edad: hay que confirmarlo con otro corpus.
- **La fiabilidad es dentro de una sola sesión.** No mide estabilidad día a día porque NeuroVoz no
  tiene repeticiones.
- **Cambio mínimo detectable (MDC95) de una sesión, en DE entre personas.** Los diales de ritmo y
  pausas dan 0,9-1,3; la entonación (0,60) y HNR (0,32) son más precisos.
  - En ritmo y pausas, un cambio entre dos sesiones tendría que superar toda la diferencia media entre
    PD y HC (~0,8-0,95 DE) para no confundirse con ruido.
  - Y es una cota optimista: en mPower, el ICC test-retest entre días fue de solo 0,26-0,33.
  - Conclusión práctica: los diales no se interpretan día a día, solo agregados durante semanas. La app
    los muestra como contexto, y la alerta se basa en el índice.

## 4. Seguimiento longitudinal (UCI Parkinson's Telemonitoring)

42 pacientes y unas 24 sesiones semanales en 6 meses. Son vocales sostenidas y el UPDRS está
interpolado entre 3 visitas.

- Ninguna variable sigue al UPDRS dentro de cada persona (|r| ≤ 0,08).
- Un score de deriva entrenado dejando fuera a cada sujeto no anticipa el cambio a 6 meses
  (rho = -0,23, n.s.).
- Con la regla de la app, la alerta salta en el 12 % de quienes empeoraron ≥ 3 puntos y en el 24 % de
  los estables. Con el nulo por desplazamiento circular, salta el 7,5 %.

**Conclusión:** con vocales sostenidas no se puede vigilar la progresión. Refuerza usar frases +
pa-ta-ka. Pero no hay ningún dataset público que valide el seguimiento con frases: es la primera cosa
que debería medir un piloto.

## 5. Regla de alerta (calibrada por simulación)

- **Referencia personal:** los primeros 14 días, con al menos 8 días válidos.
- **Valor del día:** la mediana de las grabaciones válidas del día. Las tomas hechas más de 4 h después
  de la última dosis se excluyen.
- **Alerta:** la mediana semanal está ≥ 1,5 DE por encima de la referencia durante 3 semanas seguidas,
  sin pendiente negativa.

Simulación de 90 días con ruido autocorrelacionado y 80 % de adherencia:
- Sin deriva real, la falsa alarma es ~2-3 %.
- Una deriva lenta de +1,5 DE en 90 días se detecta en ~29 % de los casos, en mediana a la semana 7.

Es una regla conservadora a propósito: pocas falsas alarmas.

**Comparación con la recomendación de la literatura** (mediana + MAD sobre una línea base de 14 días,
alerta si |z| ≥ 3 en varias sesiones; no hay un umbral validado clínicamente):
- Usamos la misma base: 14 días, mediana y MAD.
- La diferencia es que agregamos por semanas antes de comparar. Con varias sesiones por semana, la
  mediana semanal ya promedia el ruido de cada día, así que z ≥ 1,5 semanal durante 3 semanas es
  aproximadamente igual de exigente que |z| ≥ 3 por sesión, pero detecta antes.
**Estado de medicación (investigación sobre levodopa):**
- El efecto agudo ON/OFF es pequeño-moderado (SMD de F0 0,39, de la variación de F0 en lectura 0,47 y
  de la pendiente de intensidad 0,49). Es del mismo orden que la progresión anual descrita en PASADENA,
  WATCH-PD y Rusz, y mezclar sesiones ON y OFF borra la tendencia.
- Por eso `tracking.py` registra en cada sesión la hora desde la última toma, el estado declarado (ON,
  OFF, transición, otro) y las discinesias. **La referencia y la tendencia se calculan solo con
  sesiones en ON y sin discinesias.**
- Nadie publica curvas de fin de dosis por rasgo con grabaciones en casa. El umbral de 4 h es una
  convención nuestra; el piloto debería medirlo.

**Deriva de los parámetros de la voz (no solo del índice):**
- Cada dial se compara con la referencia propia (z robusto), orientado hacia el patrón del grupo
  clínico y ponderado por su estabilidad entre sesiones: F0 y rango tonal 1,0; ritmo y pausas 0,7; HNR
  0,3 (HNR y shimmer son poco estables y dependen del micrófono).
- La media ponderada pasa por la misma regla de aviso, y el aviso nombra los dos diales que más han
  cambiado. En el timeline simulado salta el día 62, liderado por el rango tonal y la variación de
  entonación (figura 4, panel inferior).
- El rango tonal se añadió como sexto dial por la evidencia de WATCH-PD, aunque en las frases cortas
  de NeuroVoz separa poco los grupos (d = −0,26).

Pendiente para un piloto real: línea base por tarea (frases y pa-ta-ka por separado; hoy se agregan) y
medir de verdad la variabilidad intra-persona por rasgo. No hay ningún dato publicado de SD, ICC o MDC
por rasgo con móvil en casa; la referencia más cercana es WATCH-PD, con ~80 % de rasgos con ICC
test-retest ≥ 0,6.

## 6. Conexión con la demo del equipo

- **Contrato de salida: [`export/CONTRATO.md`](export/CONTRATO.md).** La demo web (vox-wave-demo) la
  desarrolla otro miembro del equipo en su propio repositorio; este repositorio solo aporta el modelo.
  - Archivos: score por paciente, diales por paciente con su referencia, y la serie de 90 días (índice
    + 6 diales + dosis + aviso). Los que derivan de pacientes de NeuroVoz no se publican: se regeneran
    con `demo_timeline.py` y `export_contract.py`.
  - API (`src/serve.py`, desplegable con `src/modal_api.py`): `POST /api/score` recibe un WAV y
    devuelve el índice, los 6 diales (con nombre en español e inglés) y el control de calidad.
- `timeline_90d.json` es un **timeline SIMULADO**. Mezcla grabaciones reales de PD_0028
  (UPDRS 10) y PD_0079 (UPDRS 43), con dosis a las 08, 13 y 18 h y efecto de fin de dosis. La alerta
  salta el día 62.
- **Ojo:** el índice absoluto en un micrófono nuevo no es comparable con NeuroVoz. Por eso el
  seguimiento compara siempre con la referencia personal grabada con el mismo dispositivo.

## 7. CSV para el equipo (`results/scores/`, formato `patient_id, score`)

Todos son predicciones fuera de fold con `folds.csv`. No se publican (derivan de NeuroVoz); se generan
al ejecutar los scripts:

| Archivo | Uso |
|---|---|
| `ssl_wavlm-base-plus_layer_avg_channel_resid.csv` | **Modelo principal** (WavLM, canal descontado) |
| `confound_egemaps_all_resid.csv` | Baseline clásica honesta (eGeMAPS, canal descontado) |
| `egemaps_speech_sentences_pataka_logreg.csv` | Baseline del ángulo 1 tal como pedía el plan (sin ajuste de canal) |
| `finetuned_wavlm-base-plus.csv`, `finetuned_hubert-base-ls960.csv` | Fine-tuning SupCon (Modal); dependen de la sala |
| `hygiene_*.csv` | Variantes con el audio limpio (sección 1b) |
| `confound_channel_only.csv`, `*silence*.csv` | Controles: lo que predice la sala sola |
| `dadsqa_sentences.csv`, `dadsqa_pataka.csv` | Ángulo 3, DA-DSQA sin reentrenar (sección 9); escala 1-7 |

## 8. Limitaciones y siguientes pasos

1. NeuroVoz es transversal: todo lo anterior es asociación con la gravedad, no seguimiento real.
2. **El confusor de canal limita cualquier cifra.** Para un número limpio hace falta validación externa:
   - **ItalianPVS** (italiano; 28 PD + 37 controles). Licencia CC BY 4.0 (permite uso comercial),
     descarga abierta en IEEE DataPort, con UPDRS-III y H-Y (hay discrepancias entre fuentes). Es el
     candidato inmediato. Ojo: cambia el idioma y las tareas.
   - **PC-GITA** (español colombiano, con UPDRS y H-Y completos) y **EWA-DB** (eslovaco, solo H-Y I-II):
     acceso por solicitud, sin plazo publicado.
   - Como referencia: en la literatura, entrenar en NeuroVoz y probar en EWA-DB baja la exactitud de
     79,6 % a 51,1 %.
3. **Fine-tuning de WavLM/HuBERT**: hecho en Modal (sección 1); depende de la sala. Siguiente paso:
   fine-tuning con el canal descontado.
   - **Licencia:** NeuroVoz es CC BY-NC-ND 4.0. Los audios se subieron a un volumen privado de Modal
     (`voxwave-neurovoz`) con autorización del equipo y solo para este entrenamiento; se borraron al
     terminar.
   - **Ningún modelo entrenado con NeuroVoz puede usarse comercialmente.** El producto necesitará datos
     propios de un piloto o corpus con licencia abierta (ItalianPVS).
4. **Regulación** (FDA General Wellness, enero de 2026): una app de consumo puede mostrar tendencias y
   la referencia personal, pero sus avisos no pueden nombrar una enfermedad. La demo ya lo cumple: el
   aviso habla de «deriva respecto a tu referencia» y los diales comparan con «voces de control» y
   «grupo clínico».
   - Monitorizar el Parkinson explícitamente sería producto sanitario: De Novo en EE. UU., probablemente
     Clase IIa en la UE.
   - En ensayos clínicos puede usarse como tecnología digital investigacional, sin autorización previa.
5. **DA-DSQA** (ángulo 3): ver la sección 9.
6. **Piloto:** grabaciones diarias reales con hora de dosis para medir la variabilidad intra-persona,
   que es el número que calibra la alerta.

## 9. DA-DSQA (ángulo 3, sin reentrenar)

Score de gravedad de disartria de 1 a 7 (Whisper large-v3 + sonda, entrenado en inglés). NeuroVoz fue
uno de sus conjuntos de evaluación externa, no de entrenamiento. En su paper, la correlación con H-Y
es de 0,62, sobre PD + HC y sin controlar el canal.

Lo aplicamos sin reentrenar, con una ventana de Whisper por paciente y tarea (sus frases concatenadas
hasta 28 s, y su pa-ta-ka), y sin el VAD Silero del original. Reimplementamos la sonda y cargamos solo
los pesos; no ejecutamos código del repositorio.

| | Frases | Pa-ta-ka |
|---|---|---|
| AUROC PD vs HC (IC 95 %) | **0,83** (0,75-0,90) | 0,54 (0,41-0,65) |
| AUROC emparejado por edad | 0,71 | 0,58 |
| Mediana del score HC / PD (escala 1-7) | 1,88 / 2,16 | 4,17 / 4,19 |
| ρ con UPDRS (PD) / parcial por edad y sexo | 0,31 / 0,08 (n.s.) | 0,34 / **0,33 (p = 0,037)** |
| ρ con H-Y (PD) / parcial por edad y sexo | 0,32 / −0,02 (n.s.) | 0,00 / −0,06 |
| ρ con el modelo «solo canal» | 0,34 | −0,03 |
| ρ con nuestro modelo principal | 0,57 | 0,13 |

- **Sin haber visto NeuroVoz al entrenarse, separa los grupos con las frases (0,83).** Es una
  verificación independiente: otro modelo, entrenado con habla inglesa, apunta en la misma dirección
  que el nuestro (ρ = 0,57) y depende menos de la sala.
- **Su relación con la gravedad en frases es la edad.** La correlación con H-Y (0,32; su paper da 0,62
  sobre PD + HC) desaparece al controlar por edad y sexo.
- **Pa-ta-ka queda fuera de su dominio:** puntúa ~4,2 a todos y no separa grupos. Aun así sigue a UPDRS
  más allá de la edad (ρ parcial 0,33), una señal que merece mirarse con más datos.
- **Conclusión:** útil como segunda opinión y control externo. No supera al modelo principal, que
  sigue a UPDRS más allá de la edad con ρ = 0,49.

## 10. Mejoras probadas (todas con el canal descontado, los mismos folds y los mismos controles)

Script: `src/improve_models.py`. Los modelos grandes se extrajeron en GPU de Modal (`src/modal_embed.py`).

| Variante | AUROC | Emparejado por edad | ρ parcial UPDRS | ρ con «solo canal» |
|---|---|---|---|---|
| WavLM Base+ (principal) | 0,91 | 0,89 | **0,49** | 0,22 |
| **WavLM Large** | **0,95** | **0,94** | 0,41 | 0,25 |
| Whisper large-v3 (encoder) | 0,93 | 0,92 | 0,31 | 0,19 |
| Fusión WavLM + eGeMAPS | 0,91 | 0,90 | 0,44 | 0,23 |
| Objetivo ordinal de gravedad (HC < PD leve < PD grave) | 0,92 | 0,89 | 0,44 | 0,21 |
| Regresión de UPDRS solo en PD | – | – | 0,13 | 0,11 |
| Fine-tuning WavLM con el canal descontado | 0,67 | 0,70 | 0,27 | −0,19 |

- **Un modelo preentrenado más grande sí ayuda.** WavLM Large sube a 0,95 (0,94 emparejado por edad)
  sin depender más de la sala (ρ 0,25 frente a 0,22). A diferencia del fine-tuning, la mejora no viene
  de la sala.
- **El fine-tuning era casi todo sala.** Al quitarle la parte que explica el canal, cae de 0,96 a 0,67.
- **Seguir la gravedad necesita más datos, no otro modelo.** Con 46 pacientes con UPDRS, entrenar
  directamente para la gravedad (ordinal o regresión) no mejora al clasificador. El que mejor sigue
  UPDRS sigue siendo WavLM Base+ (0,49).
- Se probaron 7 variantes; con tantas comparaciones, diferencias de ±0,02 en AUROC no son
  significativas (los IC se solapan).

**Capas y fusión declaradas de antemano según la literatura** (`src/improve_layers.py`):

| Variante | AUROC | Emparejado por edad | ρ parcial UPDRS | ρ con sala |
|---|---|---|---|---|
| WavLM Large, media de capas | **0,95** | **0,94** | 0,41 | 0,25 |
| WavLM Large, capa 21 | 0,94 | 0,93 | 0,44 | 0,25 |
| Whisper large-v3, media de capas | 0,93 | 0,92 | 0,31 | 0,19 |
| Whisper large-v3, capas 17-20 | 0,91 | 0,91 | 0,33 | 0,12 |
| Whisper large-v3, capa 32 (última) | 0,89 | 0,87 | 0,39 | 0,12 |
| WavLM Base+ + 6 descriptores explícitos | 0,92 | 0,89 | 0,45 | 0,23 |
| WavLM Large capa 21 + 6 descriptores | 0,95 | 0,93 | 0,44 | 0,25 |

Las capas recomendadas en otros corpus (capa 21 de WavLM Large; capas 17-20 de Whisper) no superan a
la media de todas las capas, y añadir los 6 descriptores explícitos (F0, sonoridad, HNR, ritmo) no
aporta. Nos quedamos con la media de capas, decidida de antemano. Las capas intermedias y finales de
Whisper son las que menos dependen de la sala (ρ 0,12).

## 11. Validación externa (sin reentrenar): Londres e Italia

Figura `results/figures/5_validacion_externa.png`. Scripts: `src/external_mdvr.py` y
`src/external_italian.py`; rasgos extraídos en GPU con `src/modal_external.py`. Modelos entrenados solo
con NeuroVoz y aplicados a ventanas de 5 s con al menos un 60 % de habla; score por persona = media.

**MDVR-KCL** (Londres; inglés; móvil Moto G4; misma sala y misma semana para todos; CC BY 4.0)

| Modelo | Lectura (16 PD / 21 HC) | Diálogo (15 PD / 19 HC) | ρ con UPDRS III-18 (habla) dentro de PD |
|---|---|---|---|
| **WavLM, canal descontado (principal)** | **0,79** (0,64-0,92) | **0,74** (0,56-0,90) | **0,53** (p = 0,035) / 0,66 (p = 0,007) |
| WavLM Large, canal descontado | 0,83 (0,69-0,95) | 0,75 | 0,64 (p = 0,008) / 0,71 (p = 0,003) |
| WavLM sin corregir canal | 0,77 | 0,70 | 0,53 / 0,36 (n.s.) |
| eGeMAPS, canal descontado | 0,69 | 0,75 | 0,14 / 0,10 (n.s.) |
| Control: solo sala, entrenado en MDVR | 0,09 | 0,17 | – |
| Techo: WavLM entrenado en MDVR | 0,92 | 0,92 | – |

- **Es la prueba limpia.** Aquí la sala no separa grupos: el control de sala queda por debajo de 0,5,
  que con validación dejando una persona fuera y n pequeño significa «sin señal». El AUROC de 0,79 es
  voz.
- **Sigue la gravedad fuera de NeuroVoz.** El índice correlaciona con la valoración del habla del
  neurólogo (UPDRS III-18) también dentro de los pacientes (ρ = 0,53-0,66).
- **Hay margen al entrenar con datos del propio idioma y equipo:** el techo es 0,92.

**ItalianPVS** (Bari; italiano; 28 PD, 22 controles de la misma edad, 15 jóvenes; CC BY 4.0;
identificadores anónimos; todo remuestreado a 16 kHz)

| Comparación (todas las tareas de habla) | Principal | WavLM Large | WavLM sin corregir | eGeMAPS |
|---|---|---|---|---|
| PD frente a controles de su edad | **0,93** | 0,91 | 0,76 | 0,57 |
| PD a 16 kHz frente a controles de su edad | **0,96** | 0,93 | 0,82 | 0,62 |
| Controles mayores frente a jóvenes (lo ideal es ~0,5 o menos) | **0,34** | 0,25 | **0,99** | 0,69 |

- **El modelo principal no es un detector de «voz mayor».** No separa mayores de jóvenes (0,34). El
  WavLM sin corregir sí lo hace (0,99): había aprendido edad o grabación. Es la mejor prueba de que
  descontar el canal mejora la generalización (0,93 frente a 0,76).
- **Pero en Italia la sala también separa los grupos.** El control de sala entrenado dentro de
  ItalianPVS da 0,90 (0,99 con los PD a 16 kHz). El índice principal aporta claramente por encima de
  la sala en el conjunto completo (p = 3·10⁻⁷; ρ con la sala 0,38), y poco en el subconjunto a 16 kHz
  (p = 0,036; ρ 0,77). Por eso Italia **apoya**, pero no **demuestra**; la prueba limpia es Londres.
- Esta versión de ItalianPVS no trae UPDRS ni H-Y.

**Qué modelo es el principal.** WavLM Base+ con el canal descontado se fijó como principal antes de
estos exámenes y se mantiene. WavLM Large rinde algo mejor en Londres y algo peor en Italia; elegir
ahora el que mejor sale en el examen sería ajustar el modelo al test. Queda como alternativa
documentada.

**Frase para la presentación:** entrenado solo con voces españolas, el modelo reconoce el Parkinson en
inglés (AUROC 0,79, con todos grabados en la misma sala) y en italiano (0,93), y su índice sigue la
valoración del habla del neurólogo.

## 12. Entrenamiento con los tres datasets (NeuroVoz + MDVR-KCL + ItalianPVS)

Script `src/multi_corpus.py`. Mismo modelo (canal descontado, PCA 128, logística) y pesos que dan el
mismo peso a cada dataset y a cada persona. Los jóvenes italianos nunca se usan para entrenar; solo se
puntúan como control de edad.

**Deja-un-dataset-fuera** (el dataset de examen no se ha oído nunca):

| Examen en | Entrenado con | WavLM Base+ | WavLM Large | Gravedad (Base+) |
|---|---|---|---|---|
| Londres | NeuroVoz + Italia | **0,82** (0,67-0,94) | 0,78 | ρ III-18 dentro de PD 0,57 (p = 0,02) |
| Italia, PD frente a mayores | NeuroVoz + Londres | 0,93 (0,84-0,99) | 0,97 | – |
| **NeuroVoz** | **Londres + Italia** | **0,83** (0,75-0,90) | 0,90 | ρ parcial UPDRS **0,43** (p = 0,004) |
| Control: Italia, mayores frente a jóvenes | NeuroVoz + Londres | **0,81** ⚠ | 0,44 | – |

**Validación cruzada conjunta** (5 folds por persona, Base+): NeuroVoz 0,94 (ρ parcial UPDRS 0,49),
Londres 0,95 (ρ III-18 en PD 0,58), Italia 0,93. Control de mayores frente a jóvenes: 0,81 ⚠.

- **La señal se transfiere entre idiomas en las dos direcciones.** Un modelo que no ha oído ninguna
  voz española reconoce el Parkinson en NeuroVoz (0,83) y sigue su UPDRS más allá de la edad. Es la
  prueba más fuerte de que lo aprendido es voz y no la sala de NeuroVoz.
- Más diversidad al entrenar mejora un poco la generalización a Londres (0,79 → 0,82).
- **⚠ Pero aparece un atajo de edad.** Al añadir MDVR-KCL, que no publica la edad de los
  participantes, el modelo separa a los mayores de los jóvenes en Italia (0,81; el modelo solo con
  NeuroVoz daba 0,34). Probablemente sus controles son más jóvenes que sus pacientes.
- **Decisión:** el modelo conjunto se reporta como evidencia de generalización, pero **no se adopta**
  como modelo de la demo mientras no se pueda controlar la edad en todos los datasets. El principal
  sigue siendo WavLM Base+ entrenado en NeuroVoz.
