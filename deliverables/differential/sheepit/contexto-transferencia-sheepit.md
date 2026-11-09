# Contexto de transferencia — The Physics Within / diferencial / SheepIt

Fecha: 9 de noviembre de 2026. Comunicación con el usuario en español; narración, textos y subtítulos del vídeo en inglés.

## Objetivo inmediato

**Recuperar los fotogramas que ya renderizó SheepIt y terminar el short de 48 segundos con narración, música, efectos, diagramas y subtítulos. NO volver a renderizar la secuencia localmente.**

El usuario informa que ya añadió las URL de SheepIt en la configuración del entorno de la conversación nueva. Verificar esa instancia nueva; no asumir que la configuración de la instancia anterior se actualizó.

Última petición: preparar este archivo de contexto para continuar en la conversación nueva.

## Petición y autorizaciones vigentes

- El usuario pidió un diferencial de automóvil con mucho detalle y realismo, Full HD vertical nativo, y ejecución autónoma.
- Luego canceló expresamente el render local y pidió el `.blend` para SheepIt. La cancelación se ejecutó. No reiniciar `run_production.py` ni `render_frames.py`.
- Autorizó entregar el archivo mediante GitHub. Se creó una rama de exportación, sin fusionarla ni modificar los episodios anteriores.
- Ahora quiere iniciar sesión él mismo en SheepIt desde el escritorio virtual y descargar los resultados allí. Su PC local tiene restricciones administrativas.
- Permitir que el usuario escriba su contraseña en el navegador compartido. No pedir contraseñas, cookies, claves o tokens en el chat.
- No publicar el vídeo, contratar cómputo ni activar otros renders. No borrar el proyecto de SheepIt ni cambiar su configuración. No hacer push de cambios ajenos a esta entrega.
- No volver a preguntar qué mecanismo quiere ni ofrecer solo un plan. Avanzar con descarga, revisión y montaje cuando el acceso funcione.

## SheepIt: proyecto y estado conocido

Proyecto: <https://www.sheepit-renderfarm.com/project/1238988>

Nombre del archivo: `The_Physics_Within_Differential_SheepIt.blend`.

La captura del usuario muestra:

- **1152 / 1152 fotogramas renderizados**.
- Almacenamiento usado: aproximadamente 3,4 GB.
- Tiempo real de render: 48 minutos; tiempo acumulado: 2 h 08 min.
- En el momento de la captura el servidor estaba empaquetando los resultados en ZIP (posición 24). Esto puede haber terminado ya; consultar el estado actual.
- La página indicaba eliminación automática el 22 de noviembre a las 20:10, sin zona horaria confirmada. No reinterpretar ese horario como hora de Chile sin comprobarlo.

No se han descargado ni inspeccionado todavía los fotogramas de la granja. El usuario dice que puede descargarlos en su PC local, pero quiere evitar ese paso y hacerlo dentro del entorno virtual.

## Acceso al escritorio: bloqueo de la conversación anterior

Se aplicó la habilidad `cloud-environment:cloud-desktop`. La herramienta `mcp__cua_repl.js` falló tanto al intentar abrir el proyecto como al consultar el estado, con:

`the gaas-browser node_repl sandbox cannot be disabled`

No se abrió una sesión de SheepIt mediante esa herramienta. Se registró el cierre de ese intento con `completion_summary`; no heredar una supuesta pestaña ni sesión autenticada.

La instancia anterior tenía escritorio remoto habilitado, estado desconocido, y la conexión HTTP a SheepIt devolvía `403 Forbidden / CONNECT tunnel failed`. La política de red aún no incluía SheepIt. **Ese diagnóstico corresponde al entorno anterior.** El usuario ya añadió las URL para el nuevo.

En la conversación nueva:

1. Leer las habilidades de runtime y escritorio disponibles, y consultar el estado de la instancia actual.
2. Usar el navegador compartido y sus herramientas según su documentación. Si existe `open_in_codex`, abrir el escritorio para el usuario.
3. Alternativa de interfaz indicada al usuario: panel derecho → nueva pestaña `+` → `Desktop` → tomar control.
4. Abrir el proyecto de SheepIt y dejar que el usuario inicie sesión. Pausar las acciones del agente durante el control del usuario.
5. Tras devolver el control, comprobar la página y descargar el ZIP dentro del entorno. Si el servidor de descarga usa otro dominio, identificar el dominio real y gestionar su acceso mediante la configuración admitida. No eludir la política de red.
6. No instalar un cliente de render ni aportar cómputo: solo queremos recuperar los resultados.

