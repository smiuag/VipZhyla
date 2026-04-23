# Guía de Accesibilidad para Aplicaciones de Escritorio

## Referencia

Este documento integra principios de **WCAG 2.2** (Web Content Accessibility Guidelines) y patrones implementados en **ChannelHistory** (proyecto especializado en accesibilidad para usuarios invidentes). Aunque WCAG está diseñado para contenido web, sus principios fundamentales son universalmente aplicables a aplicaciones de escritorio.

---

## 1. Los Cuatro Principios Fundamentales de Accesibilidad (WCAG)

### 1.1. **Perceptible** (Perceivable)
La información y los componentes de interfaz deben presentarse de manera que los usuarios puedan percibirla.

**Para aplicaciones de escritorio enfocadas en usuarios invidentes:**
- ✅ **Todo debe ser transmitible por audio/texto**: no confíes en elementos visuales únicamente
- ✅ **Proporciona alternativas de texto**: para cualquier contenido que no sea texto (gráficos, iconos, etc.)
- ✅ **Usa TTS (Text-to-Speech)**: integración de síntesis de voz del sistema operativo
- ✅ **Evita información que dependa únicamente de color, forma o posición visual**

**Implementación práctica:**
```
❌ Mal: "Presiona el botón rojo en la esquina superior derecha"
✅ Bien: "Presiona el botón 'Guardar' (etiqueta clara) o Alt+S (atajo de teclado)"
```

---

### 1.2. **Operable** (Operable)
Los componentes de interfaz y la navegación deben ser operables, principalmente mediante teclado.

**Para aplicaciones de escritorio enfocadas en usuarios invidentes:**
- ✅ **Accesibilidad total por teclado**: ninguna función requiere mouse
- ✅ **Atajos de teclado consistentes**: Alt+letra para funciones principales
- ✅ **Sin trampas de teclado**: el usuario nunca puede quedarse atrapado en un componente
- ✅ **Tiempo suficiente**: no hay límites de tiempo para completar tareas
- ✅ **Navegación predecible**: el orden de navegación es lógico y consistente

**Patrón de atajos WCAG/ChannelHistory:**
```
Alt + [Letra] → Función principal
Alt + Shift + [Letra] → Función secundaria/extendida
Ctrl + [Letra] → Comandos generales
```

**Ejemplo de implementación (ChannelHistory):**
```
Alt + Up/Down   → Navegar mensajes anterior/siguiente
Alt + Left/Right → Navegar categorías anterior/siguiente
Alt + Home/End  → Ir a primer/último mensaje
Alt + Shift + T → Toggle timestamps
Alt + 1-0       → Acceso rápido a mensajes recientes
```

---

### 1.3. **Comprensible** (Understandable)
El texto debe ser legible y comprensible, y la interfaz debe ser predecible.

**Para aplicaciones de escritorio enfocadas en usuarios invidentes:**
- ✅ **Lenguaje claro**: evita jerga innecesaria
- ✅ **Retroalimentación clara**: anuncia qué acción se está realizando
- ✅ **Estructura consistente**: la aplicación se comporta de manera predecible
- ✅ **Etiquetas descriptivas**: cada campo/botón tiene un nombre claro
- ✅ **Prevención de errores**: valida entradas antes de procesar

**Ejemplo de retroalimentación:**
```
❌ Mal: Usuario presiona Alt+S y... silencio
✅ Bien: "Archivo guardado. 1247 bytes escritos. Presiona Alt+Z para deshacer."
```

---

### 1.4. **Robusto** (Robust)
El contenido debe ser compatible con diferentes tecnologías de asistencia (screen readers, magnificadores, etc.).

**Para aplicaciones de escritorio enfocadas en usuarios invidentes:**
- ✅ **Compatibilidad con lectores de pantalla**: NVDA, JAWS, Narrator
- ✅ **Roles y nombres semánticos**: cada componente tiene un propósito claro
- ✅ **API de accesibilidad**: usa las APIs del OS (Windows Accessibility API, Linux A11y, etc.)
- ✅ **Sin dependencias propietarias**: evita componentes custom que los lectores no entiendan

---

## 2. Patrones Implementados en ChannelHistory

ChannelHistory es un proyecto Lua/Mudlet especializado en accesibilidad para usuarios invidentes. Implementa patrones probados en producción:

