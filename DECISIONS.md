# Estado del proyecto — 2026-11-04

- Canal nuevo: mecanismos cotidianos en 3D, visuales producidos por código.
- Primer piloto confirmado: tornillo de banco.
- Idioma confirmado: inglés. Voz pendiente; primera prueba con textos.
- Canal de YouTube todavía no creado; ID y OAuth pendientes.
- Proyecto independiente de `/workspace/Mathrelaxing-youtube`.
- Blender 4.3.2 + FFmpeg 7.1.5 disponibles; sin instalación adicional.
- Generación, montaje y validación locales implementados para un mecanismo.
- Adaptador de subida preparado; ensayo local probado, API real sin probar.
- No se subió ni publicó ningún vídeo. No se configuraron tareas programadas.
- Primera entrega: prueba técnica de 12 s, 270×480, 8 fps, sin sonido.
- Siguiente revisión: composición, claridad del tornillo/flecha y explicación física.
- Antes de producción: contrastar modelo con fuentes técnicas, mejorar guion y
  presentación, decidir audio y revisar render final.
- Antes de conectar YouTube: crear canal, configurar red y OAuth del canal nuevo.

## Revisión visual 2

- Usuario pidió pulir el mecanismo y añadir escenas de acercamiento y detalle.
- Modelo mejorado: cuerpo de fundición, base giratoria atornillada, yunque,
  caras de agarre con ranuras y tornillos, manivela con extremos redondeados.
- Secuencia de cinco planos de 22 s: general, corte de rosca/tuerca, manivela,
  mordazas y general final. Textos en inglés; sin audio.
- Preview actual: 450×800, 12 fps. Primer vídeo conservado en archive-v1.
- Movimiento único continuo: 16 mm en 4 vueltas, primer contacto en t=19 s.
- Radio de manivela corregido a 65 mm para dejar espacio físico sobre la base;
  20 N perpendiculares corresponden a 1.3 N m, en el modelo ideal.
- Seis pruebas locales y comprobación del artefacto Blender: contacto sin
  penetración, continuidad de avance, cámaras y visibilidad del corte.
- No se ha conectado, subido ni publicado nada en YouTube.

## Revisión visual 3

- Usuario pidió seguir agregando detalles y acercamientos más dinámicos.
- Seis planos: general, placa de agarre aislada, rosca/tuerca, manivela,
  cierre de mordazas y general de salida.
- Cámaras en perspectiva de 50 mm con órbita, acercamiento/alejamiento y
  seguimiento del punto de interés; arranque y frenado suaves.
- Acercamientos de hasta un tercio del encuadre inicial, con cambio de ángulo.
- Geometría nueva: estriado cruzado, ranuras de tornillos, nervaduras,
  placa de identificación en relieve y anillos de cojinete.
- Se mantiene la cinemática anterior: avance total 16 mm, contacto en t=19 s.
- Duración 22 s; previsualización 450×800 a 16 fps; inglés, sin voz.
- Revisión 2 conservada en archive-v2 y en su archivo bench_vise_v2.mp4.
- Verificación de la escena: contacto sin penetración, cámaras en perspectiva
  con desplazamiento real y visibilidad correcta de los detalles aislados.
- Sin cambios en la conexión o publicación a YouTube.

## Revisión 4: narración, subtítulos y fórmulas

- Usuario autorizó empezar con subtítulos y narración; se mantiene el inglés.
- Usuario pidió expresiones matemáticas físicas en los momentos relevantes.
- Primera voz: sintética femenina estadounidense, modelo LJSpeech/Piper vía
  sherpa-onnx, síntesis local y dependencias aisladas en .venv.
- Seis frases ajustadas a los planos a velocidad natural; cues SRT medidos a
  partir de la duración real de cada archivo de voz.
- MP4 con AAC, subtítulos visibles y pista inglesa seleccionable; SRT y WAV aparte.
- Fórmulas de avance, torque perpendicular y recorrido total, con variables,
  unidades y ejemplos consistentes con los parámetros actuales.
- Se reutilizan los 352 fotogramas de la versión 3; no cambia su geometría.
- Prueba física de materiales e iluminación separada en Cycles: dos imágenes,
  pintura, metal, luces de área y banco de madera procedural.
- No se ha migrado todavía todo el vídeo al render físico ni añadido música.
- Revisión 3 conservada. Sin subida o publicación a YouTube.

## Revisión 5

- Usuario pidió mejorar flechas, una voz más dinámica/divertida y subtítulos
  del estilo de Shorts virales; luego indicó continuar.
- Flechas híbridas: anclajes y planos calculados por Blender, dibujo 2D
  antialias con grosor constante y etiquetas legibles.
- Fuerza turquesa, torque ámbar, radio gris discontinuo; magnitudes del modelo
  sin cambios y longitud de fuerza expresamente esquemática.