## GitHub y archivos recuperables

Repositorio: <https://github.com/rising-sunny/c-mo-funciona-YT>

Rama de entrega: `export/differential-sheepit-2026-11-09`.

La escena de SheepIt se publicó inicialmente en el commit:

`57006f55137340b12a7d2a7c3123b75ecee4c935`

Descarga inmutable del `.blend`:

<https://github.com/rising-sunny/c-mo-funciona-YT/raw/57006f55137340b12a7d2a7c3123b75ecee4c935/deliverables/differential/sheepit/The_Physics_Within_Differential_SheepIt.blend>

SHA256 del `.blend` comprimido de SheepIt:

`7817f10b19a9450570cd2f118530c5ab2b29b00759a6338f54e24ec7ba53682a`

### Respaldo para continuar el montaje

Junto a este contexto se entrega `continuation-assets.zip` en la misma rama y carpeta:

<https://github.com/rising-sunny/c-mo-funciona-YT/raw/refs/heads/export/differential-sheepit-2026-11-09/deliverables/differential/sheepit/continuation-assets.zip>

Tamaño: 16.518.635 bytes, aproximadamente 16,5 MB.

SHA256:

`d0fd097ae9061beac72acfaec0f4f6fb991fb813269b642e47bc500acf2ba64d`

Contiene rutas relativas a la raíz del repositorio:

- Scripts actuales del modelo, composición, validación y preparación para SheepIt.
- Escena original editable, antes de adaptar la salida para la granja.
- Narración, mezcla final, música, efectos, subtítulos y transcripción.
- Anclas de cámara, validaciones y tres imágenes de prueba revisadas.
- **Los 1152 JSON con proyecciones de cámara para los diagramas**, guardados como `work/differential/frames/0001.json` hasta `1152.json`.
- `CONTINUATION-MANIFEST.json`, con tamaños y hashes de cada archivo del respaldo.

**No contiene los 1152 PNG de SheepIt**: esos deben descargarse del proyecto. Los JSON son metadatos de proyección, no evidencia de fotogramas renderizados. Se generaron sin efectuar renders nuevos.

Este respaldo evita depender de modificaciones y archivos locales sin versionar que quizá no sobrevivan al cambio de entorno. No asumir que el repositorio base contiene por sí solo el pipeline del diferencial.

## Rutas del último entorno

Raíz del repositorio:

`/workspace/c-mo-funciona-YT`

Entregables y recursos:

`output/differential/`

Scripts y trabajo intermedio:

`work/differential/`

Copia para SheepIt:

`output/differential/sheepit/The_Physics_Within_Differential_SheepIt.blend`

También se dejó una copia en:

`/workspace/shared/downloads/The_Physics_Within_Differential_SheepIt.blend`

Estas rutas deben comprobarse en el nuevo entorno. Si faltan, recuperar desde GitHub y el ZIP de continuación. Extraer en la raíz del repositorio conservando las rutas. Antes de sobrescribir archivos existentes, comparar hashes y preservar cambios que no correspondan al respaldo.

El árbol principal tenía `work/` sin versionar. No ejecutar `git reset --hard`, `git clean` ni limpiar entregables. La rama principal/default del repositorio recuperado era `ccr-fd29bb40-y4p188`; el trabajo de entrega se hizo en un worktree separado.

En el entorno anterior, `gh` no funcionaba con su token, pero `git fetch` y `git push` mediante el entorno sí funcionaban. No mostrar ni pedir credenciales.

## Escena y formato de los resultados

- Blender 4.3.2.
- Vertical nativo **1080 × 1920**.
- **24 fps, fotogramas 1–1152, duración 48 s**.
- Cycles, máximo 96 muestras adaptativas, mínimo 16, umbral 0,035.
- Archivo de SheepIt: PNG RGB de 8 bits, AgX, denoising integrado activado con albedo y normales.
- Materiales procedurales; no hay archivos externos ni scripts necesarios para ejecutar la animación. Las transformaciones están horneadas como keyframes.
- La escena de SheepIt tiene salida relativa `//frames/differential_` y compositor simple de imagen final.
- **El `.blend` genera solo la animación 3D.** Los textos, diagramas, subtítulos y audio se añaden posteriormente con Python y FFmpeg.

