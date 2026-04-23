# Scripts - Referencia Rápida

Esta carpeta contiene todos los scripts de configuración y sonidos para el cliente VipMud en Reinos de Leyenda. Este documento sirve como **índice de referencia rápida** para no tener que explorar constantemente la carpeta.

## Estructura General

```
Scripts/
├── Reinos de leyenda/          # Carpeta principal del juego
│   ├── ScripsRL/               # Scripts del juego
│   └── Reinos de leyenda.set   # Archivo principal de carga
├── sounds/                     # Archivos de sonido (.wav)
├── VipMud.set                  # Configuración principal del cliente
├── start.set                   # Configuración de inicio
└── speech.ini                  # Configuración de síntesis de voz
```

---

## Archivos Principales (Root de Scripts/)

| Archivo | Propósito | Editar? |
|---------|-----------|---------|
| `VipMud.set` | Configuración global del cliente VipMud | ⚠️ Con cuidado |
| `start.set` | Script de inicio al conectar | ⚠️ Con cuidado |
| `speech.ini` | Configuración de voz/lector de pantalla | ⚠️ Con cuidado |
| `Reinos de leyenda.set` | Loader principal del juego (dentro de carpeta) | ⚠️ Con cuidado |

**Regla:** No modificar estos archivos directamente. Crear nuevos `.set` en `ScripsRL/` e importarlos con `#Load`.

---

## Estructura de `Reinos de leyenda/ScripsRL/`

### Core Scripts (Sistema Principal)

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `Alias_Macros.set` | Alias, macros, keybindings | Referencia para ver qué está mapeado |
| `Configuracion.set` | Configuración general del sistema | Alteraciones globales |
| `Generales.set` | Funciones y comportamientos generales | Consultar para patrones comunes |
| `Funciones.set` | Utilidades y helpers | Buscar funciones disponibles |
| `Combate.set` | Sistema de combate | Modificar mecánicas de combate |
| `Comunicaciones.set` | Canales, telepátia, chat | Triggers de mensajes |
| `Movimiento_propio.set` | Movimiento del personaje | Triggers de movimiento personal |
| `Movimiento_otros.set` | Detección de otros moviendo | Triggers de alertas de movimiento |
| `Movimiento_keys.set` | Keybindings de movimiento | Reasignar teclas de movimiento |
| `Modos.set` | Toggles de juego (XP, Expert, Idle, etc.) | Cambiar comportamiento de modos |
| `Estados.set` | Estados del personaje | Tracking de estado |
| `Stats.set` | Estadísticas | Monitoreo de stats |
| `Nicks.set` | Configuración de enemigos/aliados | Añadir enemigos, cambiar nicks |
| `Listas.set` | Listas de items, NPCs | Mantenimiento de listas |
| `Bloqueos.set` | Cooldowns, bloqueos de habilidades | Configurar timers |
| `Sucesos.set` | Event handlers | Triggers de eventos especiales |

### Categorías Temáticas

| Carpeta | Contenido | Cuándo Editar |
|---------|-----------|---------------|
| `Clases/` | Scripts específicos por clase (Soldados, Khazads, etc.) | Crear nueva clase o modificar existente |
| `Paths/` | Rutas de navegación por ciudades | Añadir/actualizar rutas |
| `Ambientacion/` | Scripts por región (Anduar, Dendra, Takome, etc.) | Modificar eventos regionales |
| `Oficios/` | Trades/profesiones (Minero, Herrero, Marinero) | Ajustar trades o profesiones |
| `Doc/` | Documentación (txt) | Consultar, no editar (información histórica) |

---

## Carpeta `Clases/`

**Propósito:** Scripts específicos de cada clase de personaje.

**Clases Soportadas:**
- `Soldados.set` — Combate físico estándar
- `Khazads.set` — Clase Khazad
- `Exploradores.set` — Exploradores con sigilo
- `Guardabosques.set` — Guardabosques
- `Tiradores.set` — Arqueros/tiradores
- `Cazadores.set` — Cazadores
- `Paladines.set` — Paladines
- `Antipaladines.set` — Antipaladines
- `Bardos.set` — Bardos
- `Monjes.set` — Monjes
- `Sigiladores.set` — Base para clases sigiladas
- `Centrar.set` — Habilidad "centrar" (compartida)
- `Combate_fisico.set` — Template para combate físico genérico
- `Magia_arcana.set` — Magia arcana
- `Magia_clerical.set` — Magia clerical
- `Yver.set`, `Gragbadur.set`, `Khaol.set` — Clases especiales

