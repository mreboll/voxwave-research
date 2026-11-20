# Guía: descargar ItalianPVS (validación externa)

Dataset: *Italian Parkinson's Voice and Speech* (Dimauro y Girardi, Universidad de Bari).
DOI 10.21227/aw6b-tg17. Licencia Creative Commons Attribution (permite uso comercial citando a los
autores). Un ZIP de 565 MB con WAV y hojas .xlsx.

## Pasos

1. Abre https://ieee-dataport.org/open-access/italian-parkinsons-voice-and-speech
2. Crea una cuenta IEEE gratuita, o entra con la tuya. No hace falta ser miembro de IEEE.
   - Arriba a la derecha, pulsa «Login» y luego «Create account».
   - Rellena correo y contraseña y confirma el correo.
3. Vuelve a la página del dataset ya con la sesión iniciada. En «Dataset files», pulsa
   **Italian Parkinson's Voice and speech_zip** (565 MB).
4. Descomprime el ZIP en `data_external/italianpvs/` (en la raíz del repositorio).
   - Deja dentro la estructura tal como viene: carpetas de grupos con los .wav y los .xlsx.
5. Ejecuta `ml/src/external_italian.py` (o `modal_external.py --dataset italian` en GPU). El script mapea las tareas (lectura y palabras frente a las frases de NeuroVoz) y
   ejecuto la validación externa con el modelo entrenado en NeuroVoz, sin reentrenar.

## Citas obligatorias (licencia CC BY)

- G. Dimauro, V. Di Nicola, V. Bevilacqua, D. Caivano, F. Girardi, «Assessment of Speech
  Intelligibility in Parkinson's Disease Using a Speech-To-Text System», IEEE Access 5, 22199-22208,
  2017. doi:10.1109/ACCESS.2017.2762475
- G. Dimauro et al., «VoxTester, software for digital evaluation of speech changes in Parkinson
  disease», IEEE MeMeA 2016. doi:10.1109/MeMeA.2016.7533761

## Qué esperar

- El idioma (italiano) y las tareas son distintos, y los grupos se grabaron en otro hospital y con
  otro equipo. Un AUROC alto ahí sería la mejor prueba de que el modelo no aprendió la sala de
  NeuroVoz.
- En la literatura, NeuroVoz → EWA-DB cae de 79,6 % a 51,1 % de exactitud, así que es razonable
  esperar una caída.