### 2.1. **Navegación por Categorías y Mensajes**

**Estructura de datos:**
```lua
categories       -- Array de nombres de categoría (ej: "Bando", "Telepátia", "Sala")
messages         -- Tabla: categoría → array de mensajes {texto, timestamp}
indices          -- Posición actual dentro de cada categoría (1-based)
selected_category-- Categoría actualmente enfocada
```

**Navegación:**
```
Alt + Left/Right    → Cambiar categoría anterior/siguiente (cíclica)
Alt + Up/Down       → Navegar mensaje anterior/siguiente dentro categoría
Alt + Home          → Primer mensaje de la categoría
Alt + End           → Último mensaje de la categoría
```

**Beneficio:** El usuario siempre sabe dónde está (qué categoría, qué posición en la lista).

---

### 2.2. **Anuncios de Texto-a-Voz Sensibles a la Plataforma**

**Implementación:**
```lua
-- Detecta el sistema operativo y usa la API nativa
if Windows then
    announce(message)  -- Windows native TTS API
elseif Mac then
    ttsQueue(message)  -- macOS system queue
elseif Linux then
    ttsQueue(message)  -- Linux system queue
end
```

**Ventaja:** 
- No depende de librerías externas
- Usa la voz del usuario (ya configurada a su gusto en Windows Accessibility)
- Compatible con lectores de pantalla existentes

---

### 2.3. **Multi-Tap Detection (Doble Toque)**

**Patrón:** Una sola tecla hace dos cosas en función del tiempo entre pulsaciones.

```lua
function channel_history.get(which)
    -- Primera pulsación: anuncia el mensaje
    -- Segunda pulsación (< 0.5s): copia al clipboard
    
    if click_time_delta < 500 then
        copy_to_clipboard(message)
        announce("Copiado al portapapeles")
    else
        announce(message)
    end
end
```

**Beneficio:** Reduce la cantidad de combinaciones de teclas necesarias.

---

### 2.4. **Toggle de Timestamps**

Permite mostrar/ocultar marcas de tiempo en forma legible para humanos.

```
Alt + Shift + T → Alterna timestamps
"3 minutos atrás" (formato relativo, fácil de entender)
"hace poco", "1 hora atrás", "3 días atrás"
```

**Beneficio:** El usuario controla verbosidad. Menos información = menos flood de audio.

---

### 2.5. **Límites de Almacenamiento**

```lua
-- Máximo 5000 mensajes por categoría
if #messages > 5000 then
    table.remove(messages, 1)  -- Elimina mensaje más antiguo
end
```

**Beneficio:** Evita que la aplicación se vuelva lenta por acumular demasiados datos.

---

### 2.6. **Acceso Rápido por Número**

```
Alt + 1 → Mensaje reciente #1
Alt + 2 → Mensaje reciente #2
...
Alt + 0 → Mensaje reciente #10
```

**Beneficio:** Acceso rápido sin navegar secuencialmente.

---

## 3. Guía de Implementación para Desktop Apps

### 3.1. **Diseño Centrado en Audio**

**Principio:** Cada elemento visual debe tener un equivalente auditivo.

| Elemento Visual | Equivalente Auditivo |
|---|---|
| Botón con ícono | Botón con etiqueta descriptiva + atajo |
| Tabla con columnas | Lista anidada con encabezados leídos |
| Colores/bordes | Cambios de estado verbalizados |
| Indicador visual de error | Sonido distintivo + mensaje de error claro |
| Barra de progreso | Anuncio de porcentaje cada N segundos |

**Ejemplo:**
```
❌ Visual: Ícono de disco (salvar)
✅ Auditivo: Botón "Guardar" + Alt+Ctrl+S + sonido de guardado confirmado

❌ Visual: Campo rojo (error)
✅ Auditivo: Anuncio "Error: Nombre de usuario vacío. Mínimo 3 caracteres."
```

---

### 3.2. **Convención de Atajos de Teclado (WCAG/ChannelHistory)**

```
Alt + [Letra]              → Funciones principales (frecuentes)
Alt + Shift + [Letra]      → Funciones extendidas/secundarias
Ctrl + [Letra]             → Comandos globales (archivo, edición)
Ctrl + Shift + [Letra]     → Comandos más potentes/peligrosos
Alt + [Flecha]             → Navegación (arriba/abajo, izquierda/derecha)
Alt + Home/End             → Ir a principio/fin
Alt + Page Up/Down         → Navegar por páginas/secciones
```

