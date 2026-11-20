# Investigación (ChatGPT, 2026-11-20): DA-DSQA y HuBERT/wav2vec2 + SupCon

## DA-DSQA (huggingface.co/jaesungbae/da-dsqa, paper arXiv 2603.15988, licencia MIT)
- Arquitectura: encoder Whisper-large-v3 congelado (`last_hidden_state`, 1280-d) → LayerNorm → MLP 2 capas (proj_dim=320) → statistics pooling (media+std) → Linear → score.
- Salida: `severity_score` 1–7 (1 = típico, 7 = disartria máxima), `raw_score`, `model_name`. NO es estadio de Parkinson.
- Checkpoint por defecto: `proposed_L_coarse_tau100.0` (9 en total: L_coarse tau 0.1/1/10/50/100, L_cont, L_dis, Rank-N-Contrast, SimCLR).
- Entrada: WAV o bytes; mono (media de canales); remuestrea a 16 kHz; Silero VAD (umbral 0.5, habla mín 250 ms, padding 30 ms) y concatena el habla; sin idioma ni transcripción; sin troceo de audios largos.
- Entrenado en inglés (SAP, LibriSpeech); NeuroVoz es uno de sus 5 sets de evaluación externa → posible contaminación al evaluar en NeuroVoz.
- Silero VAD se descarga vía torch.hub en la primera carga (requiere Internet).
- Uso:
  ```python
  import sys
  from huggingface_hub import snapshot_download
  model_dir = snapshot_download("jaesungbae/da-dsqa")
  sys.path.insert(0, model_dir)
  from pipeline import PreTrainedPipeline
  pipe = PreTrainedPipeline(model_dir)
  pipe("audio.wav")  # {"severity_score":..., "raw_score":..., "model_name":...}
  ```
- Dependencias: torch torchaudio transformers soundfile safetensors huggingface_hub.

## Malekroodi et al. 2025, Bioengineering 12(7):728 (PMC12292552)
- Modelos: `facebook/wav2vec2-base`, `facebook/hubert-base-ls960`, `facebook/wav2vec2-base-10k-voxpopuli-ft-en`. 12 capas, 768-d.
- Mejor capa (ablación, Tabla S4): capa 12.
- Comparan sin fine-tuning vs fine-tuning completo. En SupCon: rama de proyección actualiza el encoder; la rama de clasificación (CE) tiene stop-gradient hacia el encoder.
- SupCon con τ=0.07 (mejor de 0.03/0.07/0.10), hard-negative scaling 1.5.
- Entrenamiento: AdamW (β 0.9/0.999, wd 0.01), lr 2e-5, batch 32, máx 100 épocas, dropout 0.2, scheduler no especificado, early stopping por validación.
- Preprocesado: 16 kHz, recorte de silencios inicio/fin, duración fija 5 s (pad/crop), aumento con filtro paso bajo solo en train (corte no especificado).
- Datos: 112 hablantes (54 PD/58 HC), 1695 grabaciones de 16 frases; 80/20 test por hablante + 5-fold CV por hablante dentro del 80 %.
- Mejor resultado: wav2vec2 + SupCon F1 90 %. Frases mejores: PERRO, ACAMPADA, ABLANDADA; peores: CALLE, MANGA, VINO.
- Nota: recortan silencios inicio/fin pero no controlan el confusor de canal.
