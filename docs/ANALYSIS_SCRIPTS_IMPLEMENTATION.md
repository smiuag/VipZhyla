# Análisis: Implementación de Scripts de Reinos de Leyenda en VipZhyla

## Estado General

VipZhyla es un cliente MUD **incompleto** en cuanto a procesamiento de flujo de mensajes. Actualmente implementa lo básico (conexión, TTS, triggers simples), pero **carece de muchas características críticas** del sistema de scripts de VipMud para evitar spam y procesar mensajes correctamente.

---

## 1. CANALES DE COMUNICACIÓN

### ✅ Implementado en VipZhyla
- Sistema básico de canales (`ChannelType` enum en `mud_parser.py`)
- Historial de mensajes por canal (`MessageBuffer`)
- Visualización de historiales en diálogos (`list_dialogs.py`)

### ❌ FALTA: Características Críticas
- **Historial de tamaño limitado**: VipMud limita a 99 mensajes por canal. VipZhyla no tiene límite claro.
- **Variables de control "Silencio"**: VipMud tiene `SilencioTels`, `SilencioRoom`, `SilencioBando`, etc. para mutetar canales individuales.
- **Filtro de canales dinámico**: No hay forma de mutetar/filtrar canales al vuelo.
- **Detección de canales completa**: 

| Canal | Estado |
|-------|--------|
| Telepátia | ❌ No diferenciado |
| Room | ❌ No diferenciado |
| Bando | ✅ Detectado (GMCP) |
| Ciudadanía | ❌ No detectado |
| Chat | ❌ No detectado |
| Gremio | ✅ Detectado (GMCP) |
| Familia | ❌ No detectado |
| Rol | ❌ No detectado |
| Especiales | ❌ No detectado |

---

## 2. PROCESAMIENTO DE DESCRIPCIONES DE ROOMS

### Problema Principal
Cuando te mueves por rooms con descripciones largas, VipMud **filtra/silencia** las descripciones para evitar spam. VipZhyla **NO** hace esto.

### ✅ Implementado
- Recepción de descripción GMCP del room (`gmcp_handler.py`)
- Parsing básico de información del room

### ❌ FALTA: Filtrado de Descripciones
- **FiltroSalidas** (Configuracion.set línea 55): Variable que controla si se leen/muestran descripciones
  - Desactivado por defecto (0), pero debería poder activarse
  - Cuando está activo, las descripciones largas de rooms se silencian
  
- **ModoPath** (Configuracion.set línea 30): Controla velocidad de movimiento
  - `0`: 2 rooms cada 2 segundos (normal)
  - `1`: 1 room por segundo (turbo)
  - `2`: Modo ultra-turbo
  - Afecta cuánto spam se genera

- **GagLine voice**: En VipMud se usa para silenciar TTS de ciertos mensajes
  - Ejemplo: `#GagLine voice` después de una función elimina el anuncio TTS

### Archivos Relevantes en Scripts/
- `Movimiento_propio.set` - Cómo se procesa el movimiento propio
- `Movimiento_otros.set` - Cómo se procesan movimientos de otros
- `Movimiento_keys.set` - Atajos de teclado para movimiento
- `Funciones.set` línea 71+: `FuncReproducirDireccion` - Reproducción de sonidos direccionales

---

## 3. CORRECCIÓN Y FILTRADO DE TEXTOS

### ✅ Implementado
- Parsing básico de MUD output
- Manejo de ANSI codes (strip)
- Encoding de caracteres (UTF-8 / ISO-8859-1)

### ❌ FALTA: Sistema de Corrección Completo
VipMud tiene un sistema completo en `Corrector.set`:
- Corrección de signos (acentos, puntuación)
- Normalización de espacios
- Eliminación de caracteres especiales
- Función `FuncCorrectorSignos` y `FuncCorrectorCanales`

**Impacto**: Los textos pueden llegar malformados. No hay normalización.

### Archivo Relevante
- `Corrector.set` - Sistema completo de corrección

---

## 4. HISTORIAL Y BUFFERS

### ✅ Implementado
- `MessageBuffer`: Almacena mensajes por canal
- Historial dialogs: Puedes ver mensajes históricos (Shift+F1-F4)

### ❌ FALTA: Gestión Avanzada
- **Límite de 99 elementos**: VipMud lo tiene. VipZhyla podría exceder memoria
- **Persistencia**: No se guarda historial a disco
- **Búsqueda en historial**: No hay búsqueda/filtrado de mensajes históricos
- **Copiar desde historial**: `FCopiar` en VipMud permite copiar mensajes a clipboard

### Archivos Relevantes
- `Comunicaciones.set` línea 83-104: Gestión de historial con límite de 99