**Consistencia es clave:** El mismo atajo siempre hace lo mismo.

---

### 3.3. **Estructura de Anuncios (TTS)**

Cada acción debe generar un anuncio significativo:

```
[Acción] → [Estado resultante] → [Opciones disponibles]

Ejemplo:
"Archivo nuevo creado. Sin cambios. Presiona Alt+S para guardar o Alt+O para abrir."
```

**Mala estructura:**
```
"OK"  ← Usuario no sabe qué pasó
```

---

### 3.4. **Manejo de Modo Experto vs Novato**

Implementa niveles de verbosidad:

```lua
if expert_mode then
    announce_only_changes()      -- "Guardado"
else
    announce_full_context()      -- "Archivo guardado. 5 KB. Ubicación: C:\Docs\..."
end
```

---

### 3.5. **Validación y Prevención de Errores**

```lua
-- ❌ Mal
function save_file()
    if error_occurred then
        announce("Error")  -- ¿Cuál error?
    end
end

-- ✅ Bien
function save_file()
    if not filename then
        announce("Error: Nombre de archivo no especificado. Presiona Alt+N para nombrar.")
        return false
    end
    
    if file_exists(filename) and not confirm("¿Sobrescribir archivo existente?") then
        return false
    end
    
    local success, bytes = write_file(filename, content)
    if success then
        announce("Archivo guardado: " .. filename .. " (" .. bytes .. " bytes)")
    else
        announce("Error al guardar: " .. error_message)
    end
end
```

---

### 3.6. **Límites Temporales y Timeouts**

**WCAG 2.2.1 - Timing Adjustable:**
- No hay límites de tiempo para completar tareas
- Si es necesario un timeout, debe ser ajustable por el usuario
- Aviso previo antes de timeout (ej: 30 segundos de advertencia)

```lua
if timeout_approaching then
    announce("Sesión expirando en 30 segundos. Presiona Alt+E para extender.")
end
```

---

### 3.7. **Organización Jerárquica de Información**

Usa categorías y subcategorías como en ChannelHistory:

```
Mensajes
├── Bando
├── Telepátia
├── Sala
└── Sistema

Dentro de cada categoría: navegación ordenada (1-based indexing)
```

**Usuario ve:**
```
"Categoría: Bando. Mensaje 5 de 142."
```

---

## 4. Patrones de Accesibilidad Avanzados

### 4.1. **Context Stack (Pila de Contexto)**

Mantén un registro del contexto para navegación atrás:

```lua
context_stack = {
    {location = "menu_principal", option = 3},
    {location = "configuracion", option = 1},
    {location = "perfiles", profile = "jugador1"}
}

-- Alt+Backspace regresa al contexto anterior
```

---

### 4.2. **Búsqueda Incremental**

El usuario escribe caracteres y encuentra el primer elemento que coincide:

```
Usuario: "Alt+F" (buscar)
Entrada: "j"
App: "Anunciando: 'Jugador' (opción 3 de 15)"
Usuario: "a"
App: "Anunciando: 'Jaguares' (opción 5 de 15)"
```

---

### 4.3. **Descripciones Largas (Summary vs Detail)**

```lua
-- Short form (default)
announce("Datos guardados")

-- Long form (Alt+?) 
announce("Datos guardados. 127 registros. " ..
         "Ubicación: " .. filepath .. 
         ". Último guardado hace 2 minutos.")
```

---

### 4.4. **Sensores de Cambio de Estado**

Avisa cuando algo cambia sin interacción del usuario:

```lua
-- Alguien envía un mensaje en el chat
if new_message_received then
    announce("Nuevo mensaje de " .. sender .. ": " .. preview)
    play_notification_sound()
end
```

---

## 5. Checklist de Implementación

### Antes de Publicar

