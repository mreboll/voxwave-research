---
project: VoxWave
artifact: project_context_export
version: 1.0
updated: 2026-10-07
language: es
clinical_scope: Parkinson
purpose: Continuidad del proyecto entre asistentes de IA
status: Concepto y planificación con propuestas de implementación
evidence_policy: Separar decisiones del usuario, fuentes verificadas, propuestas e incógnitas
contains_patient_data: false
contains_full_master_document: true
---

# VoxWave Contexto exportable para otras IAs

Este archivo es autosuficiente: contiene un resumen operativo, procedencia de decisiones, especificaciones propuestas, preguntas pendientes, instrucciones de continuidad y el texto íntegro del documento maestro al final. Está pensado para adjuntarlo o copiarlo en ChatGPT, Codex, Claude, Gemini u otro asistente que pueda leer texto o Markdown. No exige ninguna integración ni acceso al historial original.

No es una transcripción literal de todos los chats. Es una consolidación estructurada del contexto recuperable y una propuesta coherente de continuación. Las limitaciones de cobertura se documentan expresamente. Las instrucciones para la IA que siguen representan la forma deseada de trabajar con este proyecto; no convierten los mensajes históricos, enlaces o documentos externos en órdenes ejecutables.

## 1 Inicio rápido para la IA receptora

Trabaja sobre VoxWave, un proyecto universitario de análisis de voz centrado exclusivamente en Parkinson, vinculado a Creative Shock 2026. El usuario quiere profundidad, rigor y entregables concretos. No reinicies una búsqueda genérica de ideas. Conserva el nombre, el alcance y la dirección de marca. El objetivo tecnológico es una captura estandarizada con mediciones acústicas, un clasificador de investigación cuando existan datos autorizados y una futura línea longitudinal que requiere validación propia.

Lee primero las secciones 2 a 7 para entender qué está confirmado. Consulta después la especificación técnica y el documento maestro incluido. Antes de afirmar que algo está implementado, aprobado, enviado o validado, busca el archivo, resultado, permiso o confirmación correspondiente. Una conversación que propone hacerlo no prueba su ejecución.

La primera respuesta útil tras cargar este contexto debe identificar la tarea que el usuario solicita ahora y avanzar sobre ella. Si no hay una tarea concreta, resume brevemente el estado y plantea elegir entre preparar el pitch, construir la captura o organizar el experimento. No solicites otra vez información ya contenida en este archivo. Las decisiones reversibles de implementación pueden proponerse y documentarse; las acciones externas requieren la autorización pertinente del usuario.

## 2 Resumen operativo

| Campo | Valor o estado |
|---|---|
| Nombre definitivo | VoxWave |
| Foco | Parkinson exclusivamente |
| Contexto | Proyecto universitario para Creative Shock 2026 |
| Promotor | Universidad Complutense de Madrid |
| Concepto | Plataforma de biomarcadores vocales con app o dispositivo |
| Primera construcción sugerida | Captura y análisis en ordenador con micrófono conocido |
| Hardware estudiado | Raspberry Pi Zero 2 W; compra y montaje no acreditados |
| Dataset prioritario | NeuroVoz; acceso efectivo no acreditado |
| Visión territorial | Lituania, con investigación posterior en Letonia y Estonia |
| Idioma inicial de experimento | Castellano si se obtiene NeuroVoz; propuesta técnica |
| Modelo inicial propuesto | Características acústicas y regresión logística regularizada |
| Comparación | SVM lineal y modelos sencillos bajo las mismas particiones |
| Seguimiento personal | Hipótesis futura; sin validación longitudinal acreditada |
| Estado clínico | Sin resultados propios, autorización o certificación acreditados |
| Documentación disponible | Maestro y este export, versión 1.0 |
| Logo | Brief textual detallado; archivo final aprobado no recuperado |

## 3 Convenciones de evidencia

Utiliza estas etiquetas al ampliar el proyecto:

- CONFIRMADO_USUARIO: afirmación o decisión explícita del promotor.
- FUENTE_PRIMARIA: información contrastada en documentación oficial, publicación original o briefing aportado.
- HISTORICO_PROPUESTO: sugerencia de un asistente anterior, sin aceptación o ejecución acreditada.
- PROPUESTA_ACTUAL: diseño o recomendación formulada en la consolidación del 7 de octubre de 2026.
- PENDIENTE: dato, permiso, decisión o resultado aún no acreditado.
- ILUSTRATIVO: número o ejemplo utilizado para explicar un mecanismo, sin carácter de resultado.
- SUPERADO: nombre o enfoque de trabajo sustituido por una decisión posterior.

Una fuente científica puede acreditar un resultado en su propio estudio, pero no un rendimiento de VoxWave. Una institución que aparece en una publicación no es automáticamente colaboradora del proyecto. Una propuesta de correo no es un correo enviado. Un resultado publicado sin versión, población y método no se utiliza como objetivo garantizado.

## 4 Decisiones y evolución del concepto

| ID | Decisión o antecedente | Estado | Consecuencia |
|---|---|---|---|
| D01 | Nombre VoxWave | CONFIRMADO_USUARIO | Usarlo en entregables nuevos |
| D02 | Alcance exclusivo Parkinson | CONFIRMADO_USUARIO | Mantener documentación y producto dentro de ese foco |
| D03 | Artefactos extensos y reutilizables | CONFIRMADO_USUARIO | Priorizar contenido completo y archivos descargables |
| D04 | Preferencia por explorar hardware | CONFIRMADO_USUARIO en fase de ideación | Evaluar dispositivo sin asumir compra o selección final |
| D05 | V geométrica y W ondulada con onda continua explícita | CONFIRMADO_USUARIO | Mantener en cualquier trabajo de marca |
| D06 | NeuroVoz como primer corpus | HISTORICO_PROPUESTO, con interés del usuario en solicitarlo | Resolver acceso y versión antes de entrenar |
| D07 | Zero 2 W para análisis local ligero | HISTORICO_PROPUESTO | Probar recursos; no afirmar que ya funciona |
| D08 | Plataforma móvil y expansión báltica | HISTORICO_PROPUESTO | Conservar como visión y someter a validación lingüística |
| D09 | Comparación con referencia personal | HISTORICO_PROPUESTO | Separar de clasificación transversal |
| D10 | Ordenador primero y dispositivo después | PROPUESTA_ACTUAL | Reducir dependencias del MVP |
| D11 | Piloto institucional supervisado | PROPUESTA_ACTUAL | Contrastar comprador y flujo profesional |
| D12 | Captura activa en MVP | PROPUESTA_ACTUAL | Evitar escucha ambiental e integraciones innecesarias |

La secuencia histórica fue una búsqueda de ideas de impacto social, interés en hardware, desarrollo de un concepto de voz, exploración de baseline personal, una versión móvil con visión báltica y análisis detallado de un dispositivo. Aparecieron los nombres de trabajo VoiceGuard, VoicePrint, VocalTwin y VoxTrace. Todos quedan como antecedentes; el nombre vigente es VoxWave.

La versión móvil y la versión con dispositivo no deben interpretarse como dos empresas distintas. Son posibles canales de captura de una misma propuesta. Tampoco existe evidencia de que el promotor haya cancelado la estrategia báltica por considerar una Raspberry Pi. Debe preservarse la tensión de diseño y decidir con pruebas de repetibilidad, accesibilidad y coste.

El usuario expresó frustración en un chat anterior por el tiempo invertido sin recibir archivos. La preferencia de colaboración es entregar trabajo concreto y evitar ampliar indefinidamente la investigación. Esto no justifica omitir límites de evidencia ni presentar una promesa como hecho.

## 5 Cobertura de conversaciones y archivos

Se recuperó la referencia principal y se identificaron otros chats del mismo proyecto mediante el listado de conversaciones. Las páginas recuperadas indicaban que no había más turnos antiguos en esos chats, pero algunos mensajes largos aparecen truncados por el servicio. El texto disponible no equivale a acceso íntegro a todos los archivos históricos.

| ID de fuente | Título literal | Identificador | Cobertura y aportación |
|---|---|---|---|
| C01 | Documento maestro y contexto exportable | [id omitted] | Petición de consolidación y nombre VoxWave |
| C02 | Documento y exportación exhaustivos | [id omitted] | Expectativa de extensión y necesidad de finalizar |
| C03 | VoxWave Logo Design | [id omitted] | Prompt visual y revisiones explícitas del usuario |
| C04 | Centrarse en Parkinson | [id omitted] | Decisión de alcance vigente |
| C05 | Viabilidad Del Dispositivo de Screening | [id omitted] | Pipeline, pruebas, Zero 2 W y hardware; respuesta larga truncada |
| C06 | Explicación de NeuroVoz | [id omitted] | Receptor byo_upm, correspondencia propuesta y afiliación del promotor |
| C07 | Investiga viabilidad de idea | [id omitted] | Visión báltica, acuerdo de datos y contactos; documento largo truncado |
| C08 | Creative Shock Idea Strategy | [id omitted] | Estrategia, baseline y briefing adjunto recuperado |
| C09 | Proyecto en ChatGPT y Codex | [id omitted] | Interés en continuidad entre móvil, ordenador y repositorio; texto parcial |
| C10 | Buscar ideas UE ONU | [id omitted] | Exploración previa de alternativas de impacto; texto parcial |
| C11 | Participar en hackathon | [id omitted] | Origen, interés en hardware y primeros conceptos; algunas respuestas parciales |
| C12 | Abrir proyecto local | [id omitted] | Necesidad de continuidad de trabajo local |
| C13 | Investiga ideas originales y negocio | [id omitted] | Identificado, pero lectura no completada por limitación del servicio |

El briefing de Creative Shock sí se recuperó como PDF y se leyó: página 2 describe la tarea; página 3 reúne plazo y criterios; página 6 repite la entrega. También había tres imágenes adjuntas a ese chat, pero su contenido no se utilizó como evidencia adicional. Las imágenes finales de logotipo no se devolvieron como archivos en el chat de marca; se dispone del brief y las revisiones textuales.

El chat C07 afirma que se creó un dossier anterior de VoxTrace de 27 páginas y ofrece un enlace de un entorno antiguo. Ese PDF no se recuperó como archivo accesible. Su existencia y contenido no se usan como prueba de implementación. El maestro actual conserva la información textual recuperada y corrige el nombre a VoxWave.

El export no incorpora transcripciones irrelevantes de las alternativas de negocio anteriores. Conserva la consecuencia para VoxWave: se buscaba una idea original, social, viable, con hardware potencial y capaz de producir un MVP convincente. Si aparece material adicional, debe integrarse sin reabrir automáticamente esas otras ideas.

## 6 NeuroVoz y permisos

