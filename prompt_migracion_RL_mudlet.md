# Tarea: Migración de ScriptsRL de VipMUD a Mudlet con accesibilidad NVDA

## Contexto del proyecto

Eres un experto en Lua, Mudlet, accesibilidad con lectores de pantalla (especialmente NVDA en
Windows) y MUDs de texto.

Se te pide migrar un paquete de scripts maduro para el MUD "Reinos de Leyenda"
(rlmud.org / reinosdeleyenda.es) desde el cliente VipMUD al cliente Mudlet, generando un paquete
`.mpackage` completamente funcional, con accesibilidad como prioridad de diseño, no como añadido
posterior.

El repositorio original ya está descargado en este directorio de trabajo bajo la carpeta
`ScriptsRL/`. Empieza siempre leyendo ese directorio y todos sus archivos antes de hacer nada.

---

## Antes de escribir código: haz un plan

**Tu primer paso obligatorio es producir un documento `PLAN_MIGRACION.md`** en el directorio de
trabajo con:

1. **Inventario completo** de todos los archivos fuente que encontraste, qué hace cada uno y qué
   categoría de funcionalidad cubre (navegación, combate, estadísticas, inventario, sonidos,
   atajos de teclado, etc.).
2. **Tabla de equivalencias** VipMUD → Mudlet: para cada construcción de VipMUD que encuentres
   (`#GKey`, `#GAlias`, `#GAliasC`, `#Say`, `#Play`, `#Trigger`, `#var`, `%lastline`, `#find`,
   `#prompt`, `#if`, `#wait`, `#pc`, `#PlayLoop`, etc.), documenta cómo se traducirá en
   Mudlet/Lua.
3. **Decisiones de diseño de accesibilidad**: qué datos se almacenarán en buffers virtuales
   navegables, qué atajos de teclado se usarán, cómo se leerá la información con `readText()`.
4. **Lista priorizada de módulos** a implementar, del más crítico al menos crítico.
5. **Riesgos y ambigüedades** que hayas detectado en los scripts originales y cómo piensas
   resolverlos.
6. **Estructura de archivos** del paquete Mudlet que vas a crear.

**No escribas código Lua hasta que el plan esté completo.** Cuando termines el plan, indícalo
claramente y espera confirmación para continuar, o continúa directamente si estás en modo
autónomo.

---

## Documentación que debes consultar activamente

Cuando tengas dudas sobre la API de Mudlet, consulta estas fuentes antes de inventarte nada:

- **API Lua de Mudlet**: https://wiki.mudlet.org/w/Manual:Lua_Functions
- **Scripting en Mudlet**: https://wiki.mudlet.org/w/Manual:Scripting
- **Accesibilidad y lectores de pantalla**: https://wiki.mudlet.org/w/Manual:Screen_Readers
  y https://wiki.mudlet.org/w/Accessibility_On_Windows
- **Paquetes de Mudlet**: https://wiki.mudlet.org/w/Manual:Mudlet_Packages
- **Geyser (framework GUI)**: https://wiki.mudlet.org/w/Manual:Geyser

También puedes consultar estos repositorios de referencia para patrones de accesibilidad en
Mudlet:

- https://github.com/ironcross32/ChannelHistory — patrón de buffer virtual para ciegos, muy
  relevante, vale la pena leer su código fuente completo como plantilla.

Como referencia adicional de cómo otros han resuelto triggers para el mismo juego (Reinos de
Leyenda) en otro cliente, puedes consultar:

- https://github.com/francipvb/RLMush — scripts para MUSHclient para RL, útil para entender
  patrones del output del juego.

---

## Requisitos de accesibilidad — esto es fundamental

El paquete resultante debe ser **jugable por completo por una persona ciega usando NVDA en
Windows**, sin necesidad de ver la pantalla en ningún momento. Esto no es opcional.

### Configuración de accesibilidad en la inicialización del paquete

**El paquete debe aplicar directamente las configuraciones de accesibilidad necesarias al
cargarse**, sin depender del alias `mudlet access` para eso. En el script `init.lua`, incluye:

```lua
-- Configuraciones de accesibilidad aplicadas automáticamente al instalar el paquete
setConfig("blankLinesBehaviour", "hide") -- evita que NVDA repita líneas en blanco vacías
-- Consulta Manual:Screen_Readers para cualquier otra opción de setConfig relevante
-- y añádelas aquí
```

**No declares como dependencia el paquete genérico de Virtual Buffer del repositorio oficial de
Mudlet.** Este paquete implementa su propio sistema de buffers específico para RL, que lo
reemplaza con una solución mejor adaptada al juego. Sí puedes declarar como dependencia el
paquete Reader si lo consideras útil como complemento, pero no es obligatorio.

**Documenta en el README, como paso 1 de la instalación** (antes de importar el `.mpackage`),
que el usuario debe ejecutar una vez en Mudlet el comando:

```
mudlet access
```

Esto configura opciones del cliente (como `Ctrl+Tab` para cambiar el foco entre ventana de
entrada y salida) que no son accesibles desde Lua y que son esenciales para la experiencia con
NVDA.

### Principios de diseño accesible para este paquete

**1. `readText()` como canal principal de información**
Usa la función nativa `readText("texto")` de Mudlet para anunciar eventos importantes
directamente al lector de pantalla. No dependas solo de que NVDA lea el scroll de la ventana
principal, porque en partidas con mucho texto eso es inmanejable.

**2. Buffers virtuales para listas e información estructurada**
Cuando el juego devuelva una lista (inventario, contenido de baúl, objetos en sala, hechizos
activos, enemigos en sala, etc.), NO muestres la lista solo en una ventana visual. En su lugar:

- Captura cada línea de la respuesta con un trigger multilínea o con un estado de captura
  (`capturando = true/false`).
- Almacena los ítems en una tabla Lua indexada: `RL.buffers.inventario = {}`,
  `RL.buffers.enemigos = {}`, etc.
- Añade navegación con atajos de teclado: flechas+modificador para moverse por el buffer,
  anunciando cada ítem con `readText()`.
- Sigue el patrón de ChannelHistory: navegar entre categorías con `Alt+izquierda/derecha`,
  navegar ítems con `Alt+arriba/abajo`, ir al primero/último con `Alt+Inicio/Fin`.

**3. Atajos de teclado para datos de estado rápido**
El usuario necesita poder consultar sus estadísticas en cualquier momento sin interrumpir el flujo
de juego. Implementa atajos que lean en voz alta con `readText()`:

- Stats de combate (PVs, maná/energía, stamina, porcentajes, etc.) — mapea desde los atajos
  equivalentes que había en VipMUD.
- Último enemigo que entró en la sala.
- Estado actual del personaje (posición, efectos activos si los hay).
- Adapta los atajos originales de VipMUD si tienen sentido, o propón nuevos si los originales
  entran en conflicto con los atajos nativos de NVDA. Ten en cuenta que NVDA usa `Insert` como
  tecla modificadora principal y ocupa muchas combinaciones con el numpad, así que evita esas
  zonas del teclado para los atajos del paquete.

**4. Captura de prompt/estadísticas en tiempo real**
Si el juego envía un prompt con PVs, energía u otros stats (como `[PVs: 450/500 | Mana: 200/300]`
o similar), captúralo con un trigger y almacena los valores en variables Lua dentro del namespace
del paquete (`RL.stats.pvs`, `RL.stats.pvs_max`, etc.) para que los atajos de lectura rápida
siempre tengan datos frescos.

**5. Feedback de sonido**
Mudlet tiene una API de audio completa. Mantén los sonidos del paquete original donde tengan
sentido (los `.wav` en `sounds/RL/`). Usa `playSoundFile()` para alertas críticas (bajo de PVs,
ser atacado, recibir mensaje privado, etc.). El sonido complementa al lector, no lo reemplaza.

**6. Confirmaciones habladas para acciones**
Cuando el usuario ejecute un alias o macro importante (activar/desactivar modo combate, cambiar
objetivo, usar habilidad), confirma la acción con `readText()` además de enviar el comando al
MUD. Ejemplo: `readText("Objetivo cambiado a " .. objetivo)`.

