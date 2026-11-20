Corrige la diapositiva de fórmulas de VoxWave («AI VOICE ANALYSIS / COMPARING WITH HER BASELINE»). Mantén exactamente el mismo diseño: 4 tarjetas en rejilla 2×2 con número (01-04), título corto, dibujo, fórmula y valor grande en naranja; el círculo «AI» en el centro; la línea inferior con el baseline; misma tipografía, colores, márgenes y tamaño. Cambia solo el contenido de las tarjetas y añade una línea pequeña de aviso al pie.

Contexto: el modelo real de VoxWave es una IA (WavLM, red neuronal de voz preentrenada) cuyo índice se calcula después de eliminar el efecto de la sala y el micrófono de cada grabación. Además vigila 6 «diales» interpretables de la voz frente a la referencia personal de 14 días. La diapositiva actual muestra solo medidas acústicas clásicas, incluye dos que no usamos (temblor y tono medio) y presenta números que parecen resultados reales. Tiene que reflejar lo que hacemos de verdad.

Contenido nuevo de las tarjetas (fórmulas en LaTeX):

01 · «Cuánto varía la entonación» (Pitch variation). Dibujo: línea de tono ondulada que se va aplanando.
   \text{Entonación} = \frac{\sigma_{F_0}}{\mu_{F_0}} \quad (F_0 \text{ en semitonos})
   Valor de ejemplo: 0,12

02 · «Recorrido del tono» (Pitch range). Dibujo: puntos de tono con dos líneas horizontales finas en los percentiles 20 y 80.
   \text{Rango} = P_{80}(F_0) - P_{20}(F_0) \quad \text{(semitonos)}
   Valor de ejemplo: 4,9 st

03 · «Regularidad del ritmo silábico» (Rhythm). Mantén el dibujo actual de barras.
   \text{nPVI} = \frac{100}{m-1}\sum_{k=1}^{m-1}\left|\frac{d_k - d_{k+1}}{(d_k + d_{k+1})/2}\right|
   Valor de ejemplo: 48

04 · «Cuánto tiempo es pausa» (Pauses). Mantén el dibujo actual de onda con huecos.
   \text{Pausas} = \frac{1}{T}\int_0^T \mathbf{1}[E(t) < \theta]\,dt
   Valor de ejemplo: 23 %

Círculo central «AI»: añade debajo o a su lado, en pequeño, la fórmula del índice de IA con la sala descontada:
   \text{Índice} = 100\cdot\sigma\!\left(\mathbf{w}^\top \tilde{\mathbf{x}}\right),\quad \tilde{\mathbf{x}} = \mathbf{x} - [1\;\mathbf{c}]\,\hat{B}
   y la etiqueta corta: «IA (WavLM) · sin efecto de la sala».

Línea inferior (se mantiene): «…cada una frente a su propia referencia:»
   z_{k,t} = \frac{x_{k,t} - \tilde{x}_k}{1{,}4826\cdot \mathrm{MAD}_k}
   y añade a continuación, en el mismo estilo: «aviso solo si z ≥ 1,5 durante 3 semanas seguidas».

Pie de diapositiva, pequeño y en gris: «Valores de ejemplo, ilustrativos. Monitorización, no diagnóstico.»

Reglas:
- Elimina la fórmula de temblor (Tremor) y la de tono medio por autocorrelación (Pitch): no forman parte del modelo.
- No inventes otros números ni añadas afirmaciones de precisión.
- Mantén el idioma actual de la diapositiva. Si está en inglés, traduce los títulos: 01 «How much the pitch varies», 02 «Pitch range», 03 «How regular the syllables are», 04 «How much of the time is silence», etiqueta del centro «AI (WavLM) · room effect removed», aviso final «alert only if z ≥ 1.5 for 3 weeks in a row», pie «Illustrative example values. Monitoring, not diagnosis.»
- Comprueba que las fórmulas se renderizan bien y que nada se solapa. Si algo no cabe, reduce la fórmula del círculo central antes que tocar las tarjetas.