Fuentes S2, S3 y S4 del maestro: artículo original, repositorio de autores y registro de Zenodo. Los recuentos difieren entre versiones; no sobrescribir esa discrepancia. El experimento debe registrar la versión descargada y contar participantes realmente utilizables. No tratar las grabaciones repetidas como participantes adicionales.

El usuario llegó a la pantalla de solicitud de acceso y copió el acuerdo. En C06 identificó el receptor como byo_upm. Hay borradores que dicen «ya hemos solicitado», pero esa frase forma parte de un texto sugerido por el asistente. No hay comprobante inequívoco de solicitud enviada, correo enviado, aprobación ni descarga. Estado operativo: PENDIENTE_DE_CONFIRMACION.

El texto histórico del acuerdo exige no reidentificar, no redistribuir sin autorización escrita y no explotar comercialmente los materiales o derivados sin consentimiento escrito. Requiere atribución al corpus y trabajo científico. La versión aplicable debe conservarse junto a la descarga. No deducir derechos sobre audios a partir de la licencia del código, ni dar por autorizado un uso de concurso por ser universitario.

Contacto recuperado y verificado en directorio UPM: Juan Ignacio Godino Llorente, [email omitted]. Un eventual mensaje debería presentar afiliación real, finalidad académica, protocolo propuesto y preguntas sobre uso, demostración y derivados. El equipo debe confirmar su capacidad de aceptar las condiciones. No enviar mensajes ni rellenar datos personales por inferencia.

En borradores antiguos aparece «Pedro [Apellidos]», mientras que un texto pegado de Zenodo muestra otro nombre. Para evitar propagar un error, este export no fija identidad personal para firmar. Solo conserva la Universidad Complutense de Madrid. Antes de una solicitud externa se confirma el firmante con información explícita.

## 7 Colaboración báltica y fuentes adicionales

Lituania es el territorio inicial propuesto para la visión de producto. NeuroVoz puede facilitar un primer experimento en castellano. Debe hacerse explícita esa diferencia en el pitch: tener un clasificador en castellano no acredita funcionamiento en lituano, letón o estonio.

El artículo lituano de 2017 enlazado en S12 publica un punto de contacto para audios: [email omitted]. Su antigüedad exige confirmar que sigue siendo la vía adecuada. Kaunas University of Technology, Lithuanian University of Health Sciences y Kauno Klinikos son posibles interlocutores de investigación, no socios confirmados.

Para Tartu se identificaron Aleksis Krass y sus supervisores Joonas Järve y Pille Taba. Los correos [email omitted] y [email omitted] provienen de C07 y deben reconfirmarse antes de uso; no se afirman como verificados nuevamente en este export. La tesis original está enlazada en S13. No hay respuesta institucional ni acceso concedido acreditados.

Las opciones de cooperación son acceso bajo acuerdo, características derivadas con permisos o validación externa ejecutada por el propietario de datos. Esta última no requiere necesariamente transferir audios, pero sí un protocolo, resultados predefinidos y protección frente a ajustes sucesivos al conjunto de prueba. El primer contacto debe preguntar por viabilidad, no presuponer un convenio.

PC-GITA y LIEPA-3 aparecieron como recursos potenciales. No se ha validado aquí una descarga ni licencia concreta. El primero es una pista para corpus clínico adicional; el segundo se mencionó como habla general para adaptación lingüística. No confundir preentrenamiento de idioma con etiquetas clínicas, ni añadir una gran descarga al camino crítico del MVP.

## 8 Especificación funcional propuesta

La sesión activa se organiza como una máquina de estados. Inicio y explicación; consentimiento o verificación de permiso; prueba de micrófono; tarea; comprobación de calidad; repetición si procede; siguiente tarea; extracción; resultado o no evaluable; cierre y almacenamiento autorizado. Cancelar debe ser posible y quedar registrado.

El protocolo provisional tiene cuatro tareas: fonación, DDK, frase y habla espontánea. Sus duraciones y ejemplos figuran en el maestro. Deben fijarse un identificador de protocolo y una versión. Si se acorta una tarea o cambia la frase, el sistema no puede seguir afirmando que aplica exactamente el protocolo anterior.

Requisitos funcionales de referencia:

- RF01: registrar solo tras una acción explícita y mostrar cuándo está grabando.
- RF02: conservar metadatos suficientes para reproducir el análisis autorizado.
- RF03: rechazar audio inutilizable con causa comprensible.
- RF04: permitir repetir una tarea sin duplicar indebidamente la sesión.
- RF05: separar estado de calidad, medidas acústicas y salida de modelo.
- RF06: devolver valores ausentes como nulos con motivo, nunca como ceros engañosos.
- RF07: impedir inferencia con versiones o características incompatibles.
- RF08: permitir funcionamiento local de las funciones esenciales si se elige ese despliegue.
- RF09: registrar versiones de micrófono, protocolo, extractor y modelo.
- RF10: presentar resultados experimentales sin convertirlos en consejo clínico autónomo.

Los requisitos no funcionales deben medirse antes de fijar compromisos: latencia, memoria, autonomía, tasa de repetición, facilidad de uso y recuperación de fallos. No hay benchmarks de VoxWave disponibles. La frase «funciona sin Internet» es una meta de arquitectura para la rama local, no una prueba completada.

## 9 Contrato de datos ilustrativo

El siguiente JSON es un ejemplo sintético de diseño, no una sesión real ni una implementación existente. Los identificadores de versiones son etiquetas propuestas. Se usa null para reflejar que no hay modelo ni medidas calculadas.

```json
{
  "schema_version": "proposal-1",
  "project": "VoxWave",
  "session_id": "DEMO-SESSION-001",
  "participant_id": "SYNTHETIC-001",
  "purpose": "research_demo",
  "language": "es",
  "protocol_version": "proposal-voice-4tasks",
  "device": {
    "platform": "desktop",
    "microphone_id": "pending-selection",
    "capture_config_version": "pending"
  },
  "quality": {
    "status": "not_evaluated",
    "reasons": []
  },
  "tasks": [
    {"type": "sustained_vowel", "status": "not_recorded"},
    {"type": "ddk", "status": "not_recorded"},
    {"type": "sentence", "status": "not_recorded"},
    {"type": "spontaneous_speech", "status": "not_recorded"}
  ],
  "extractor_version": null,
  "features": [],
  "model": {
    "version": null,
    "status": "not_available",
    "score": null,
    "calibration_version": null,
    "threshold_version": null
  },
  "personal_baseline": {
    "status": "insufficient_data",
    "valid_sessions": 0
  },
  "clinical_interpretation": null
}
```

En un diseño real, cada característica necesita identificador, valor, unidad, tarea, validez y versión de cálculo. El identificador de consentimiento o autorización puede almacenarse como referencia separada, sin copiar información personal en cada resultado. Las rutas internas de audio no deben incluir nombres o diagnósticos visibles para el algoritmo.

## 10 Organización técnica para continuar

Propuesta de repositorio, todavía no creada como producto en este trabajo:

```text
voxwave/
  README.md
  PROJECT.md
  DECISIONS.md
  docs/
    intended_use.md
    protocol.md
    data_access.md
    feature_dictionary.md
    validation_plan.md
    model_card.md
    risk_register.md
  src/
    capture/
    quality/
    features/
    inference/
    storage/
    interface/
  configs/
  tests/
  reports/
  data/
    README.md
```

La carpeta de datos solo documentaría ubicación y condiciones; audios clínicos, credenciales y datos personales no se subirían al repositorio. Un repositorio privado no convierte la redistribución en autorizada. Las dependencias se fijarán después de comprobar plataforma y licencias. No inventar un enlace de GitHub, rama, commit o carpeta ya existente.

Los chats de continuidad expresan interés en trabajar desde móvil y ordenador. La solución portable propuesta es mantener decisiones y especificaciones en archivos versionados, y transferir este contexto cuando cambie el asistente. No se conserva como hecho ninguna afirmación histórica sobre funciones concretas de aplicaciones; deberán comprobarse si el usuario solicita configurar esas herramientas.

## 11 Experimentos y criterios de aceptación

| ID | Pregunta | Entregable | Criterio mínimo propuesto |
|---|---|---|---|
| E01 | Se puede grabar de forma consistente | Informe de captura repetida | Fallos identificables y configuración reproducible |
| E02 | El extractor produce valores estables | Comparación sobre archivos de referencia | Mismo archivo y versión producen mismo resultado dentro de tolerancia definida |
| E03 | Existe señal clasificadora útil | Evaluación agrupada por participante | Sin fuga y comparación con referencia trivial |
| E04 | El sistema se transfiere al dispositivo | Comparación ordenador y Pi | Equivalencia de salida y recursos medidos |
| E05 | Se transfiere entre idiomas | Informe externo o reservado | Prueba independiente sin reajuste al test |
| E06 | La referencia personal es interpretable | Estudio de sesiones repetidas | Separar variabilidad técnica y personal |
| E07 | El flujo resulta usable | Observación con usuarios objetivo | Medir ayuda, abandonos y comprensión |

No hay umbrales clínicos mínimos aprobados. Deben definirse con el colaborador clínico y según la finalidad. El número de participantes y la precisión de intervalos requieren planificación estadística. Una cifra alta de accuracy en una demo no cierra ninguno de los experimentos posteriores.

La evaluación técnica debe incluir silencio, saturación, poca voz, frecuencia incorrecta, micrófono desconectado, almacenamiento lleno, sesión interrumpida y modelo incompatible. La evaluación de ML debe garantizar separación por persona, transformación dentro de los folds, umbral congelado y un análisis de exclusiones. No optimizar sobre el conjunto final ni seleccionar el mejor resultado de muchas pruebas sin declararlo.

## 12 Hardware y límites de implementación

El candidato es Zero 2 W, no una referencia genérica a cualquier Raspberry Pi Zero. La especificación oficial figura en S5. Antes de compra se revisarán disponibilidad y coste actual; no se ha adquirido ningún componente en esta tarea. Las familias I2S citadas en el maestro son ejemplos históricos, no selección de piezas ni garantía de controladores.

La ruta de bajo riesgo técnico propuesta es ordenador con USB, extracción ligera y modelo clásico, seguida de despliegue en Pi. El audio se guardará sin procesamiento destructivo cuando sea posible. El LED indica estado de operación; no tiene por qué representar una categoría clínica. Una pequeña OLED puede ser insuficiente para instrucciones accesibles.

No ejecutar modelos grandes de voz o lenguaje en la Pi como requisito del MVP. Si una comparación de investigación necesita embeddings, puede hacerse fuera del dispositivo y evaluarse después una alternativa ligera. La latencia de inferencia no representa el tiempo total: captura, extracción, interfaz y escritura pueden dominar la sesión.