**7. No crear ventanas visuales sin alternativa accesible**
Si decides crear algún elemento de UI visual con Geyser (gauge de PVs, minimap, etc.) para
usuarios videntes, asegúrate de que toda esa información tenga también su equivalente en atajos
de teclado + `readText()`. Las ventanas Geyser son opacas para NVDA.

---

## Mapeo de conceptos VipMUD → Mudlet

Úsalo como guía, no como regla rígida. Si encuentras una mejor forma de hacer algo en Mudlet,
hazla:

| VipMUD                              | Mudlet / Lua                                                                 |
|-------------------------------------|------------------------------------------------------------------------------|
| `#GKey tecla {acción}`              | Key Binding con código Lua                                                   |
| `#GAlias nombre {código}`           | Alias con código Lua                                                         |
| `#Say texto NoDisplay\|Output`      | `readText("texto")`                                                          |
| `#Say texto` (sin NoDisplay)        | `echo("texto\n")` o dejar que el MUD lo muestre                              |
| `#Play archivo.wav`                 | `playSoundFile(getMudletHomeDir().."/ScriptsRL/sounds/RL/archivo.wav")`      |
| `#PlayLoop archivo.wav volumen`     | `playMusicFile(...)` con loop                                                |
| `#pc %mp3loop stop`                 | `stopMusic()`                                                                |
| `#Trigger patron {código}`          | Trigger con patrón regex y código Lua                                        |
| `#var nombre valor`                 | Variable Lua en el namespace: `RL.vars.nombre = valor`                       |
| `%lastline(N)`                      | Buffer circular de últimas N líneas, actualizado con trigger por línea       |
| `#find patron FIRST\|Reverse`       | Búsqueda sobre tabla Lua del buffer, navegada con atajos de teclado          |
| `#prompt variable {texto}`          | `RL.utils.prompt(texto, callback)` — implementar con variable de estado      |
| `#wait N`                           | `tempTimer(N/1000, function() ... end)`                                      |
| `#if {cond} {then} {else}`          | `if cond then ... else ... end` en Lua                                       |
| `#ClipBoard texto`                  | `setClipboardText(texto)` si existe, o alternativa via utilidades del SO     |
| `%charInfo(name/password)`          | Variables en `RL.config.nombre` / `RL.config.password`, en archivo local    |
| `#dir n s`                          | Definición de salidas opuestas — ignorar o usar para el mapper de Mudlet     |
| `#autoMenu path`                    | Reimplementar la funcionalidad específica según lo que haga                  |
| `#window output`                    | `setFocus("main")` o documentar el atajo `Ctrl+Tab` de NVDA                 |
| Control de volumen SAPI             | `RL.sounds.setVolume(n)` + `setMusicVolume()` / `setSoundVolume()`          |

---

## Estructura del paquete a crear

Organiza el código en módulos coherentes. Como mínimo:

```
RL-Mudlet/
├── src/
│   ├── core/
│   │   ├── init.lua          -- Inicialización, carga de módulos, config accesibilidad
│   │   ├── config.lua        -- Variables de configuración del usuario
│   │   └── utils.lua         -- Funciones de utilidad compartidas
│   ├── accessibility/
│   │   ├── buffers.lua       -- Sistema de buffers virtuales navegables
│   │   ├── keybindings.lua   -- Todos los atajos de teclado accesibles
│   │   └── tts.lua           -- Funciones wrapper de readText con lógica de prioridad
│   ├── game/
│   │   ├── stats.lua         -- Captura y lectura de estadísticas del personaje
│   │   ├── combat.lua        -- Triggers y lógica de combate
│   │   ├── inventory.lua     -- Captura de inventario/baúl a buffer
│   │   ├── navigation.lua    -- Aliases de movimiento y exploración
│   │   └── [otros módulos según lo que encuentres en el repo original]
│   ├── triggers/
│   │   └── [triggers organizados por categoría]
│   └── sounds.lua            -- Gestión centralizada de sonidos
├── sounds/                   -- Copiar los .wav del repo original aquí
├── README.md                 -- Instrucciones de instalación, uso y setup NVDA
├── ATAJOS.md                 -- Referencia rápida de todos los atajos del paquete
└── PLAN_MIGRACION.md         -- El plan que generaste al principio
```