- Voz Kokoro af_bella con guion conversacional, pausas y contacto en t=19 s.
- Subtítulos grandes, bloques cortos, contorno y resaltado amarillo.
- Resaltado por palabra aproximado dentro de las frases medidas; no es una
  alineación forzada palabra/audio. La pista SRT conserva las frases exactas.
- Vídeo de 22 s, 450×800, 16 fps. Revisión 4 y sus audios conservados.
- Sin publicaciones ni cambios de canal. La prueba Cycles sigue separada.

## Revisión 6: música y render completo a 60 fps

- Usuario pidió buscar música de fondo en la web y generar el Short a 60 fps.
- Se consultaron archivos públicos de GitHub y los créditos de las demos oficiales
  de Godot, con pistas y licencias explícitas.
- Elegida Monkeys Spinning Monkeys, Kevin MacLeod, CC BY 3.0 según esos créditos.
- Guardados audio, evidencia de licencia, atribución y hash en assets/music.
- Créditos añadidos a la descripción; mezcla con bajada automática bajo la voz.
- Exportación final vertical 1080×1920 a 60 fps, 22 s: 1320 fotogramas nativos.
- Se mantiene el acabado Workbench de la revisión aceptada; estudio Cycles aparte.
- Subtítulos, proyección de flechas y cámara adaptados al perfil final.
- Publicación y conexión al canal continúan pendientes; no se ha subido nada.

## Identidad del canal

- Nombre confirmado por el usuario: The Physics Within.
- Usuario pidió banner y perfil con apariencia de diseño gráfico sobrio,
  evitando una estética reconocible de ilustración generada por IA.
- Primera propuesta vectorial en branding/the-physics-within/: azul tinta,
  blanco cálido y dorado; Nimbus Sans; símbolo de corte con núcleo interior.
- Banner 2560×1440 con contenido esencial dentro de 1546×423 centrados.
- Perfil PNG 1024×1024 y SVG editables con letras convertidas en contornos.
- Frase propuesta: See what makes the world work.
- Se entregan archivos; no se ha cambiado ni subido nada al canal.

## Adaptación a Facebook

- Usuario pidió portada y perfil para su nueva página de Facebook.
- Se conserva la identidad The Physics Within y el mismo símbolo de perfil.
- Portada 1640×720 con nombre y frase protegidos frente a recortes centrados
  habituales de escritorio/móvil y evitando la zona inferior del avatar.
- PNG listos para subir, SVG y kit ZIP en branding/the-physics-within/facebook.
- Las vistas de dispositivo son aproximadas; no se ha modificado Facebook.

## Episodio 2: jeringas hidráulicas

- Usuario confirmó la propuesta de jeringas hidráulicas para el segundo Short.
- Dos cuerpos con corte visible, líquido y tubo cerrado, émbolos acoplados y carga.
- Áreas 5 y 20 cm², fuerzas ideales 10 y 40 N, recorridos 80 y 20 mm.
- Se conservan volumen desplazado (40 mL) y trabajo ideal (0.8 J).
- Hipótesis explícitas: sin aire, fricción, fugas ni efectos de altura.
- Modelo contrastado con OpenStax, Pascal’s Principle, módulo m42193.
- Siete planos, 28 segundos, inglés, voz Kokoro y subtítulos cortos; 1080p60.
- Mismo estilo de flechas planas y música con créditos y bajada bajo la voz.
- Se corrigió una regresión en la agrupación de subtítulos con palabras finales
  aisladas; se añadieron pruebas del modelo hidráulico y de subtítulos.
- No se ha subido ni publicado el episodio.

- Episodio 2 terminado: 1680 fotogramas nativos, audio estéreo, SRT y overlays verificados; copia final en deliverables/hydraulic-syringes.

## Episodio 3: timbre electromagnético

- Usuario aprobó un timbre clásico con contacto auto-interruptor.
- Ocho planos, 30 s, inglés y 1080p60 nativos; narración y subtítulos de la serie.
- Modelo acoplado de corriente inductiva, armadura, resorte, contacto y golpe.
- Secuencia revisada: la corriente no desaparece instantáneamente al abrir.
- El golpe conserva inercia tras el corte; el resorte permite volver a cerrar.
- Usuario reiteró que las flechas no deben formar parte del render 3D.
- Se eliminaron también las líneas de campo de la escena: fuerzas, campo,
  corriente y llamadas se dibujan en capas 2D transparentes independientes.
- La escena guardada se verifica para asegurar que no contiene mallas de anotación.
- Modelo ilustrativo, no calibrado con un timbre comercial; tiempos ampliados,
  contacto y descarga inductiva simplificados, hipótesis documentadas.
- Sonidos originales sintetizados y alineados a nueve impactos mostrados.
- No se ha publicado en YouTube ni Facebook.

- Episodio 3 terminado y verificado: 1800 fotogramas nativos, ocho frases, nueve golpes sincronizados y gráficos 2D independientes; entregable en deliverables/electric-bell.