## 13 Marca y comunicación

Nombre: VoxWave. Paleta: #092634, #004E72, #FF6E42 y #F9F9F9. Símbolo: combinación de V y W con onda continua reconocible. La V debe ser más recta y geométrica; la W, más ondulada. El promotor pidió continuar la onda y hacerla explícita. Evitar asociaciones anatómicas involuntarias y un símbolo que se confunda con otro tipo de registro médico.

Estilo: plano, limpio, preciso, minimalista, profesional y cercano. No texturas realistas, degradados brillantes ni mockups como sustituto del archivo de marca. Todavía no hay un logotipo final aprobado recuperado. Para continuar el diseño se debe usar el brief, y pedir el original solo si el usuario exige modificar una imagen concreta que no está disponible.

Mensajes recomendados: describir qué se mide, para quién y qué se está investigando. Evitar promesas de detección anterior a síntomas, porcentajes personales sin calibración o mejoras clínicas no demostradas. Los valores de antiguos ejemplos de puntuación, similitud y tendencia eran ilustrativos. No deben reaparecer en una diapositiva como resultados del equipo.

## 14 Negocio y estrategia de impacto

Los antecedentes favorecían un modelo B2B o B2B2C con clínicas, hospitales, sistemas de salud y entidades de investigación. Se discutieron contratos por paciente, licencias de plataforma y uso en ensayos como posibilidad futura. Ninguno está aprobado ni tiene demanda acreditada. Una suscripción de consumo no está formalmente prohibida, pero tampoco es el canal priorizado en esta consolidación.

La propuesta actual es investigar un piloto institucional supervisado y medir quién opera, quién revisa, quién paga y cuánto soporte necesita. Las hipótesis de precio del maestro son ejemplos internos. No sustituirlas por un plan de ingresos presentado como pronóstico. Los costes de datos, licencias y validación pueden pesar más que el hardware.

ODS principal: 3. La contribución potencial a acceso y continuidad se medirá con resultados concretos; ODS 10 y 9 son vínculos secundarios posibles. No afirmar vidas salvadas, diagnósticos adelantados o reducción de costes sin un diseño que permita demostrarlo. Para la primera fase, medir sesiones válidas, ayuda necesaria, comprensión y coste de operación.

## 15 Creative Shock y camino crítico

El briefing aportado exige un vídeo de 3 a 5 minutos, con foco en marketing y finanzas, una idea original relacionada con los ODS y entrega por enlace de Google Drive a través de un formulario. El plazo indicado es el 11 de octubre a las 23:59 EEST, UTC+3; se interpreta como 2026 por el contexto de la edición. La fecha equivale a la misma hora local de Europe/Kiev en ese día. No se ha subido ni enviado el vídeo en esta tarea.

Los seis criterios son problema y necesidad, solución e innovación, impacto y ODS, potencial de construir un MVP con IA, negocio sostenible y calidad narrativa. La rúbrica no implica que el proyecto tenga puntuaciones altas: las estrellas de mensajes anteriores eran opiniones del asistente, no evaluación de la organización.

Prioridad inmediata: comprobar instrucciones recibidas, cerrar relato y roles, grabar una demostración honesta y preparar respaldo. El modelo clínico no debe convertirse en condición para completar un vídeo de concepto. Si se usan pantallas simuladas, hay que identificarlas. Antes de enviar, comprobar duración, audio, legibilidad, acceso al enlace y confirmación de recepción.

## 16 Incógnitas que no deben rellenarse por imaginación

- Composición del equipo, nombres de responsables y dedicación disponible.
- Estado real de inscripción y recepción de cualquier actualización del concurso.
- Solicitud enviada de NeuroVoz, permiso aprobado, versión descargada y condiciones aceptadas.
- Respuestas de UPM, Kaunas o Tartu y capacidad del equipo para firmar acuerdos.
- Existencia de repositorio, código, modelo, métricas o prototipo físico fuera de este trabajo.
- Micrófono, sistema operativo, piezas, presupuesto y disponibilidad de compra.
- Primera finalidad clínica y entorno exacto del futuro piloto.
- Datos longitudinales y referencia clínica para seguimiento.
- Precio, voluntad de pago, costes verificables, financiación y mercado alcanzable.
- Licencias de software y datos para cualquier desarrollo comercial.
- Archivo final de logo, tipografía elegida, dominio y disponibilidad de marca.

Estas incógnitas no obligan a preguntar por todo antes de trabajar. La siguiente tarea debe resolver únicamente las que bloquean su resultado y avanzar en lo demás con supuestos explícitos.

## 17 Prompt reutilizable de continuidad

Puedes copiar este bloque al iniciar otra conversación:

```text
Estoy continuando VoxWave. Lee el export de contexto adjunto completo y úsalo como referencia del proyecto. Mantén el nombre VoxWave y el enfoque exclusivo en Parkinson. Conserva la estrategia de voz, la visión báltica, NeuroVoz como corpus prioritario pendiente de permisos y la opción de Raspberry Pi Zero 2 W sin tratarla como hardware ya validado.

Distingue decisiones confirmadas, hechos de fuentes primarias, propuestas, ejemplos e incógnitas. No inventes datos, métricas, acuerdos, permisos, código existente ni envíos realizados. No conviertas el análisis vocal en un diagnóstico autónomo. Separa cribado transversal y seguimiento personal. Si programas ML, divide por participante y ajusta transformaciones dentro del entrenamiento.

Quiero entregables concretos y completos, sin prolongar innecesariamente la investigación. Reutiliza lo ya documentado. Si falta un dato imprescindible, señala exactamente cuál y avanza en las partes independientes. Actualiza decisiones y estado al terminar.

La tarea que quiero hacer ahora es: [ESCRIBIR LA TAREA].
```

## 18 Instrucciones específicas por tipo de trabajo

Para investigación: prioriza publicaciones originales y documentos oficiales. Registra fecha, población, tarea, dispositivo y método de evaluación. Explica si el resultado procede de un corpus transversal o longitudinal. No conviertas una revisión narrativa en evidencia de rendimiento de VoxWave.

Para ingeniería: inspecciona el repositorio real antes de asumir estructura. Implementa un flujo mínimo comprobable y documenta errores. Mantén audios y credenciales fuera de repositorios y servicios sin permiso. Explica pruebas realizadas y qué sigue sin verificarse. No entrenes con datos inaccesibles ni generes métricas ficticias para completar una pantalla.

Para negocio: comienza por comprador y trabajo actual. Distingue entrevista, interés, piloto y contrato. Construye escenarios con supuestos y sensibilidad. No uses la población mundial como mercado inmediatamente alcanzable. Incluye mantenimiento y coste de revisión del resultado.

Para diseño y pitch: aplica el brief de marca y los requisitos del concurso. Muestra un recorrido, una prueba y una decisión. Etiqueta simulaciones. No rehagas el nombre ni amplíes el alcance. Utiliza imágenes reales del prototipo solo si existen y han sido facilitadas.

Para documentación: mantén IDs de decisiones y fuentes. Si una afirmación cambia, conserva qué evidencia provocó el cambio. Una instrucción actual del promotor prevalece sobre propuestas históricas, pero no transforma afirmaciones científicas en hechos verificados.

## 19 Registro para la próxima actualización

Después de cada avance, añadir una entrada con fecha, tarea, archivos creados o modificados, evidencia, decisiones, riesgos y siguiente paso. Marcar un hito como completado solo cuando su entregable exista. Si no se pudo probar una función, escribir «no verificado» y describir qué prueba falta.

```json
{
  "date": "YYYY-MM-DD",
  "task": "Descripción de la tarea realizada",
  "artifacts": [],
  "confirmed_decisions": [],
  "proposals": [],
  "evidence": [],
  "tests": [],
  "open_questions": [],
  "next_action": "Siguiente acción concreta"
}
```

Estado al exportar: documentación creada; proyecto de producto sin implementación ni resultados propios acreditados en este encargo. El trabajo realizado fue consolidar contexto, contrastar fuentes y producir los dos artefactos. Durante esta tarea no se realizó ninguna solicitud de datos, envío de correos, compra de componentes ni presentación del proyecto al concurso.

## 20 Documento maestro íntegro

La siguiente parte reproduce el contenido completo del documento maestro. Es parte deliberada del export para que una IA no dependa de abrir el PDF. Las referencias S1 a S15 se resuelven en su bibliografía. Las propuestas del maestro mantienen el estado indicado arriba y no deben tratarse como acuerdos del equipo.

<!-- INICIO DEL DOCUMENTO MAESTRO -->

# VoxWave
## Documento maestro del proyecto

Proyecto de análisis de voz para investigación en cribado y seguimiento del Parkinson. Versión 1.0. Fecha de referencia: 7 de octubre de 2026. Destinatarios: equipo promotor, colaboradores técnicos, profesionales clínicos, mentores y jurado de Creative Shock.

VoxWave propone convertir una breve serie de tareas vocales en mediciones acústicas reproducibles que puedan estudiarse como apoyo al cribado del Parkinson y, en una fase posterior, al seguimiento de cambios de la voz. El primer objetivo es construir una demostración transparente y un experimento reproducible. Su utilidad clínica tendrá que demostrarse con participantes independientes, una población de uso definida y evaluación prospectiva.

El nombre VoxWave, el enfoque exclusivo en Parkinson y la dirección visual del logotipo son decisiones del promotor. La arquitectura, el protocolo abreviado, los presupuestos y la secuencia de desarrollo de este documento son propuestas de trabajo, salvo indicación expresa. Ningún valor ilustrativo representa un resultado obtenido por VoxWave. La disponibilidad de un modelo entrenado, un dispositivo montado, acceso al corpus o un acuerdo clínico debe acreditarse mediante sus respectivos entregables.

## Guía de lectura

Las secciones 1 a 5 definen el proyecto y su uso. Las secciones 6 a 15 desarrollan datos, ingeniería y validación. Las secciones 16 a 23 cubren operación, negocio, impacto, Creative Shock y marca. Las secciones 24 a 29 convierten la estrategia en decisiones, tareas, criterios de aceptación y fuentes. El export de contexto complementario conserva la procedencia, los estados de decisión y las instrucciones para continuar el trabajo con otras IAs.

## 1 Resumen ejecutivo y decisión estratégica

La hipótesis principal es que una captura estandarizada de voz, acompañada de control de calidad y análisis acústico, puede aportar información útil sobre patrones asociados al Parkinson. La propuesta no se reduce a clasificar un archivo: incluye instrucciones comprensibles, una grabación técnicamente válida, un resultado interpretado dentro de sus límites y una vía de revisión profesional.