---

## 5. EVENTOS Y REACCIONES

### ✅ Implementado
- Sistema básico de triggers
- Condiciones simples
- Acciones (TTS, GAG)

### ❌ FALTA: Eventos Complejos
VipMud tiene triggers para eventos complejos:
- Entrada/salida de PCs en rooms (Funciones.set línea 70-110)
- Reacciones a habilidades (tipo %3)
- Reacciones a cambios de presentes en room
- Sonidos direccionales automáticos

**Ejemplo VipMud** (Funciones.set línea 71):
```
#GAlias FuncReproducirDireccion {
  #If {%3 = 1 and %IfWord(%2,@ListaDireccionesValidas,|)} {
    FuncComprobarSujeto %1 {RL\Movimiento\Direcciones\Llegada aliados\%2.wav}
  }
}
```

VipZhyla no puede hacer esto automáticamente.

### Archivos Relevantes
- `Eventos.set` - Sistema de eventos
- `Funciones.set` - Funciones base de reacción

---

## 6. CONFIGURACIÓN DINÁMICA

### ✅ Implementado
- Diálogo de Preferencias (Ctrl+P)
- Cambio de encoding

### ❌ FALTA: Opciones de Configuración
VipMud tiene muchas opciones en `Configuracion.set`:

| Variable | Propósito | Estado |
|----------|-----------|--------|
| `ModoJ` | Modo de juego (Combate/XP/Idle) | ❌ No |
| `ModoE` | Modo experto (output reducido) | ❌ No |
| `ModoPath` | Velocidad de movimiento | ❌ No |
| `ModoS` | Modo silencioso (sin sonidos) | ❌ No |
| `AlertaVida` | Alertas de HP bajo | ✅ Parcial |
| `ModoAmbientacion` | Sonidos ambiente | ❌ No |
| `FiltroSalidas` | Filtra descripciones largas | ❌ **CRÍTICO** |
| `AutoCentrar` | Centrarse automáticamente | ❌ No |
| `SeleccionCanal` | Canal inicial | ❌ No |

---

## 7. SONIDOS Y AUDIO

### ✅ Implementado
- TTS básico
- Reproducción de sonidos simples (via pygame/winsound)
- Control de volumen

### ❌ FALTA: Sistema Avanzado de Audio
- **Sonidos direccionales**: Entradas/salidas con panning L/R basado en dirección
- **Frecuencia variable**: Cambiar pitch de sonidos según contexto
- **Sonidos contextuales**: Diferentes sonidos para aliados vs enemigos
- **Sonidos de rooms**: Sonidos ambientales por location
- **GagLine**: Silenciar TTS selectivamente

### Ejemplo VipMud (Funciones.set línea 74-85):
```
#If {%2 = "noreste" or %2 = "sudeste"} {
  #Var TempRepDir 2500    ; Paneo derecha
};
#If {%2 = "noroeste" or %2 = "sudoeste"} {
  #Var TempRepDir -2500   ; Paneo izquierda
};
```

### Archivo Relevante
- `Funciones.set` línea 164+: `FuncPlayPan` - Audio con panning

---

## 8. PRESENTES EN ROOM Y SEGUIMIENTO

### ✅ Implementado
- Parseo básico de presentes (GMCP)
- Almacenamiento en `CharacterState`

### ❌ FALTA: Actualización Dinámica
- No se actualiza lista de presentes al entrar/salir PCs
- No hay triggers para "PC ha entrado"/"PC ha salido"
- No hay seguimiento de enemigos vs aliados en room

---

## 9. COMBATE Y REACCIONES EN COMBATE

### ✅ Implementado
- Detección de daño (via triggers)
- Anuncios de HP bajo
- Estados básicos

### ❌ FALTA: Sistema Completo
VipMud tiene en `Combate.set`:
- Detección de ataques fallidos
- Reacciones a hechizos
- Reacciones a habilidades especiales
- Seguimiento de combatientes
- Modo combate/XP/Idle con switches automáticos

---

## 10. ARCHIVOS CRÍTICOS NO IMPLEMENTADOS

### Prioridad ALTA (necesarios para funcionalidad base)
1. **Comunicaciones.set** - 📄 Necesita análisis pero parcialmente implementado
2. **Configuracion.set** - ⚠️ Falta `FiltroSalidas`, `ModoPath`, otros
3. **Corrector.set** - ❌ Completamente ausente
4. **Funciones.set** - ⚠️ Parcialmente (falta audio direccional, gestión de presentes)