**Patrón de uso:**
1. En archivo de personaje (`nombredelPJ.set`), añadir:
   ```
   #Load ScripsRL\Clases\Soldados.set
   ```
2. Si clase no existe, usar template:
   ```
   #Load ScripsRL\Clases\Combate_fisico.set
   ```
3. Si tiene habilidad "centrar":
   ```
   #Load ScripsRL\Clases\Centrar.set
   ```

---

## Carpeta `Paths/`

**Propósito:** Rutas de navegación preestablecidas entre ciudades/ubicaciones.

**Ubicaciones Disponibles:**
- `Takome.set`, `Takome2.set` — Rutas desde Takome
- `Eldor.set` — Rutas desde Eldor
- `Golthur.set`, `Golthur2.set` — Rutas desde Golthur
- `Kheleb.set` — Rutas desde Kheleb
- `Anduar.set` — Rutas desde Anduar
- `Dendra.set`, `Dendra2.set` — Rutas desde Dendra
- `Naggrung.set` — Rutas desde Naggrung
- `Veleiron.set` — Rutas desde Veleiron
- `Url om.set` — Rutas desde Urlom
- `Eloras.set` — Rutas desde Eloras
- `Zulk.set` — Rutas desde Zulk
- `MG.set` — Rutas especiales

**Cómo funcionan:**
- Jugador en ciudad oye sonido "Path disponible.wav"
- Presiona `Ctrl+Shift+M` para ver destinos disponibles
- Selecciona destino y navegación automática

**Para añadir un path:**
1. Crear archivo en `Paths/` con nombre de ciudad origen
2. Definir secuencia de movimientos (norte, sur, este, oeste, etc.)
3. Actualizar configurador de paths principal

---

## Carpeta `Ambientacion/`

**Propósito:** Scripts específicos de cada región/reino.

**Regiones Disponibles:**
- `Anduar.set` — Región de Anduar
- `Dendra.set` — Región de Dendra
- `Takome.set` — Región de Takome
- `Grimoszk.set` — Región de Grimoszk
- `Asignacion.set` — Asignaciones por región
- `Generales.set` — Eventos ambientales globales

**Contenido típico:**
- Descripciones de habitaciones
- Triggers de eventos especiales
- Encuentros únicos por región
- Avisos de peligro regionales

---

## Carpeta `Oficios/`

**Propósito:** Scripts de profesiones/trades.

**Trades Disponibles:**
- `Minero.set` — Minería
- `Herrero.set` — Herrería
- `Marinero.set` — Profesión marina
- `Jornalero.set` — Jornalero
- `Crear.set` — Crafting/creación
- `Oficios.set` — Base de oficios

**Estructura:**
- Cada trade tiene keybindings específicos
- Triggers para progreso/éxito
- Sonidos de confirmación

---

## Carpeta `sounds/RL/`

**Propósito:** Archivos de sonido (.wav) para eventos del juego.

**Categorías de Sonidos:**
```
sounds/RL/
├── Combate/           # Sonidos de combate (hits, escudos, bloqueos)
├── Movimiento/        # Sonidos de movimiento (caminar, entrar, salir)
├── Items/             # Sonidos de items (equipo, botín)
├── Hechizos/          # Sonidos de magia
├── Eventos/           # Sonidos de eventos especiales
├── Comunicaciones/    # Sonidos de chat/mensajes
├── Avisos/            # Alertas (peligro, logro)
└── Ambiente/          # Sonidos de ambiente
```

**Cuándo Consultar:**
- Necesitas añadir sonido a un evento → Mira qué sonidos existen
- Configurar trigger de sonido → Busca archivo `.wav` correspondiente
- Crear nueva clase → Necesitarás sonidos para sus habilidades

---

## Configuración de Personaje

**Para nuevo personaje:**

1. **Crear archivo** → `Reinos de leyenda/[NombreDelPersonaje].set`
   ```
   nombredelPersonaje
   #Load ScripsRL\Clases\Soldados.set
   ```

2. **Configurar en juego:**
   ```
   configurarficha            (setup básico)
   configurarpromptb          (si no puede matar aliados)
   configurarprompta          (si puede matar todos)
   configurarpromptx          (control manual de nicks)
   ```

3. **Agregar suffix si es necesario:**
   ```
   configurarpromptbm         (si tiene pieles de piedra/imágenes)
   configurarpromptam         (variante para otros bandos)
   ```