La oportunidad inicial está en resolver una tarea delimitada con pocos recursos. Se recomienda empezar por un prototipo de investigación supervisado, en castellano y con un protocolo fijo. El software debe funcionar primero en un ordenador con un micrófono conocido. La Raspberry Pi Zero 2 W será una segunda plataforma de ejecución, condicionada a pruebas de compatibilidad, memoria, latencia y estabilidad. El hardware dedicado solo aporta valor si mejora la repetibilidad, la accesibilidad o la operación frente a un móvil o un ordenador.

El proyecto contempla dos preguntas diferentes. El cribado compara patrones vocales con un modelo poblacional y estudia si ayudan a priorizar una evaluación. El seguimiento compara sesiones de una misma persona y estudia cambios respecto a su referencia. Un conjunto transversal de casos y controles puede servir para explorar la primera pregunta; no demuestra automáticamente la segunda. Tampoco demuestra detección antes de los síntomas o utilidad en población general.

La recomendación para Creative Shock es presentar una solución social concreta, un prototipo visible y una ruta de validación económicamente creíble. Una demostración honesta de captura, control de calidad y extracción de características tiene valor incluso si el acceso a datos todavía no permite entrenar un clasificador. La promesa comercial debe crecer al mismo ritmo que la evidencia.

## 2 Problema y oportunidad en Parkinson

El Parkinson puede afectar al movimiento y al habla. La OMS lo considera un problema creciente de salud pública y señala dificultades de acceso a la atención; su ficha de 2023 sitúa en más de 8,5 millones las personas afectadas en 2019. Esa cifra histórica sirve para contextualizar el problema, no para estimar directamente el mercado de 2026. [S1]

Para VoxWave, el problema operativo que merece investigarse es la falta de mediciones vocales breves, consistentes y fáciles de revisar entre encuentros presenciales o en entornos con recursos limitados. Es necesario comprobarlo mediante entrevistas: cuánto tiempo consume la evaluación actual, qué información falta, quién interpreta los cambios y qué decisión podría mejorar con una nueva herramienta.

La voz resulta atractiva porque puede capturarse con equipos asequibles y repetirse sin un procedimiento invasivo. Sin embargo, varía con el idioma, el contexto, el micrófono, la distancia, el esfuerzo, el cansancio y el estado de la persona. Una señal estadística en un corpus no equivale a un indicador específico de Parkinson en cualquier entorno. La principal dificultad no es grabar o ejecutar una fórmula, sino demostrar que el resultado conserva su significado fuera del conjunto de entrenamiento.

VoxWave debe evitar asumir que toda persona con Parkinson tiene el mismo patrón vocal o que una voz sin alteraciones aparentes descarta la enfermedad. La pregunta útil es qué información adicional aporta el sistema, para quién, con qué errores y frente a qué procedimiento actual. Esa pregunta debe guiar la recogida de datos y el modelo de negocio.

## 3 Propuesta de valor y alcance

La propuesta para la persona participante es completar tareas sencillas con instrucciones accesibles y conocer si la grabación ha sido válida. Para el profesional, es disponer de mediciones trazables y comparables, con calidad, fecha, protocolo y contexto. Para la institución, es explorar un proceso estandarizado cuyo coste y carga operativa puedan medirse.

El MVP incluirá captura de audio, control de calidad, extracción de características, registro de resultados y una visualización comprensible. Un clasificador experimental solo se activará cuando existan datos autorizados, una evaluación por participante y documentación del modelo. El seguimiento personal podrá empezar como visualización descriptiva; atribuir un cambio a evolución clínica requerirá evidencia adicional.

Quedan fuera del MVP el diagnóstico autónomo, la recomendación de cambios de medicación, la sustitución de consultas, las garantías de detección temprana, la inferencia libre mediante un modelo conversacional y la monitorización ambiental permanente. Se propone grabar únicamente después de una acción explícita de la persona. Las futuras ampliaciones deberán mantener el foco en Parkinson.

La frase de posicionamiento propuesta es: «VoxWave transforma pruebas de voz estandarizadas en información acústica para investigar herramientas accesibles de apoyo al cribado y seguimiento del Parkinson». En una presentación breve puede simplificarse, pero no debe eliminarse la diferencia entre una herramienta en desarrollo y un producto validado.

## 4 Usuarios y contexto de uso

Conviene separar beneficiario, operador, intérprete y comprador. La persona que realiza la prueba es el beneficiario directo. Un profesional, investigador o cuidador autorizado puede ayudar a operarla. La interpretación clínica corresponde al profesional responsable. El comprador inicial podría ser una unidad de investigación, clínica, asociación con colaboración clínica o institución que financie un piloto; estas son hipótesis comerciales, no acuerdos existentes.

Se recomienda evaluar primero un entorno supervisado. Facilita comprobar la colocación del micrófono, las instrucciones, los motivos de repetición y la experiencia de uso. El uso domiciliario añade variabilidad acústica, conectividad, soporte, almacenamiento y posibles problemas de comprensión. Debe tratarse como una ampliación del entorno validado.

La interfaz necesita texto grande, contraste suficiente, instrucciones de una sola acción, botón fácil de pulsar y tiempo para responder. El color debe acompañarse de palabras o símbolos. Una pantalla OLED pequeña puede mostrar el estado, pero no sustituye una interfaz legible para instrucciones complejas. La ayuda sonora es opcional y debe detenerse antes de grabar.

Las pruebas de usabilidad deberían incluir personas del perfil objetivo, no solo compañeros del equipo. Deben observarse dudas, repeticiones, abandonos y necesidad de ayuda. Una entrevista posterior puede explorar confianza, incomodidad al grabarse y comprensión del resultado. El objetivo es detectar fallos del proceso, no evaluar clínicamente a quienes participen en una simple prueba de interfaz.

## 5 Recorrido de una sesión

Antes de grabar, el sistema explica el propósito, el uso de los datos y la posibilidad de detenerse. El operador verifica identidad seudonimizada, protocolo y dispositivo. Se comprueba el ruido de fondo y se realiza una prueba corta de micrófono. La sesión comienza solo cuando el audio resulta técnicamente utilizable.

El protocolo abreviado propuesto en las conversaciones comprende una vocal /a/ sostenida durante unos 5 segundos, repetición de /pa-ta-ka/ durante unos 10 segundos, una frase controlada durante unos 10 segundos y habla espontánea durante unos 20 segundos. Estas duraciones son orientativas. La sesión real incluye instrucciones, pausas y posibles repeticiones, por lo que no debe prometerse una duración total exacta de un minuto.

La frase «El perro corre por el parque» apareció como ejemplo. No debe considerarse equivalente a las frases originales de un corpus ni presentarse como prueba clínica validada. Para transferir un modelo entre investigación y dispositivo es preferible conservar las tareas y condiciones para las que se entrenó, o estudiar explícitamente el efecto del nuevo protocolo.

Tras cada tarea se comprueba si hay voz suficiente, saturación, silencios inesperados o archivo incompleto. Cuando una tarea falla, se ofrece una indicación específica y una repetición limitada. La persona puede finalizar sin completar todo. El resultado conserva qué tareas existen y cuáles faltan; no rellena automáticamente los datos ausentes con ceros.

Al terminar, se informa de la calidad y del estado del análisis. En una demo sin validación clínica se muestran características o ejemplos identificados como experimentales. En un futuro estudio clínico, el contenido y la acción posterior estarán definidos en su protocolo. El sistema registra la entrega del resultado y cualquier revisión humana, sin convertir una grabación inválida en una señal tranquilizadora.

## 6 Qué mide el sistema

Las características acústicas son descripciones de la señal. Su interpretación depende de cómo se graba y calcula cada una. VoxWave necesita un diccionario que especifique nombre, unidad, tarea aplicable, algoritmo, parámetros, rango de validez y tratamiento de valores ausentes. Ese diccionario forma parte del producto, porque cambiar la medición puede cambiar el modelo.

| Familia | Qué resume | Precaución de interpretación |
|---|---|---|
| F0 y variación tonal | Frecuencia fundamental y su distribución | Revisar errores de seguimiento y tramos sin sonoridad |
| Jitter | Variación entre periodos de ciclos vocales | Usarlo solo cuando la periodicidad permite medirlo |
| Shimmer | Variación de amplitud entre ciclos | Sensible a ganancia y procesamiento del micrófono |
| HNR | Relación entre estructura armónica y ruido | Depende del método y de la calidad de captura |
| MFCC y espectro | Representación de la envolvente espectral | También reflejan dispositivo, idioma y entorno |
| Pausas y ritmo | Distribución temporal del habla | Mantener silencios internos y definir qué es una pausa |
| DDK | Regularidad y velocidad de secuencias articulatorias | Verificar detección de sílabas contra anotación humana |
| Energía y prosodia | Variación relativa de intensidad y entonación | No equiparar amplitud digital con presión sonora calibrada |

La fonación sostenida y el habla conectada responden a preguntas distintas. No conviene mezclar todas las medidas en una media indiferenciada. Puede construirse un vector por tarea y una agregación por sesión, conservando información sobre cuántos segmentos válidos contribuyen. Si una característica falla, el informe de calidad debe permitir distinguir un problema del algoritmo de una propiedad del audio.

Un gráfico con «estabilidad», «articulación» o «prosodia» solo debe usarse si cada eje tiene una definición y una transformación documentadas. Un panel de cinco estrellas puede sugerir una escala clínica inexistente. Es preferible mostrar valores, unidades, intervalos descriptivos y estado experimental. Las explicaciones de un clasificador indican qué variables influyeron en su cálculo; no demuestran causalidad clínica.

## 7 NeuroVoz y estrategia de datos

NeuroVoz es un corpus de habla en castellano vinculado a la Universidad Politécnica de Madrid y al Hospital General Universitario Gregorio Marañón. El artículo describe 112 participantes, 54 con Parkinson y 58 controles, con grabaciones de los participantes con Parkinson en estado ON. Incluye fonaciones, DDK, repetición de frases y monólogos. [S2]

Existe una discrepancia de versiones que debe conservarse: el repositorio de código describe 108 hablantes y 2.903 audios; el registro v3 de Zenodo describe 112 participantes y 2.977 archivos. Los archivos de Zenodo tienen acceso restringido. El tamaño efectivo del experimento deberá calcularse sobre la versión autorizada y descargada, después de aplicar exclusiones documentadas. [S3, S4]

La unidad estadística principal es la persona. Miles de archivos de un centenar de hablantes no equivalen a miles de participantes independientes. También importa el origen clínico de las etiquetas, la distribución por edad, la representación de diferentes perfiles vocales y la relación entre condición clínica y equipo de grabación. Un modelo puede aprender señales de selección o adquisición en lugar de la diferencia de interés.