### Prioridad MEDIA (para mejora de UX)
5. **Movimiento_propio.set** - ⚠️ Básico implementado, falta filtrado de output
6. **Movimiento_otros.set** - ❌ No hay reacciones a movimientos de otros
7. **Eventos.set** - ❌ Sistema de eventos completo ausente
8. **Embarcaciones.set** - ❌ No hay soporte para barcos

### Prioridad BAJA (características avanzadas)
9. **Clases/** - ⚠️ Solo atajos de teclado básicos
10. **Oficios/** - ❌ No hay soporte
11. **Paths/** - ⚠️ Rutas cargadas pero no hay macro-movimiento
12. **Ambientacion/** - ❌ Sonidos ambientales no implementados

---

## 11. PROBLEMA ESPECÍFICO: SPAM DE DESCRIPCIONES

### El Problema
Cuando mueves un character rápidamente (mucho moving), recibe:
1. Descripción larga del room
2. Lista de presentes
3. Salidas disponibles
4. Información GMCP

Multiplicado por 10 rooms = MUCHO SPAM para un usuario ciego.

### Solución en VipMud
```
#Var FiltroSalidas 0  ; Desactivado por defecto
; Cuando está activo:
; - NO anuncia descripciones largas
; - NO anuncia listas de presentes
; - Anuncia solo: ubicación, enemigos
```

### Lo que Falta en VipZhyla
1. **Opción de FiltroSalidas** en preferencias (Ctrl+P)
2. **Detección de longitud**: Si descripción > X caracteres, silenciar
3. **Actualización inteligente**: Solo anunciar cambios relevantes (nuevos presentes, enemigos)

---

## 12. ARQUITECTURA FALTANTE

### Modelo de Datos Necesario

```python
# Debería haber (no existe actualmente):

class OutputFilter:
    """Gestiona qué se muestra/anuncia"""
    - gag_lines: dict       # Líneas a silenciar
    - filter_descriptions: bool  # FiltroSalidas
    - max_description_length: int  # Si > X, silenciar
    - muted_channels: dict  # Canales muteados

class ChannelManager:
    """Gestiona canales con límites"""
    - channels: dict[ChannelType, Channel]
    - max_history: int = 99  # Límite VipMud
    - mute_status: dict     # Qué canales están mutados

class MovementProcessor:
    """Procesa movimiento inteligentemente"""
    - last_room: str
    - last_presentes: list
    - detect_new_presentes()  # Anuncia solo nuevas entradas
    - filter_description_by_mode(text, mode)
```

---

## RECOMENDACIONES DE IMPLEMENTACIÓN

### Fase Inmediata (CRÍTICO)
1. **Agregar FiltroSalidas a preferencias**
   - Opción on/off en Ctrl+P
   - Cuando activo, NO anuncia descripciones > 200 caracteres

2. **Agregar límite a historiales**
   - Maximum 99 messages per channel
   - Remove oldest when limit exceeded

3. **Agregar silenciamiento selectivo**
   - Poder mutetar canales individuales desde UI

### Fase 2 (IMPORTANTE)
4. Implementar `OutputFilter` class
5. Agregar detección inteligente de nuevos presentes
6. Agregar sonidos direccionales (panning)
7. Agregar `ModoPath` (velocidad de movimiento)

### Fase 3 (MEJORA)
8. Implementar corrector de textos (Corrector.set)
9. Agregar eventos complejos (entrada/salida de PCs)
10. Agregar sonidos ambientales por room

---

## ARCHIVOS RELEVANTES EN VIPZHYLA

### Deben revisarse/actualizarse:
- `src/client/message_buffer.py` - Agregar límite de 99
- `src/client/mud_parser.py` - Agregar detección de todos los canales
- `src/ui/preferences_dialog.py` - Agregar opciones FiltroSalidas, ModoPath, etc.
- `src/main.py` - Aplicar filtros en append_output()
- `src/app/audio_manager.py` - Agregar soporte para GagLine

### Deben crearse:
- `src/client/output_filter.py` - Nuevo: Filtrado inteligente de output
- `src/client/channel_manager.py` - Nuevo: Gestión de canales con límites
- `src/models/channel_config.py` - Nuevo: Configuración de canales

---

## CONCLUSIÓN

VipZhyla está **en fase muy temprana** de desarrollo respecto al procesamiento de flujo de mensajes. Los scripts de VipMud tienen un sistema maduro y complejo de:
- Filtrado de spam
- Gestión de canales
- Reacciones automáticas
- Audio direccional
- Corrección de textos

Para que VipZhyla sea usable a largo plazo, necesita implementar al menos las características de **Fase Inmediata** (arriba), especialmente el **FiltroSalidas**, que es crítico para evitar spam cuando se viaja rápido.