Empaqueta todo como un `.mpackage` válido al final (es un ZIP con estructura XML de Mudlet).
Consulta `https://wiki.mudlet.org/w/Manual:Mudlet_Packages` para el formato exacto.

---

## Estilo de código Lua

- Usa un namespace global `RL` para todo: `RL.stats`, `RL.buffers`, `RL.config`, `RL.sounds`,
  etc. Nunca variables globales sueltas que puedan colisionar con Mudlet u otros paquetes.
- Comenta en español, dado que el proyecto es hispanohablante.
- Documenta cada función con su propósito, parámetros y lo que devuelve.
- Cuando un trigger capture datos del juego, hazlo robusto: contempla variaciones de color ANSI
  (usa `string.gsub` para limpiarlos si es necesario) y variaciones de espaciado.
- Prefiere patrones regex bien testeados sobre substring matching cuando el output del MUD sea
  predecible.
- Gestiona errores con `pcall` en operaciones que puedan fallar, y usa `readText()` para avisar
  al usuario de errores en lugar de fallar silenciosamente.

---

## Sobre los sonidos

El repo incluye archivos `.wav` en `sounds/RL/`. Inclúyelos en el paquete. Al instalar, los
sonidos deben quedar en `getMudletHomeDir() .. "/ScriptsRL/sounds/RL/"`. Crea una función
`RL.sounds.play(nombre)` que construya la ruta automáticamente y gestione errores si el archivo
no existe.

Para los sonidos de música/tema que en VipMUD usaban `#PlayLoop`, usa la API `playMusicFile()`
de Mudlet con el parámetro de loop correspondiente.

---

## Qué NO hacer

- No uses `print()` para información al usuario. Usa `readText()` para cosas que el ciego
  necesita oír, o `cecho()` / `echo()` para cosas que van al buffer de texto visible.
- No crees gauges visuales, mapas ni ventanas Geyser sin proporcionar también su alternativa de
  teclado + `readText()`. Si hay que priorizar, la alternativa de teclado va primero.
- No hardcodees rutas de archivo con barras invertidas de Windows. Usa siempre
  `getMudletHomeDir()` y barras `/`.
- No rompas los atajos nativos de NVDA. Evita combinaciones con `Insert`, las teclas de numpad
  sin Bloq.Num activo, y `Alt+F4`.
- No generes código Lua que dependa de versiones de Mudlet anteriores a la 4.17.

---

## Entregables finales

1. `PLAN_MIGRACION.md` — inventario completo, tabla de equivalencias, decisiones de diseño.
2. Código Lua organizado en módulos dentro de `src/`.
3. El paquete empaquetado como `ScriptsRL.mpackage`, listo para instalar en Mudlet.
4. `README.md` en español con:
   - Paso 1: ejecutar `mudlet access` en Mudlet antes de instalar.
   - Paso 2: instalar el `.mpackage`.
   - Configuración recomendada de NVDA (activar "Simple review mode" en opciones → review
     cursor, crear perfil de configuración específico para Mudlet).
   - Referencia completa de todos los atajos de teclado del paquete.
5. `ATAJOS.md` — referencia rápida de atajos, imprimible.

---

## Tono de trabajo

Sé pragmático. Si encuentras algo en el repo original que no tiene sentido directo en Mudlet,
adáptalo con criterio y documenta la decisión en el plan. Si hay funcionalidades que en VipMUD
eran workarounds de limitaciones del cliente y en Mudlet hay una forma nativa mejor, usa la forma
mejor.

El objetivo no es una traducción literal sino un paquete que funcione bien en Mudlet y sea
completamente accesible. Si detectas ambigüedades sobre cómo funciona algo en el juego, márcalo
como "necesita verificación con el MUD real" en el plan, pero implementa una versión razonable
basada en lo que hayas deducido del código original.

**Empieza ya: lee el directorio `ScriptsRL/`, analiza todos los archivos, y produce el
`PLAN_MIGRACION.md`.**