El plan de acceso debe describir institución, responsable, objetivo, usuarios autorizados, almacenamiento y destino de resultados. Deben revisarse las condiciones específicas de los audios y metadatos. La licencia MIT del repositorio de código no concede por sí sola derechos sobre las grabaciones ni sobre una explotación comercial del conjunto. No se presupone que VoxWave tenga acceso aprobado.

Al recibir datos, se crea un manifiesto con identificadores seudonimizados, tareas, sesiones, rutas internas, frecuencia de muestreo, duración, checksum, versión y motivos de exclusión. Se conserva el original inmutable y se generan derivados reproducibles. Las etiquetas deben permanecer separadas de las rutas y de cualquier atajo que el modelo pudiera aprovechar accidentalmente.

Otros corpus podrían servir para validación externa, pero su selección queda pendiente de idioma, tareas, permisos y calidad de etiquetas. Combinar conjuntos sin estudiar su procedencia puede producir una clasificación del hospital o micrófono. El experimento externo debe especificar qué cambió: población, lengua, protocolo o hardware. No basta con reunir más archivos para resolver la generalización.

### Acceso y condiciones de uso

El acuerdo de NeuroVoz aportado en el historial prohíbe la reidentificación, exige autorización escrita para redistribución y para uso comercial de materiales o derivados, y establece obligaciones de atribución. Debe conservarse el texto aplicable a la descarga concreta. La participación en un concurso no sustituye la confirmación de que el uso y la exhibición previstos son compatibles. El usuario identificó el receptor de Zenodo como byo_upm; se había preparado un correo a Juan Ignacio Godino Llorente, pero no hay comprobante de envío o aprobación. [S14]

### Estrategia báltica y adaptación lingüística

Una línea importante del proyecto es desarrollar una solución útil para idiomas europeos con menor representación en datos clínicos, comenzando por Lituania y explorando Letonia y Estonia. Esta visión apareció bajo el nombre provisional VoxTrace y se conserva ahora bajo VoxWave. Empezar un experimento con NeuroVoz en castellano no cambia por sí solo el mercado pretendido: distingue el idioma disponible para investigación del idioma que debe validarse para uso local.

El artículo lituano de Vaiciukynas y colaboradores de 2017 estudió fonación y una frase en lituano con dos canales de grabación, incluido un smartphone. Describe 99 participantes con ambos canales y remite las consultas sobre audios originales al departamento de otorrinolaringología de LSMU. Constituye una referencia relevante para estudiar adquisición y transferencia, no una validación del futuro producto. [S12]

En Estonia se identificó la tesis de Aleksis Krass sobre detección de Parkinson en grabaciones en estonio, supervisada por Joonas Järve y Pille Taba en la Universidad de Tartu. Es un punto de entrada para explorar colaboración y evaluación local. No implica acceso concedido ni relación institucional con VoxWave. [S13]

La arquitectura multilingüe propuesta separaría representación acústica compartida, adaptación por idioma y referencia personal. Son tres hipótesis que deben evaluarse por separado. Un primer estudio podría entrenar con castellano, evaluar sin adaptación en un conjunto lituano reservado y comparar con una adaptación que utilice otros participantes lituanos. El conjunto final no se usa para elegir el adaptador. Una evaluación posterior en estonio añadiría una prueba externa; traducir instrucciones no demuestra equivalencia clínica.

PC-GITA se mencionó como posible corpus adicional y LIEPA-3 como recurso lingüístico para una fase posterior. Sus condiciones y utilidad deberán comprobarse antes de incorporarlos. Un corpus de habla general sin etiquetas clínicas puede ayudar a estudiar idioma, pero no sustituye un corpus etiquetado de Parkinson. No se propone descargar grandes volúmenes de datos para resolver un bloqueo que depende de permisos y etiquetas.

La estrategia de colaboración admite varias modalidades: acceso autorizado a audios, acceso a características con condiciones claras, o evaluación del modelo por la institución sin mover grabaciones. Esta última opción puede servir para una prueba externa, siempre que el protocolo impida ajustar reiteradamente el modelo a los resultados del conjunto reservado. La viabilidad de cualquiera de ellas queda pendiente de acuerdo.

## 8 Arquitectura funcional

El flujo propuesto es: consentimiento y sesión, captura de audio original, control de calidad, preprocesamiento limitado, extracción por tarea, agregación, inferencia experimental, almacenamiento y presentación. Cada etapa produce un registro verificable y puede fallar de manera explícita. La interfaz necesita estados diferenciados para espera, grabación, repetición, análisis, resultado, cancelación y error.

En la primera versión, todo puede ejecutarse en un ordenador. En la versión embebida, la Pi ejecuta captura y análisis local ligero. Un servidor opcional puede recibir resultados autorizados para revisión o investigación, pero no debería ser imprescindible para terminar una sesión local. La conectividad se añade por una necesidad demostrada: sincronización, gestión de dispositivos o revisión remota.

La arquitectura separa el programa de captura, el extractor, el modelo y la interfaz. Esto permite cambiar el dispositivo sin rehacer el entrenamiento, siempre que se verifique equivalencia de las características. Un contrato de datos común debe impedir que un modelo reciba columnas en distinto orden, unidades incompatibles o una versión de extractor no admitida.

El paquete de despliegue debe incluir modelo, transformaciones, lista ordenada de características, protocolo, parámetros del extractor, umbral si procede, versión, dependencias, firma o checksum y pruebas de referencia. La inferencia debe detenerse ante incompatibilidad. No se descargarán modelos de procedencia desconocida ni se deserializarán archivos de modelo no confiables.

## 9 Captura y preprocesamiento

Se propone guardar audio PCM en WAV sin compresión con pérdidas. La frecuencia de muestreo y la profundidad se fijarán tras revisar el corpus y las necesidades de las medidas. Si se adopta 16 kHz para una rama del análisis, se documentará su idoneidad; no se descartará el original cuando otros parámetros necesiten mayor ancho de banda. Cada conversión debe quedar registrada.

La distancia al micrófono, la posición, el nivel de ganancia y el entorno deben ser consistentes. La distancia de 20 cm mencionada previamente es un punto de partida de ingeniería, no un estándar validado para VoxWave. Un soporte o marca física puede ayudar a repetir la colocación. La interfaz debe pedir una voz cómoda y evitar forzar la intensidad para alcanzar un objetivo artificial.

Los controles iniciales deberían cubrir saturación, archivo vacío, señal insuficiente, duración válida, ausencia de voz y ruido estimado. Sus umbrales se ajustan sobre pruebas de captura, antes de evaluar rendimiento clínico. Un rechazo técnico se explica con una causa concreta. La tasa de rechazo se publica junto con la precisión del modelo para evitar aparentar buen rendimiento a costa de excluir los casos difíciles.

La detección de actividad vocal puede recortar silencio externo o delimitar segmentos, pero eliminar pausas internas destruiría información temporal. La normalización de amplitud tampoco es neutra si se quiere medir variación de energía. La reducción de ruido, compresión, ganancia automática y realce de voz pueden modificar características; deben desactivarse cuando sea posible o evaluarse como parte del sistema.

La primera prueba de ingeniería compara varias grabaciones repetidas de la misma señal y de personas voluntarias con el mismo equipo. Se registra dispersión de medidas, fallos y sensibilidad a distancia o ruido. Esta prueba comprueba repetibilidad del proceso; no proporciona sensibilidad o especificidad para Parkinson.

## 10 Extracción y entrenamiento

La ruta sugerida es Python para investigación, bibliotecas de lectura de audio, un extractor acústico definido y scikit-learn para modelos clásicos. openSMILE con eGeMAPS es un candidato, no una obligación. El conjunto exacto de características depende de la versión y configuración. Antes de integrarlo en desarrollo de producto deben revisarse sus términos comerciales, incluidos los usos indirectos de características o modelos. [S6]

La primera referencia será un clasificador trivial y después regresión logística regularizada. Una SVM lineal y un modelo de árboles pueden compararse con el mismo esquema de evaluación. La selección no se decide por una única cifra máxima: cuentan estabilidad entre particiones, calibración, recursos, complejidad y facilidad de reproducir resultados.

Imputación, escalado y selección de variables se ajustan exclusivamente con el conjunto de entrenamiento de cada partición. La búsqueda de hiperparámetros usa una validación interna también separada por participante. Todas las sesiones y tareas de una persona permanecen juntas. Si hay múltiples centros, se añadirá una evaluación por centro cuando el tamaño lo permita.

La calibración requiere datos separados del ajuste del modelo dentro del diseño de evaluación. El umbral se fija según el uso y los costes de error definidos previamente; no se elige mirando repetidamente el conjunto final de prueba. Una puntuación entre cero y uno no es automáticamente una probabilidad individual de Parkinson.

Los modelos de embeddings o redes pequeñas son una línea de comparación posterior. Su evaluación debe justificar cualquier mejora frente al modelo sencillo y considerar licencias, tamaño, consumo y sesgos. Un modelo conversacional no sustituye al extractor ni al clasificador. La transcripción puede incorporarse si una tarea la necesita, pero sus errores pueden introducir otra fuente de confusión.

## 11 Validación y métricas

El protocolo de evaluación debe registrarse antes de examinar los resultados finales. Debe definir población, unidad de análisis, particiones, exclusiones, tareas, métricas principales y tratamiento de ausentes. Una comprobación automática impedirá que un identificador de participante aparezca a la vez en entrenamiento y prueba.

Se recomienda informar sensibilidad, especificidad, matriz de confusión, balanced accuracy, AUROC y AUPRC cuando correspondan, junto con intervalos de incertidumbre. También deben informarse prevalencia de la muestra, calibración, valores predictivos para la población pertinente y cobertura del sistema. Los intervalos por remuestreo deben respetar la agrupación por persona. Si los subgrupos son pequeños, se describe la limitación en lugar de concluir ausencia de sesgo.

Un ejemplo puramente aritmético muestra por qué importa la población: con prevalencia hipotética del 1%, sensibilidad del 90% y especificidad del 90%, entre 10.000 personas habría aproximadamente 90 verdaderos positivos y 990 falsos positivos. El valor predictivo positivo sería 90 dividido entre 1.080, aproximadamente 8,3%. Estos supuestos no son resultados de VoxWave ni estimaciones de la población del proyecto.

El análisis de errores debe revisar audios rechazados, errores de segmentación, distribución por dispositivo, edad, sexo registrado, idioma y contexto de medicación cuando esos datos estén disponibles y su tratamiento esté autorizado. Es útil comparar un modelo con variables demográficas frente a otro acústico para detectar posibles atajos, sin transformar esos análisis en decisiones clínicas automáticas.