En el entorno anterior Blender no tenía OIDN integrado utilizable. Las pruebas locales se procesaron con OIDN externo 2.5.1 y pases reales de normal/albedo. La copia de SheepIt activa denoising integrado para una compilación estándar de Blender; **no aplicar otra pasada de denoising a los PNG de la granja sin comprobar primero si ya están denoised**.

Tres pruebas locales definitivas revisadas: fotogramas 1, 241 y 601. Están en `proof-0001.png`, `proof-0241.png`, `proof-0601.png`. El `poster.png` anterior era una imagen de prueba, no prueba de vídeo final terminado.

El render local quedó cancelado con 14 fotogramas completos, no con 1152. No hay un `video.mp4` final del diferencial. `production-status.json` registra `cancelled_by_user`. No tratar archivos de pruebas o fotogramas antiguos como la entrega completa de la granja.

## Física y animación que se deben conservar

Modelo genérico de diferencial abierto con transmisión final de ejes paralelos, compatible con una disposición transversal. No representa un grupo hipoide longitudinal de un automóvil comercial concreto.

- Corona externa de 48 dientes y piñón de entrada de 12: `ωinput = −4 ωcarrier`.
- Corona y portasatélites forman un mismo cuerpo rígido.
- Planetarios laterales de 24 dientes y satélites de 12; perfiles de involuta esférica aproximados, con holgura deliberada. No son planos de fabricación.
- Para laterales iguales: `ωL + ωR = 2 ωcarrier`.
- Velocidad del portasatélites: 0,60 rad/s.
- En recta: salidas 0,60 / 0,60 rad/s; los satélites orbitan sin girar respecto del portasatélites.
- Transición entre 15 y 19 s a salidas 0,36 / 0,84 rad/s; los satélites ahora también giran sobre el pasador.
- Ruedas de igual radio, rodadura sin deslizamiento; la exterior recorre más distancia.
- Ejemplo final ideal, cuasiestático, sin pérdidas ni inercia: ambos torques de salida son 20 N·m. Potencias: 7,2 W y 16,8 W, usando `P = Tω`.
- Velocidad diferente no implica torque diferente.

La relación de ángulos se comprobó en los 1152 frames. Se comprobaron 56 posiciones para intersecciones de engranajes cónicos, transmisión final y estructuras seleccionadas. Pasaron sin cruces de superficies. Se aumentó el despeje de los puentes del portasatélites y la carcasa de inspección se retira hacia arriba para no atravesar piezas. Estas comprobaciones no equivalen a un cálculo industrial de contacto o resistencia.

## Narrativa y edición ya preparadas

La composición se hace en `work/differential/compose.py`:

1. 0–6 s: vista exterior; por qué dos ruedas necesitan velocidades distintas.
2. 6–13 s: interior; corona/portasatélites y relación de transmisión.
3. 13–21 s: recta y curva; esquema del eje sobre caminos interior/exterior y velocidades de ruedas.
4. 21–29 s: primer plano; distinguir órbita de los satélites y giro relativo sobre el pasador.
5. 29–36 s: suma de velocidades y promedio del portasatélites.
6. 36–42 s: pregunta de pausa: “Does the faster wheel receive more torque?”
7. 42–48 s: igual torque ideal y mayor potencia en la rueda más rápida.

Los puntos se proyectan desde la cámara real con `world_to_camera_view`. El líder del piñón usa además `output/differential/inspection-anchors.json`, exportado del punto real de la escena para la cámara general fija. El resto de anclas vienen de los JSON por fotograma. Las flechas de velocidades y torque son esquemáticas y se indica en pantalla.

No sustituir esto por una secuencia de etiquetas sin explicación física. Mantener unidades, colores, sentidos y las hipótesis del ejemplo final.

## Audio y subtítulos

Recursos ya creados en `output/differential/audio/`:

- `narration.wav`: voz inglesa Kokoro af_bella, 48 s.
- `narration.json`: tiempos reales de las 7 frases sintetizadas; usado por el compositor para subtítulos.
- `mix.wav`: mezcla de voz, música y efectos.
- `quiet-circuit-study.wav`: música ambiental/electrónica original de 48 s.
- `mechanical-effects.wav`: efectos discretos sintetizados.
- `transcript.txt` y `narration.srt`.

Subtítulos de montaje: `output/differential/subtitles.srt`. El compositor dibuja grupos de palabras temporizados dentro de cada frase.

