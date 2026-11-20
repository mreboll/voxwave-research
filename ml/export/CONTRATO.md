# Contrato de salida del modelo VoxWave (para la demo vox-wave-demo)

Dos formas de consumir el modelo: **archivos estáticos** (esta carpeta) o la **API en vivo**.
Todo lo de esta carpeta se regenera con `ml/src/demo_timeline.py` y `ml/src/export_contract.py`.

En el repositorio público solo está `dials_reference.csv` (estadísticas agregadas por grupo). Los
archivos por paciente (`patient_*.csv`) y el timeline simulado (`timeline_90d*`) derivan de grabaciones
de NeuroVoz, cuya licencia no permite redistribuirlas: se generan en local tras descargar el corpus.

## 1. API en vivo (grabar y puntuar en la demo)

Base: `<MODAL_API_URL>`, la URL que imprime `python -m modal deploy src/modal_api.py` (o
`http://localhost:8000` con `uvicorn serve:app --app-dir src`).
CORS abierto para `https://vox-wave-demo.vercel.app` y `http://localhost:5173`.

### `POST /api/score`

- Cuerpo: `multipart/form-data` con el campo `file`, un WAV PCM de 16 bits, mono o estéreo.
- Duración: entre 1 y 60 s. Tamaño máximo: 20 MB.
- Desde el navegador: graba con MediaRecorder (que entrega webm/ogg) y convierte a WAV antes de enviar:

```js
// Decodifica el audio grabado y lo reescribe como WAV PCM de 16 bits, mono, 16 kHz.
async function blobToWav(blob, sampleRate = 16000) {
  const ctx = new OfflineAudioContext(1, 1, sampleRate)
  const decoded = await ctx.decodeAudioData(await blob.arrayBuffer())
  const frames = Math.ceil(decoded.duration * sampleRate)
  const offline = new OfflineAudioContext(1, frames, sampleRate)
  const src = offline.createBufferSource()
  src.buffer = decoded
  src.connect(offline.destination)
  src.start()
  const pcm = (await offline.startRendering()).getChannelData(0)
  const view = new DataView(new ArrayBuffer(44 + pcm.length * 2))
  const text = (o, s) => [...s].forEach((c, i) => view.setUint8(o + i, c.charCodeAt(0)))
  text(0, 'RIFF'); view.setUint32(4, 36 + pcm.length * 2, true); text(8, 'WAVE')
  text(12, 'fmt '); view.setUint32(16, 16, true); view.setUint16(20, 1, true)
  view.setUint16(22, 1, true); view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true); view.setUint16(32, 2, true); view.setUint16(34, 16, true)
  text(36, 'data'); view.setUint32(40, pcm.length * 2, true)
  pcm.forEach((x, i) => view.setInt16(44 + i * 2, Math.max(-1, Math.min(1, x)) * 0x7fff, true))
  return new Blob([view], { type: 'audio/wav' })
}
```

```js
const form = new FormData()
form.append('file', wavBlob, 'grabacion.wav')
const res = await fetch(`${MODAL_API_URL}/api/score`, {
  method: 'POST',
  body: form,
})
const result = await res.json()
```

Respuesta 200:

```json
{
  "index": 38.2,
  "valid": true,
  "issues": [],
  "duration_s": 3.1,
  "snr_db": 41.0,
  "dials": [
    {"id": "F0semitoneFrom27.5Hz_sma3nz_stddevNorm", "name": "Variación de entonación",
     "name_en": "Pitch variation", "z": -0.8, "hc_median_z": 0.06, "pd_median_z": -0.35}
  ],
  "model_version": "voxwave-wavlm-v2",
  "disclaimer": "Prototipo de investigación. No es un diagnóstico."
}
```

| Campo | Significado |
|---|---|
| `index` | Índice vocal 0-100: parecido de la grabación a voces del grupo clínico. **Solo es interpretable comparado con la referencia de la misma persona y el mismo micrófono**; el valor absoluto cambia con el dispositivo. |
| `valid`, `issues` | Control de calidad: grabación corta, saturación o mucho ruido. Si `valid` es `false`, pide repetir. |
| `dials[].z` | Posición del dial en desviaciones respecto a las frases de NeuroVoz. |
| `dials[].hc_median_z`, `pd_median_z` | Marcas de referencia del grupo de control y del grupo clínico, para dibujar el dial. |

Errores: `400` si el audio es ilegible, demasiado corto o demasiado largo; `413` si es demasiado
grande. El cuerpo es `{"detail": "<mensaje en español>"}`.

### `GET /api/timeline`

Devuelve el mismo JSON que `timeline_90d.json` (sección 3).

**Arranque:** la API mantiene un contenedor encendido, así que responde en ~1-2 s. Si se
apaga (`python -m modal app stop voxwave-demo`), la primera llamada tarda ~30 s.