- [ ] **Teclado**: Toda función accesible sin mouse
- [ ] **Atajos consistentes**: Alt+letra para acciones principales
- [ ] **Sin trampas de teclado**: Tab/Escape siempre funcionan
- [ ] **Anuncios significativos**: TTS dice qué pasó y qué hacer
- [ ] **Navegación clara**: Usuario sabe dónde está en la jerarquía
- [ ] **Etiquetas descriptivas**: Cada botón/campo tiene nombre claro
- [ ] **Timeouts ajustables**: Ninguna tarea tiene límite de tiempo fijo
- [ ] **Validación inteligente**: Errores específicos, no genéricos
- [ ] **Categorización**: Información organizada en grupos lógicos
- [ ] **Límites de almacenamiento**: No acumula datos infinitamente
- [ ] **Modo verbose/expert**: Control de nivel de detalle
- [ ] **Prueba con NVDA/JAWS**: Compatibilidad con lectores reales

### Testing

```bash
# Test con NVDA (libre, Windows)
# https://www.nvaccess.org/

# Test con Narrator (Windows nativo)
# Win + Ctrl + Enter

# Test manual sin mouse
# Desactiva touchpad/mouse en BIOS o SO
# Intenta completar todas las tareas usando solo teclado
```

---

## 6. Herramientas y Librerías Recomendadas

### Síntesis de Voz

| Lenguaje | Librería | Notas |
|---|---|---|
| Python | `pyttsx3` | Multiplataforma, sin conexión |
| C# | `System.Speech` | Nativo de Windows |
| Node.js | `web-speech-api` | Solo navegador |
| Lua | `ttsQueue()` (Mudlet) | Específico del cliente |

### APIs de Accesibilidad

| OS | API | Documentación |
|---|---|---|
| Windows | **UI Automation** / **MSAA** | Microsoft Accessibility API |
| macOS | **NSAccessibility** | Apple Accessibility API |
| Linux | **AT-SPI2** | Assistive Technology Service Provider Interface |

---

## 7. Referencias y Normas

- **WCAG 2.2**: https://www.w3.org/TR/WCAG22/ (Principios: Perceivable, Operable, Understandable, Robust)
- **ChannelHistory**: https://github.com/ironcross32/ChannelHistory (Implementación de referencia)
- **NVDA (Screen Reader gratuito)**: https://www.nvaccess.org/
- **JAWS (Screen Reader profesional)**: https://www.freedomscientific.com/products/software/jaws/
- **Windows Narrator**: Incluido en Windows 10+ (Win + Ctrl + Enter)

---

## 8. Ejemplo de Aplicación Accesible Mínima (Python)

```python
import pyttsx3
import sys

class AccessibleApp:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Velocidad moderada
        self.state = "menu"
        self.messages = ["Mensaje 1", "Mensaje 2", "Mensaje 3"]
        self.current_msg_idx = 0
    
    def speak(self, text):
        """Anuncia texto vía TTS"""
        print(f"[TTS] {text}")  # Debug
        self.engine.say(text)
        self.engine.runAndWait()
    
    def on_up(self):
        """Alt + Up: mensaje anterior"""
        if self.current_msg_idx > 0:
            self.current_msg_idx -= 1
            self.announce_current_message()
    
    def on_down(self):
        """Alt + Down: mensaje siguiente"""
        if self.current_msg_idx < len(self.messages) - 1:
            self.current_msg_idx += 1
            self.announce_current_message()
    
    def announce_current_message(self):
        msg = self.messages[self.current_msg_idx]
        pos = self.current_msg_idx + 1
        total = len(self.messages)
        self.speak(f"Mensaje {pos} de {total}: {msg}")
    
    def run(self):
        self.speak("Aplicación iniciada. Presiona flechas arriba/abajo para navegar. Ctrl+C para salir.")
        while True:
            try:
                key = input(">>> ").strip().lower()
                if key in ["up", "u"]:
                    self.on_up()
                elif key in ["down", "d"]:
                    self.on_down()
                elif key in ["quit", "q"]:
                    self.speak("Aplicación cerrada")
                    break
                else:
                    self.speak("Comando no reconocido")
            except EOFError:
                break

if __name__ == "__main__":
    app = AccessibleApp()
    app.run()
```

---

## 9. Notas Finales

**La accesibilidad no es un complemento, es un diseño fundamental.**

- Comienza desde el prototipo, no al final
- Involucra usuarios invidentes reales en el desarrollo
- Itera basado en retroalimentación (no suposiciones)
- Mantén la consistencia en toda la aplicación
- Documenta los atajos y comportamientos claramente

**Objetivo:** Una aplicación donde un usuario invidente sea tan rápido y eficiente como con una GUI visual optimizada para videntes.