Mezcla verificada: **−16,30 LUFS, −1,49 dBTP**, duración 48 s. Ver `audio-validation.json`. Verificar de nuevo el audio del MP4 codificado, porque AAC puede cambiar el pico.

Música: **Quiet Circuit Study — The Physics Within**, nueva composición ambiental original sin grabaciones, muestras ni citas musicales de terceros. El archivo Quiet Circuit anterior no sobrevivió al entorno recuperado; no afirmar que esta sea aquella pista. El usuario rechazó música con carácter de circo.

No hace falta regenerar la voz: se entrega el audio existente. Para el montaje bastan NumPy, Pillow, soundfile y FFmpeg; los metadatos de proyección ya están exportados. Si se necesita editar o regenerar proyecciones, usar Blender.

## Procedimiento después de descargar el ZIP de SheepIt

1. Confirmar espacio disponible **antes de descargar y extraer**: la captura indicaba 3,4 GB de almacenamiento del proyecto, pero el tamaño real del ZIP y de los resultados todavía no está verificado. Evitar duplicados innecesarios.
2. Inspeccionar el ZIP y sus nombres de archivo antes de extraer. Evitar rutas absolutas, `..`, enlaces y sobrescrituras de archivos ajenos. No asumir el patrón de numeración de SheepIt.
3. Comprobar que hay exactamente los 1152 fotogramas esperados; resolver la numeración real antes de renombrar. No ordenar lexicográficamente si los nombres no llevan ceros.
4. Verificar dimensiones 1080×1920, formato, canales y que no haya imágenes vacías/corruptas. Revisar exterior, marcha recta, transición de curva, primer plano y final; comparar visualmente con las pruebas locales.
5. Normalizar los PNG como `work/differential/frames/0001.png` a `1152.png`. El respaldo incluye los JSON correctos al lado. Si ya existen los 14 PNG de pruebas locales, preservarlos aparte para que no se mezclen con los de SheepIt.
6. Confirmar que los scripts usan la raíz correcta. Están preparados para `/workspace/c-mo-funciona-YT`; si se restauró en otra ruta, adaptar `ROOT` y las rutas absolutas de forma consistente.
7. Ejecutar desde la raíz del repositorio:

   ```bash
   .venv/bin/python work/differential/compose.py
   ```

   No ejecutar los scripts del render cancelado. `compose.py` no renderiza 3D: añade overlays y subtítulos a los PNG, prepara la mezcla y codifica el MP4 con FFmpeg.

8. El compositor produce `output/differential/video.mp4`, `poster.png`, `subtitles.srt`, `final-validation.json` y `SHA256SUMS.txt`. Comprobar los archivos reales; no asumir éxito solo por existir un archivo de estado viejo.
9. Validación esperada: decodificación completa sin errores, 1080×1920, 24 fps, 1152 frames, duración cercana a 48 s; audio aproximadamente −16 LUFS y pico verdadero ≤−1 dBTP. Revisar además sincronización y claridad visual del vídeo real.
10. Entregar vídeo y escena editables por el mecanismo disponible. No publicar el vídeo. La entrega mediante GitHub ya fue autorizada para los archivos de este trabajo; mantener los anteriores intactos.

## Conservación e historial

El entorno recuperado al inicio contenía una versión anterior del repositorio: episodios de tornillo de banco, jeringas hidráulicas y timbre. No aparecían la catapulta v2, el episodio de freno, Quiet Circuit anterior ni el OIDN externo descritos en el primer traspaso. No se recrearon ni sustituyeron esos episodios.

No afirmar que todo el historial local esté en GitHub. El respaldo adjunto cubre la continuación del diferencial, no los trabajos anteriores que faltaban.

El directorio de entregables requerido por el sistema de chat (`/codex/browser/projectless/.../output`) no existía ni era escribible en la instancia anterior. No se pudo adjuntar directamente un archivo desde allí, por eso se acordó usar GitHub. En la nueva instancia comprobar las capacidades actuales y no inventar enlaces locales de descarga.

## Primer mensaje recomendado al retomar

“Voy a comprobar el entorno nuevo y abrir tu proyecto de SheepIt en el navegador compartido. Tú iniciarás sesión; después descargaré los fotogramas aquí y continuaré el montaje, sin volver a renderizar.”

No pedir que el usuario repita este contexto ni que comparta credenciales. Si el navegador o la descarga siguen bloqueados, reportar el error concreto de la nueva instancia y la acción necesaria para resolverlo.