## 2. Archivos por paciente (NeuroVoz, 107 pacientes con frases + pa-ta-ka)

Todas las cifras son **predicciones fuera de fold**: el modelo no vio a ese paciente al entrenarse.

**`patient_scores.csv`**: `patient_id, group, voice_index, updrs, hy`
- `group`: PD o HC.
- `voice_index`: 0-100, modelo principal (WavLM congelado con el canal descontado).
- `updrs`, `hy`: escalas clínicas; vacías en HC.

**`patient_dials.csv`**: `patient_id, group` y una columna por dial, con el valor z medio del paciente.

**`dials_reference.csv`**: una fila por dial.

| Columna | Significado |
|---|---|
| `name_es`, `name_en` | Nombre visible |
| `hc_median_z`, `pd_median_z` | Medianas por grupo (para pintar la referencia) |
| `d_pd_vs_hc_age_sex_adjusted` | Diferencia PD-HC en DE, ajustada por edad y sexo |
| `rho_updrs_partial` | Correlación con UPDRS controlando edad y sexo (débil en todos los diales: |rho| ≤ 0,27) |
| `mdc95_between_person_sd` | Cambio mínimo detectable de una sesión. Un cambio menor es ruido. |
| `tracking_weight` | Peso en la deriva de diales según su estabilidad entre sesiones: 1,0 F0 y rango tonal, 0,7 ritmo y pausas, 0,3 HNR. |

Los 6 diales:

| Dial | Qué significa más alto |
|---|---|
| Pitch variation / Variación de entonación | Más entonación. Más bajo = voz monótona, típico de la disartria hipocinética. |
| Syllable rate / Ritmo silábico | Más sílabas por segundo. |
| Voiced segment length / Duración de tramos sonoros | Tramos sonoros más largos, con menos cortes. |
| Voice clarity (HNR) / Claridad | Menos ruido en la voz. Sensible al micrófono: usar como contexto. |
| Pause length / Duración de pausas | Pausas más largas. En NeuroVoz, el grupo clínico tiene pausas más cortas. |
| Pitch range / Rango tonal | Más recorrido de tono. Más bajo = voz más plana. Es el rasgo que WATCH-PD encontró alterado incluso con habla «normal». |

## 3. Seguimiento de 90 días (SIMULADO)

Construido con grabaciones reales de dos pacientes de NeuroVoz: PD_0028 (UPDRS 10) se desliza hacia
PD_0079 (UPDRS 43). **En pantalla debe indicarse que es simulado.**

**`timeline_90d_sessions.csv`**: una fila por sesión diaria.
- `day`, `date`, `time`
- `minutes_since_dose`: minutos desde la última toma de levodopa (pautas a las 08, 13 y 18 h).
- `state`: estado de medicación declarado (`on`, `off`, `transition`, `other`). En la simulación, `off`
  cuando han pasado más de 4 h desde la toma.
- `dyskinesia`: discinesias declaradas en la sesión.
- `wear_off`: la sesión es más de 4 h después de la toma.
- `counts_for_trend`: solo `true` en ON y sin discinesias. El resto se dibuja, pero no cuenta: el efecto
  ON/OFF de la levodopa sobre la voz es del mismo orden que un año de progresión.
- `voice_index` y los 6 diales (z por grabación; en fin de dosis la entonación baja ~0,45 DE).

**`timeline_90d_dial_drift.csv`**: una fila por día válido.
- Cada dial expresado como z robusto frente a la referencia propia, **orientado**: positivo = hacia el
  patrón del grupo clínico.
- `dial_drift`: la media ponderada por `tracking_weight`. Es el «índice de cambio de los parámetros de
  la voz».

**`timeline_90d_weekly.csv`**: `week, start_day, value, z, above_usual_range`. Es la mediana semanal
tras los 14 días de referencia.

**`timeline_90d.json`**: todo lo anterior, más:
- `baseline` (centro y dispersión), `tracking_rule`, `disclaimer`.
- `alert`: `{week, day, message}` o `null`, para el índice.
- `dial_drift`: `{daily, weekly, weights, directions, alert}`. Su `alert` incluye `top_dials`, los dos
  diales que más han cambiado, para decir qué parámetro de la voz se movió.

Regla de aviso (igual para el índice y para la deriva de diales): la mediana semanal ≥ referencia +
1,5 × dispersión durante 3 semanas seguidas, sin pendiente negativa. En el timeline saltan los dos
avisos el día 62; el de los diales señala el rango tonal y la variación de entonación.

## 4. Textos (guía FDA General Wellness, enero de 2026)

Para que la demo no se convierta en producto sanitario, los avisos y las explicaciones no deben nombrar
la enfermedad. Usa «deriva respecto a tu referencia» y «coméntalo con tu neurólogo», y para las
referencias de los diales, «voces de control» y «grupo clínico».