---

## Alias Importantes (En Juego)

| Alias | Acción |
|-------|--------|
| `configurarficha` | Setup inicial del personaje |
| `canalescolores` | Crea aliases para canales con colores |
| `versionscrips` | Muestra versión de los scripts |
| `mac` | Toggle modo autocentrar |
| `repb` | Reportar por bando |
| `repd` | Reportar mediante decir |
| `rept` | Reportar por telepátia |
| `repc` | Reportar por ciudadanía |
| `obj [nombre]` | Cambiar objetivo prioritario |

---

## Keybindings Globales

| Tecla | Acción |
|-------|--------|
| `F7` | Toggle autocentrar (si tiene "centrar") |
| `F10` | Toggle modo experto |
| `F11` | Cambiar modo juego (Original → Combat → XP → Idle) |
| `F12` | Toggle lectura automática de texto |
| `Ctrl+Shift+R` | Recargar todos los scripts |
| `Ctrl+Shift+M` | Ver paths disponibles |
| `Ctrl+G` | Ver miembros del grupo |
| `Ctrl+T` | Ver lista de telepátias |
| `Alt+0-9` | Leer últimos X cambios en PV |
| `Alt+1` | Consultar PV actual/máximo |
| `Alt+2` | Consultar energía actual/máximo |
| `Alt+3` | Último enemigo entrante |
| `Alt+4` | Último aliado entrante |
| `Alt+5` | Último player conectado |
| `Alt+6` | Último player desconectado |

---

## Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Scripts no funcionan | `Ctrl+Shift+R` (recarga) |
| Sonidos no se escuchan | Verificar `speech.ini` y volumen |
| Prompt no actualiza stats | Ejecutar `configurarprompt[variante]` |
| Lector de pantalla no habla | Reconfigurar voces en speech.ini |
| Combate flood de sonido | Cambiar a modo `Idle` o `Expert` (F11/F10) |
| Errores al editar `.set` | Asegurar edición solo con Notepad |

---

## Resumen: Qué Editar vs. Qué Consultar

### ✅ EDITAR/CREAR AQUÍ:
- `Reinos de leyenda/ScripsRL/Clases/` — Nueva clase
- `Reinos de leyenda/ScripsRL/Paths/` — Nueva ruta
- `Reinos de leyenda/[NombreDelPersonaje].set` — Archivo de personaje (crear nuevo)

### 🔍 CONSULTAR AQUÍ:
- `Reinos de leyenda/ScripsRL/Alias_Macros.set` — Ver qué está mapeado
- `Reinos de leyenda/ScripsRL/Generales.set` — Entender patrones
- `Reinos de leyenda/ScripsRL/Funciones.set` — Buscar función disponible
- `sounds/RL/` — Ver sonidos disponibles
- `Reinos de leyenda/ScripsRL/Doc/` — Leer documentación histórica

### ❌ NO EDITAR DIRECTAMENTE:
- `VipMud.set` — Configuración global (solo si sabes qué haces)
- `start.set` — Startup (solo si sabes qué haces)
- `speech.ini` — Config de voz (solo si sabes qué haces)

---

## Referencias Documentación Original

Para información completa y detallada, consultar:
- **Instalación:** `Reinos de leyenda/ScripsRL/Doc/Instrucciones instalación.txt`
- **Manejo:** `Reinos de leyenda/ScripsRL/Doc/Instrucciones manejo.txt`
- **Cambios:** `Reinos de leyenda/ScripsRL/Doc/Historial de cambios.txt`

---

## Tips de Desarrollo

1. **Crear extensión sin romper:**
   ```
   #Load ScripsRL\Clases\Soldados.set  # Carga base
   #Load ScripsRL\Clases/Mi_Extension.set  # Tu extensión
   ```

2. **Reload rápido después de editar:**
   - Guardar archivo
   - Presionar `Ctrl+Shift+R` en VipMud

3. **Debug de triggers:**
   - Buscar trigger en archivo
   - Verificar sintaxis VipMud
   - Usar alias temporales para test

4. **Nombrado consistente:**
   - Clases: `NombreClase.set`
   - Paths: `NombreCiudad.set`
   - Extensiones personales: `[NombrePJ]_[Función].set`

---

**Última actualización:** 23/04/2026
**Versión scripts:** 2.6+ (Reinos de Leyenda)
**Cliente requerido:** VipMud 2.0+