La validación externa utiliza personas que no participaron en el desarrollo y, preferiblemente, otra fuente o entorno. Después, un estudio prospectivo observa el sistema en el flujo previsto. Su tamaño muestral se calcula según el objetivo y precisión requerida, con apoyo estadístico. Un pequeño piloto de usabilidad no puede certificar rendimiento clínico.

El criterio de avance no debe ser un porcentaje elegido para impresionar. Primero se demuestra ausencia de fugas y mejora reproducible sobre una referencia trivial. Después se define con profesionales el mínimo útil de sensibilidad, especificidad, cobertura y carga de revisión. El coste de falsos positivos y negativos forma parte del diseño desde el principio.

## 12 Seguimiento personal y referencia longitudinal

La referencia personal es una hipótesis de producto prometedora: recoger varias sesiones comparables y estudiar desviaciones respecto a la variabilidad habitual de la misma persona. Los días 1, 3, 5 y 7 citados en el diseño previo eran ilustrativos. El número y frecuencia de sesiones deben elegirse después de observar repetibilidad y carga de uso.

El sistema debe registrar cambios de micrófono, protocolo y versión, así como contexto relevante de la sesión. Una actualización técnica puede crear un salto artificial en la serie. Por ello, las comparaciones entre versiones necesitarán una prueba de equivalencia o una nueva referencia. La ausencia de suficientes sesiones válidas debe aparecer como «referencia insuficiente».

Una desviación vocal no prueba progresión de Parkinson. Para estudiar esa relación hacen falta datos longitudinales y una referencia clínica apropiada. Tampoco puede inferirse respuesta a tratamiento a partir de un corpus transversal de personas grabadas en ON. El modelo poblacional y el seguimiento personal deben mantenerse como salidas separadas hasta que exista evidencia para combinarlos.

Se propone usar estadísticas robustas y visualizar tendencias con incertidumbre, evitando alertas por una única medida aislada. La frecuencia de revisión y los criterios de notificación se definirán con el profesional responsable. Para el prototipo basta mostrar sesiones, calidad y evolución descriptiva de medidas, sin automatizar decisiones asistenciales.

## 13 Hardware y Raspberry Pi

La Raspberry Pi Zero 2 W dispone de CPU Arm Cortex-A53 de cuatro núcleos a 1 GHz, 512 MB de RAM, conectividad inalámbrica y formato de 65 por 30 mm. La Zero original tiene una arquitectura y capacidad diferentes. La documentación del fabricante permite valorar la plataforma, pero no demuestra que el pipeline completo de VoxWave funcione con los tiempos deseados. [S5]

Se recomienda reservar el entrenamiento para el ordenador. La Pi ejecutaría instrucciones, captura, control de calidad, extracción ligera e inferencia. Los 512 MB exigen controlar dependencias y procesamiento por bloques. Instalar un modelo pequeño no resuelve automáticamente el coste del extractor. Deben medirse tiempo total, memoria máxima, arranque, temperatura, consumo y funcionamiento sin red.

| Elemento | Función | Decisión propuesta para el primer prototipo |
|---|---|---|
| Ordenador | Desarrollo y entrenamiento | Primera plataforma de referencia |
| Pi Zero 2 W | Ejecución local embebida | Incorporar después de validar el flujo |
| Micrófono USB | Captura inicial | Priorizar estabilidad y acceso a audio sin realce |
| Micrófono digital I2S | Integración compacta | Evaluar después por controlador y reproducibilidad |
| MicroSD | Sistema y datos locales | Imagen versionada y control de espacio |
| Botón grande | Inicio o confirmación | Añadir antirrebote y estado visible |
| Pantalla o interfaz accesible | Instrucciones | Comprobar legibilidad antes de elegir tamaño |
| Indicador luminoso | Estado de captura | Complementar siempre con texto |
| Alimentación USB | Funcionamiento | Primera opción antes de batería |
| Carcasa y soporte | Protección y colocación | Diseño sencillo que no altere la acústica |

INMP441, ICS-43434 y SPH0645 aparecieron como ejemplos de familias de micrófonos digitales en la conversación. No constituyen una lista de compra validada: hay que confirmar disponibilidad, autenticidad, compatibilidad eléctrica, controlador y calidad de captura. Un micrófono USB conocido reduce complejidad inicial, aunque también debe verificarse su procesamiento interno.

La batería puede añadirse tras medir el consumo real. Su elección debe incluir protección, carga, autonomía y apagado seguro. La tarjeta puede corromperse si se corta alimentación mientras se escribe. El diseño necesita gestión de sesiones incompletas y recuperación al reiniciar. Una carcasa atractiva no debe impedir ventilación, higiene, reparación o posición repetible del micrófono.

La alternativa de móvil u ordenador sigue siendo válida. Se propone una comparación controlada: mismo protocolo, mismas personas y medidas de repetibilidad, tiempo y coste. Si el hardware dedicado no mejora resultados ni acceso, puede mantenerse como demostrador sin convertirse en el centro del negocio. Esta decisión se tomará con evidencia de uso, no por preferencia estética.

## 14 Software y contrato de resultados

Una organización de trabajo posible separa módulos de captura, calidad, características, inferencia, interfaz y almacenamiento. Las pruebas deben centrarse en fallos con consecuencias: audio vacío, saturación, columnas desordenadas, versión incompatible, interrupción de energía, repetición de envío y ausencia de consentimiento válido.

Cada sesión tendrá un identificador opaco y un estado. El resultado incluirá versión del esquema, protocolo, equipo, fecha, tareas completadas, indicadores de calidad, características con unidades, versión del modelo y estado de inferencia. Si el análisis no puede realizarse, la puntuación será nula y habrá una causa explícita. Un cero es un valor; no debe utilizarse para representar un error.

Los datos identificativos se separarán de las mediciones. Para sincronización, una cola local guardará eventos pendientes y evitará duplicados mediante identificadores únicos. Los registros técnicos no deben contener audio, nombres o texto libre innecesarios. El operador tendrá una forma visible de comprobar espacio, micrófono, versión y última sesión completada.

El despliegue precisa una imagen reproducible, dependencias fijadas, pruebas de audio de referencia y una opción de reversión. La actualización del modelo se trata como un cambio del sistema completo: puede afectar a puntuaciones, tendencias y documentación. No se sustituye silenciosamente un modelo mientras continúa una serie longitudinal.

## 15 Presentación del resultado y flujo profesional

La pantalla final debe contestar primero si la prueba fue válida. Después puede mostrar mediciones o una puntuación experimental, indicando qué tareas contribuyeron. Una categoría de riesgo solo se introducirá tras definir umbrales, población y acción asociada. Los términos «bajo», «moderado» y «elevado» propuestos previamente no son categorías clínicas establecidas de VoxWave.

Para una demostración, un texto apropiado sería: «Sesión completada. Estas medidas describen la grabación y forman parte de un prototipo de investigación». Si falla el audio: «No se ha podido analizar esta tarea porque la grabación está saturada. Puede repetirse con la colocación indicada». Los ejemplos de interfaz deben revisarse con usuarios para comprobar comprensión.

En un futuro piloto asistencial deberá existir un responsable de revisar resultados, un plazo, un canal y un registro de acciones. Una alerta sin capacidad de respuesta no resuelve el problema. También deben definirse casos no evaluables, retirada del estudio y comunicación de incidencias. La decisión profesional se conserva como una etapa distinta de la salida del algoritmo.

El informe para profesionales puede reunir fecha, tarea, calidad, contexto, resultados y comparación temporal. Debe permitir rastrear cada cifra hasta el archivo autorizado y la versión de procesamiento, sin distribuir grabaciones innecesariamente. La integración con otros sistemas se estudiará después de validar qué información necesita realmente el destinatario.

## 16 Privacidad y seguridad por diseño

El proyecto debe tratar las grabaciones y las inferencias de salud como información sensible. Quitar un nombre no garantiza anonimato de la voz. En un escenario europeo deberán justificarse la base del artículo 6 y la condición aplicable del artículo 9 del RGPD, junto con finalidad, minimización, conservación y derechos. El consentimiento de investigación y la base jurídica del tratamiento no son conceptos intercambiables. [S7]

Como propuesta de diseño, VoxWave separará identidad y mediciones, limitará accesos por función y conservará una trazabilidad de accesos. Se cifrará la transmisión y se protegerán almacenamiento y claves. Los permisos para participar, conservar audios y reutilizarlos en entrenamiento se explicarán de forma diferenciada según el protocolo autorizado.

Antes de recoger datos reales, el responsable deberá fijar una política de retención con plazos y procedimiento de borrado, incluida la gestión de copias. También deberá evaluar si corresponde una evaluación de impacto y documentar proveedores o transferencias. El procesamiento local reduce algunos flujos de datos, pero no elimina obligaciones ni riesgos de pérdida del dispositivo.

El modelo de amenazas propuesto incluye acceso físico a la tarjeta, equipo compartido, credenciales expuestas, sincronización duplicada, actualización manipulada y archivo de modelo no confiable. Para la demo pública se utilizarán datos sintéticos o ejemplos con permisos adecuados. No deben subirse audios de participantes a asistentes de IA o servicios externos sin autorización y condiciones compatibles.

## 17 Ruta regulatoria y de calidad

La finalidad prevista determina el análisis regulatorio. Llamar «screening» a un sistema o añadir un aviso no elimina por sí solo su posible consideración como producto sanitario. La guía MDCG 2019-11 revisión 1, publicada en junio de 2025, orienta la cualificación y clasificación del software bajo el marco europeo. La clase concreta de VoxWave no puede fijarse sin definir su uso, usuarios y consecuencias de decisiones. [S8]

El trabajo inmediato es redactar una finalidad prevista de una página y someterla a revisión especializada antes de desplegar una función clínica. La evaluación debe contemplar software y hardware, evidencia, gestión de riesgos, usabilidad, ciberseguridad y obligaciones de seguimiento. El análisis de normativa de IA y su calendario se incorpora a esa revisión según la clasificación efectiva y el modo de comercialización.

Como práctica de ingeniería desde el MVP, se propone mantener requisitos numerados, incidencias, versiones, pruebas y decisiones. Esto no acredita conformidad, pero evita perder trazabilidad. Una modificación en micrófono, protocolo, extractor o umbral debe registrar motivo, impacto y validación necesaria. La documentación se construye junto al sistema, no al final de la presentación.

El equipo no debe anunciar marcado, autorización, certificación ni aprobación de autoridades sin evidencia documental. Tampoco una colaboración académica sustituye la revisión ética que pueda requerir un estudio. La demo, el piloto de usabilidad, la investigación clínica y la comercialización son etapas diferentes y deben presupuestarse por separado.

## 18 Modelo de negocio y adopción

La hipótesis recomendada es una entrada institucional con pilotos supervisados. Reduce la necesidad de convencer a consumidores individuales de interpretar su voz y permite observar un flujo concreto. El comprador podría pagar por el servicio, el dispositivo, el soporte o una combinación. La estructura definitiva depende de quién obtiene valor y quién asume la revisión.

Hay tres opciones para contrastar. Una licencia de software con equipo compatible reduce fabricación, pero puede aumentar variabilidad de captura. Un dispositivo con servicio facilita estandarización, pero añade logística y mantenimiento. Un servicio de investigación ofrece un primer uso delimitado, aunque no demuestra demanda de un producto asistencial. Las entrevistas deben evaluar estas opciones con problemas y costes reales.

El proceso comercial propuesto comienza por descubrir el trabajo actual del centro, acordar un piloto con objetivos medibles y documentar carga operativa. Se registran tiempo de instalación, formación, sesiones completadas, soporte y disposición a continuar. Las cartas de interés pueden apoyar la demanda, pero no se contarán como ingresos ni como validación clínica.

No se propone vender datos de voz como fuente principal de ingresos. La ventaja competitiva deseada es una combinación de adquisición consistente, flujo útil, evidencia, integración y confianza. Un modelo clásico por sí solo es fácil de replicar. La barrera defendible surge de resolver el problema operativo y validar el sistema con datos y permisos adecuados.

## 19 Economía del prototipo y escenarios

Los siguientes importes son supuestos de planificación internos en euros, no cotizaciones ni precios verificados de mercado. Deben sustituirse por ofertas concretas con impuestos, transporte, disponibilidad y licencias. Su finalidad es mostrar qué partidas existen y cómo afectan a la decisión de fabricar.

| Partida de un prototipo | Supuesto inferior | Supuesto superior |
|---|---:|---:|
| Placa de procesamiento | 20 | 35 |
| Micrófono y adaptadores | 20 | 50 |
| Almacenamiento y alimentación | 20 | 35 |
| Botón e indicadores o pantalla | 10 | 30 |
| Carcasa y montaje básico | 15 | 40 |
| Total de componentes | 85 | 190 |

El total excluye horas del equipo, equipos de desarrollo, licencias, validación, soporte, fallos y certificación. Una reserva ilustrativa del 20% situaría componentes y contingencia entre 102 y 228 euros por prototipo. Es posible comenzar por debajo de ese coste incremental si ya se dispone de ordenador y micrófono; eso no equivale al coste de entregar una unidad comercial.

Un ejemplo de servicio también debe separar ingresos y costes. Con una cuota hipotética de 40 euros por centro y mes y 15 euros de costes variables de servicio, la contribución sería 25 euros por centro y mes. Para cubrir 1.000 euros de costes fijos mensuales se necesitarían 40 centros, antes de recuperar desarrollo, equipos u otros costes omitidos. Estas cifras sirven para discutir el modelo, no como recomendación de precio.

El mercado se estimará de abajo arriba: centros alcanzables, perfiles elegibles por centro, sesiones previstas y capacidad de pago. TAM, SAM y SOM tendrán definiciones, fuentes y periodo. La prevalencia mundial no se multiplicará por una cuota para presentar ingresos plausibles. La previsión debe incluir adopción lenta, abandono, sustitución de equipos y carga de soporte.

## 20 Competencia y alternativas

La alternativa principal puede ser el procedimiento que ya usa el profesional. También compiten por la misma necesidad las aplicaciones de grabación, las evaluaciones remotas, herramientas de investigación vocal y otros sistemas de seguimiento de Parkinson. Sin una revisión específica de productos y su situación actual no debe afirmarse que VoxWave es el primero o que no tiene competencia.

La matriz de investigación comercial debería comparar finalidad, población, idioma, evidencia publicada, captura, necesidad de hardware, integración, privacidad, coste y estado regulatorio. Cada celda debe citar una fuente y fecha. Los anuncios de un proveedor se distinguirán de validación independiente. La ausencia de información pública quedará como desconocida.

La diferenciación que merece probarse es una experiencia sencilla con captura repetible y procesamiento local opcional, compatible con recursos limitados. Para defenderla habrá que medir tiempo, tasa de repetición, variabilidad y carga de revisión frente a las alternativas. El equipo puede cambiar la forma de entrega si una aplicación resuelve mejor el mismo problema.

## 21 Impacto social y sostenibilidad

La relación principal propuesta con la Agenda 2030 es el ODS 3, por la aspiración de apoyar acceso y continuidad de atención. El ODS 10 puede ser relevante si el diseño demuestra que reduce barreras. El ODS 9 puede encajar como innovación aplicada. Estas asociaciones son un marco de presentación, no una acreditación ni una prueba de impacto.

La teoría de cambio comienza con recursos: equipo, datos autorizados y colaboradores. Las actividades son desarrollar, probar y evaluar un proceso vocal accesible. Los productos inmediatos son sesiones válidas, informes y aprendizaje de implementación. Los resultados intermedios que deben estudiarse incluyen mejor información para revisión, menor carga y acceso más fácil. El impacto en salud requiere evidencia adicional y una comparación pertinente.

Los indicadores del primer piloto serán tasa de finalización, necesidad de ayuda, repeticiones, tiempo total, comprensión del resultado y coste por sesión válida. En una fase clínica podrán estudiarse decisiones apoyadas y tiempos hasta revisión, con un diseño capaz de atribuir efectos. Número de descargas o dispositivos entregados no equivale a beneficio para la salud.

El dispositivo debe contemplar reparación, reutilización y consumo. Evitar hardware innecesario puede mejorar coste y sostenibilidad. La accesibilidad incluye idioma, alfabetización digital, capacidad motora y conectividad. Si el rendimiento es inferior en determinados grupos, el proyecto debe corregirlo o limitar su uso; una promesa universal sin datos debilitaría el objetivo social.

## 22 Creative Shock y presentación

La página para participantes de Creative Shock 2026 describe equipos de 3 a 4 estudiantes, una ronda online del 5 al 11 de octubre, anuncio de finalistas el 15 de octubre y final presencial del 18 al 21 de noviembre en Vilna. La página principal anuncia un vídeo de 3 a 5 minutos. Conserva además algunas preguntas frecuentes de 2025; por ello, el correo y las bases recibidas por el equipo deben resolver hora límite y requisitos exactos. [S9, S10]

El briefing aportado por el equipo concreta la entrega el 11 de octubre a las 23:59 EEST, UTC+3. Exige subir el vídeo a Google Drive y enviar el enlace compartible mediante el formulario correspondiente. Pide explicar marketing y finanzas, aunque no exige un modelo financiero detallado. Antes del envío hay que comprobar duración, permisos de reproducción del enlace y recepción del formulario. El año se interpreta en el contexto de la edición 2026 y deberá prevalecer cualquier actualización enviada por la organización. [S11]

| Criterio del briefing | Evidencia que debe mostrar VoxWave |
|---|---|
| Problema y necesidad del usuario | Persona concreta, barrera observada y entrevistas |
| Solución e innovación | Flujo de voz y diferencia comprobable frente a alternativas |
| Impacto y relación con ODS | Cadena de impacto y métricas, especialmente ODS 3 |
| Potencial de construcción con IA | MVP acotado, demo y componentes realizables |
| Negocio y sostenibilidad | Comprador, motivo de pago, costes y adopción |
| Pitch y narrativa | Explicación entendible dentro de 3 a 5 minutos |

El mensaje central propuesto es un problema social observable, una solución delimitada, un negocio posible y un experimento que reduce incertidumbre. No conviene dedicar todo el vídeo al algoritmo. El jurado debe comprender quién usaría VoxWave, quién pagaría, cómo se integra en el trabajo real y qué se ha construido efectivamente.

Un guion de cuatro minutos puede distribuir aproximadamente 35 segundos al problema, 45 al usuario y recorrido, 55 a la demostración, 45 a negocio e impacto, 40 a evidencia y límites y 20 al equipo y siguiente hito. Esta distribución es una propuesta narrativa, no una rúbrica oficial. Se ajustará al encargo concreto recibido.

La demostración ideal muestra una tarea vocal, el control de calidad, dos o tres medidas bien explicadas y la salida del sistema. Puede incluir una grabación de respaldo por si falla el hardware. Si las pantallas o resultados son simulados, se identifican antes de mostrarlos. No se invita al jurado a interpretar una prueba propia como información de salud.

Las preguntas previsibles son por qué voz, por qué hardware, qué ventaja aporta frente a un móvil, cómo se validará, qué ocurre con los errores, qué permisos existen, cuánto cuesta operar y quién compra. La respuesta fuerte es concreta y verificable. Ante un resultado aún no medido se presenta el experimento y el criterio de decisión, sin inventar certeza.

## 23 Branding y logotipo

El nombre confirmado es VoxWave, con V y W mayúsculas. La dirección visual recuperada combina las letras V y W con una onda de audio continua. Las revisiones del promotor piden una V más recta y geométrica, una W más ondulada, continuidad de la onda y una lectura de onda más explícita. También se pidió evitar asociaciones anatómicas involuntarias.

La paleta indicada es azul marino #092634, azul profundo #004E72, coral #FF6E42 y fondo casi blanco #F9F9F9. El estilo deseado es plano, preciso, minimalista y cercano, sin brillos ni texturas realistas. El coral puede servir como acento; no debe codificar un estado clínico por sí solo ni atribuir al símbolo una función de medición.

El siguiente entregable de diseño debe contener una versión vectorial editable, composición horizontal, símbolo independiente, versión monocroma y pruebas a tamaño pequeño. Se comprobará legibilidad de V y W, grosor consistente y comportamiento sobre fondos claros y oscuros. La onda debe reconocerse como voz sin aparentar un registro cardiológico o una certificación médica.

El tono verbal será claro, sobrio y empático. Son adecuados «medición vocal», «calidad de grabación», «prototipo» y «apoyo a la investigación». Deben evitarse promesas absolutas y metáforas que conviertan el análisis en un detector infalible. La disponibilidad jurídica del nombre y de dominios queda por comprobar antes de una inversión comercial significativa.

## 24 Riesgos y decisiones de mitigación

| Riesgo | Consecuencia | Respuesta propuesta |
|---|---|---|
| Acceso a datos pendiente | No puede entrenarse el modelo previsto | Solicitar permisos y mantener demo acústica sin clasificación |
| Fuga entre participantes | Rendimiento artificialmente alto | Particiones agrupadas y comprobación automática |
| Diferencia entre corpus y dispositivo | Error fuera del laboratorio | Estudio de transferencia y prueba externa |
| Interpretación excesiva del resultado | Confusión y falsa confianza | Mensajes probados y revisión profesional definida |
| Variabilidad del micrófono | Cambios de medidas sin cambio de voz | Configuración fija y pruebas de repetibilidad |
| Recursos insuficientes de la Pi | Fallos o tiempos excesivos | Medir primero y mantener ejecución en ordenador |
| Licencias incompatibles | Bloqueo de producto | Revisar permisos antes de comprometer arquitectura |
| Carga de revisión elevada | Escasa adopción | Medir flujo y coste de atender resultados |
| Dependencia de pocas personas | Retrasos y pérdida de conocimiento | Documentar decisiones y repartir entregables |
| Afirmaciones sin respaldo | Pérdida de credibilidad | Registro de evidencias y revisión del pitch |

El riesgo más importante para la viabilidad no se resuelve añadiendo complejidad al modelo. Es necesario comprobar que el sistema mide de forma consistente y que la información puede usarse en un proceso real. Si esas condiciones fallan, la respuesta adecuada es simplificar el alcance, cambiar el entorno o reformular la propuesta de valor.

## 25 Roadmap y puertas de avance

La fase inmediata, del 7 al 11 de octubre de 2026 como calendario propuesto para la ronda anunciada, prioriza relato, responsabilidades, demo y entrega del vídeo conforme a las bases del equipo. No se compromete un modelo clínico nuevo en ese plazo. En paralelo se prepara la solicitud de datos y se documenta el protocolo de captura.

Durante las siguientes dos semanas, la prioridad técnica será una captura reproducible en ordenador, un manifiesto de datos y pruebas de calidad. Si se dispone de acceso autorizado, se construirá un experimento por participante con modelo sencillo. Si no, se completarán interfaz, mediciones y pruebas de infraestructura con datos adecuados, manteniendo desactivada la clasificación clínica.

La fase posterior incorpora la Pi solo después de que exista una referencia de funcionamiento en ordenador. Se comparan características e inferencia sobre los mismos archivos, memoria y tiempo de sesión. Antes de la final de noviembre puede ser razonable tener un demostrador estable; la disponibilidad de datos o hardware puede alterar esa previsión.

El piloto supervisado requiere finalidad, responsable, permisos y protocolo. La validación externa y prospectiva se planifica después con recursos suficientes. No se fija una fecha de comercialización porque depende de evidencia, financiación y ruta regulatoria. El seguimiento longitudinal se desarrolla como línea separada con datos de sesiones repetidas.

| Puerta | Evidencia para avanzar |
|---|---|
| G1 Captura | Sesiones completas, errores explícitos y repetibilidad documentada |
| G2 Datos | Acceso autorizado, versión y manifiesto auditado |
| G3 Modelo | Evaluación sin fugas y resultados reproducibles con incertidumbre |
| G4 Dispositivo | Equivalencia con ordenador y funcionamiento estable medido |
| G5 Piloto | Protocolo, responsabilidades, permisos y plan de análisis |
| G6 Uso clínico | Evidencia y requisitos aplicables evaluados para la finalidad prevista |

## 26 Equipo y responsabilidades

No se presupone una composición cerrada del equipo. Se proponen cuatro responsabilidades: producto y negocio; datos y modelado; hardware y experiencia de uso; evidencia, documentación y coordinación clínica. Una misma persona puede cubrir varias al principio, pero cada entregable debe tener un responsable identificable y una fecha.

La colaboración clínica debe ayudar a definir la pregunta, población, referencia y consecuencias de los resultados. La colaboración técnica debe verificar audio, modelos y despliegue. Mentores de negocio pueden contrastar comprador, precio y canal. No se presentarán instituciones mencionadas en publicaciones como socios de VoxWave sin un acuerdo real.

El promotor ha indicado que estudia en la Universidad Complutense de Madrid. Esa afiliación académica no equivale a autorización para firmar en nombre de una universidad. Los borradores de correspondencia deben revisarse antes de enviarse: un borrador antiguo utilizó un nombre personal de ejemplo que no debe trasladarse automáticamente a solicitudes reales.

Los contactos de trabajo identificados son BYO-UPM para NeuroVoz y posibles interlocutores en Kaunas y Tartu para datos bálticos. La dirección institucional de Godino Llorente es [email omitted], verificada en la web de UPM. El artículo lituano indica [email omitted] para consultas sobre audios; al ser una publicación de 2017, conviene confirmar la vigencia operativa. Los contactos estonios recuperados de la conversación se guardan en el export como pendientes de reconfirmación. No se ha enviado correspondencia como parte de este documento. [S12, S15]

Las reuniones de avance deberían cerrar tres cosas: evidencia nueva, decisión tomada y siguiente prueba. Un registro breve evita que propuestas de una IA se conviertan accidentalmente en compromisos del equipo. Toda decisión importante conservará fecha, responsable, alternativas y condición para revisarla.

## 27 Backlog accionable

| Prioridad | Trabajo | Entregable comprobable |
|---|---|---|
| P0 | Confirmar bases del concurso y responsables | Lista de requisitos y fecha límite exacta |
| P0 | Fijar finalidad del MVP | Descripción de usuario, entorno y salida |
| P0 | Preparar demo con estados reales | Captura y calidad sin resultados inventados |
| P0 | Preparar vídeo y respaldo | Archivo final y comprobación de reproducción |
| P1 | Tramitar acceso y uso de NeuroVoz | Condiciones aceptadas y versión identificada |
| P1 | Definir protocolo y diccionario acústico | Configuración versionada y unidades |
| P1 | Implementar evaluación agrupada | Informe reproducible por participante |
| P1 | Entrevistar usuarios y compradores | Necesidades, objeciones y criterios de piloto |
| P2 | Probar Zero 2 W | Informe de recursos y equivalencia |
| P2 | Formalizar piloto supervisado | Protocolo y plan de análisis revisados |
| P2 | Finalizar identidad visual | Archivos vectoriales y reglas básicas |
| P3 | Diseñar estudio longitudinal | Objetivos y medidas repetidas justificadas |

La definición de terminado del MVP incluye instrucciones funcionales, audio trazable, control de calidad, extracción reproducible, salida honesta, tratamiento de errores y documentación suficiente para repetir la demo. Un vídeo convincente sin esos componentes es una presentación conceptual; puede ser útil, pero debe denominarse así.

## 28 Preguntas abiertas y próximos pasos

La decisión más urgente es elegir un uso inicial: investigación supervisada de cribado o medición descriptiva para seguimiento. Ambos caben en la visión de VoxWave, pero intentar validar los dos al mismo tiempo aumenta datos, alcance y mensajes. La recomendación es una demo común de captura y análisis, con una primera pregunta experimental explícita.

También quedan por resolver el acceso efectivo a NeuroVoz, idioma y población del primer piloto, micrófono, presupuesto disponible, colaboradores, permisos, plazo real del concurso y capacidad de soporte. Ninguna de esas incógnitas exige paralizar una demo de adquisición, pero sí limita qué resultados pueden anunciarse.

En las próximas 48 horas propuestas, el equipo debería cerrar el guion, montar una captura sencilla, probarla con grabaciones no clínicas autorizadas y producir un vídeo de respaldo. Al mismo tiempo puede preparar, sin asumir aprobación, la solicitud de datos y una ficha de experimento. El éxito inmediato es salir con una propuesta coherente, verificable y lista para aprender.

## 29 Fuentes y trazabilidad documental

Las referencias externas se consultaron el 7 de octubre de 2026. Apoyan hechos concretos sobre corpus, plataforma, términos y contexto; no validan VoxWave. Las recomendaciones de producto, ingeniería, presupuesto y roadmap son propuestas del presente documento. Las decisiones del promotor se conservan con su procedencia en el export complementario.

[S1] Organización Mundial de la Salud. Enfermedad de Parkinson. Ficha de 9 de agosto de 2023. https://www.who.int/es/news-room/fact-sheets/detail/parkinson-disease

[S2] Mendes-Laureano y colaboradores. NeuroVoz a Castillian Spanish corpus of parkinsonian speech. Scientific Data 11, 1367, 2024. Registro del artículo y resumen: https://pmc.ncbi.nlm.nih.gov/articles/PMC11655668/ . DOI: https://doi.org/10.1038/s41597-024-04186-z

[S3] BYO-UPM. Neurovoz_Dababase. Repositorio de autores con scripts y descripción del corpus. https://github.com/BYO-UPM/Neurovoz_Dababase

[S4] NeuroVoz. Registro v3 de Zenodo, publicado el 3 de septiembre de 2024. Metadatos públicos y archivos restringidos. https://zenodo.org/records/13647600

[S5] Raspberry Pi. Ficha oficial de Raspberry Pi Zero 2 W. https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/

[S6] audEERING. Licencia de openSMILE. Revisar la versión concreta utilizada y obtener autorización cuando corresponda. https://github.com/audeering/opensmile/blob/master/LICENSE

[S7] Unión Europea. Reglamento 2016/679, especialmente artículos 6 y 9. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679

[S8] Comisión Europea. Publicación de MDCG 2019-11 revisión 1 sobre cualificación y clasificación de software, junio de 2025. https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en

[S9] Creative Shock. Información para participantes de 2026. https://creativeshock.lt/for-participants

[S10] Creative Shock. Página principal y anuncio del formato de vídeo. https://creativeshock.lt/

[S11] Creative Shock Online Qualification Round Briefing. PDF aportado por el equipo en la conversación Creative Shock Idea Strategy. Requisitos en página 2, plazo y criterios en página 3 y recordatorio de entrega en página 6. Fuente primaria del encargo del concurso.

[S12] Vaiciukynas y colaboradores. Detecting Parkinson's disease from sustained phonation and speech signals. PLOS ONE, 2017. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0185613

[S13] Aleksis Krass. Tesis sobre detección de Parkinson a partir de voz en estonio, Universidad de Tartu, 2025. https://dspace.ut.ee/bitstreams/[id omitted]/download

[S14] Acuerdo de uso de NeuroVoz copiado por el usuario desde Zenodo en la conversación Investiga viabilidad de idea. Texto histórico aportado; conservar y revisar el acuerdo vigente antes de aceptar condiciones o descargar.

[S15] Universidad Politécnica de Madrid. Directorio de personal de Señales, Sistemas y Radiocomunicaciones. https://ssr.upm.es/personal-3/

Fin del documento maestro. Las cifras de escenarios, duraciones del protocolo y plazos de desarrollo propuestos deben revisarse cuando el equipo disponga de datos de ejecución.


<!-- FIN DEL DOCUMENTO MAESTRO -->

FIN DEL EXPORT VOXWAVE 1.0
