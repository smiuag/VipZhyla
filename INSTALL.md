# Instalación y Uso de VipZhyla

## Requisitos

- **Python 3.11+** ([descargar](https://www.python.org/downloads/))
- **Pantalla o screen reader** (NVDA, JAWS, Narrator)
- **Conexión a Internet** (para conectar al MUD)

## Pasos de Instalación

### 1. Descargar el proyecto

```bash
git clone https://github.com/tu-usuario/VipZhyla.git
cd VipZhyla
```

O descargar el ZIP desde GitHub y extraerlo.

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --user -r requirements.txt
```

Si hay problemas, instala manualmente:
```bash
pip install --user wxPython pyttsx3
```

### 4. Ejecutar la aplicación

```bash
python src/main.py
```

¡Deberías escuchar: "VipZhyla iniciado. Presiona F1 para ayuda, Ctrl+K para conectar."

---

## Primeros Pasos

### 1. Abrir la Ayuda
Presiona **F1** → Escucharás una bienvenida con 10 pestañas de ayuda completa

### 2. Conectar al MUD
Presiona **Ctrl+K** → Dialogo de conexión
- Servidor por defecto: `reinosdeleyenda.com:23`
- O escribe otro servidor MUD
- Presiona Enter para conectar

### 3. Movimiento
Usa **Alt + tecla**:
- Alt+U = Oeste
- Alt+O = Este
- Alt+I = Arriba
- Alt+K = Sur
- Alt+8 = Norte
- Alt+M = Abajo

El cliente anunciará automáticamente cada sala a la que entres.

### 4. Localización en el Mapa
Escribe `locate` y presiona Enter
- El cliente enviará "ojear" al MUD
- Escuchará: "Localizado: {Sala}. Salidas: {n,s,e,o}"

### 5. Navegar a una Sala
Escribe `irsala mercado` y presiona Enter
- El cliente busca "mercado"
- Si hay 1 resultado: navega automáticamente
- Si hay varios: muestra opciones
- Puedes cancelar con `parar`

### 6. Historial de Mensajes
Presiona **Shift+F1-F4**:
- Shift+F1 = Canal general
- Shift+F2 = Historial de sala
- Shift+F3 = Telepatía
- Shift+F4 = Eventos
- Usa Arriba/Abajo para navegar mensajes
- Presiona Escape para cerrar

### 7. Gestionar Triggers/Aliases (Avanzado)
Presiona **Ctrl+T** → Dialogo de gestión
- 3 pestañas: Triggers, Aliases, Timers
- Triggers: detectan patrones en el juego y reaccionan
- Aliases: accesos directos de comandos (h → help)
- Timers: acciones periódicas
- **Nota:** La UI de edición está en desarrollo (Phase 3.5)

---

## Comandos Especiales del Cliente

| Comando | Qué hace | Ejemplo |
|---------|----------|---------|
| `locate` | Establece tu posición actual | `locate` |
| `irsala <nombre>` | Navega automáticamente a una sala | `irsala mercado` |
| `parar` | Detiene una navegación en curso | `parar` |

---

## Atajos de Teclado Completo

### Conexión
- `Ctrl+K` = Conectar
- `Ctrl+D` = Desconectar

### Movimiento (Alt+Tecla)
- `U/O/I/M/K/8/7/9/J/L/,/.` = Direcciones

### Historial (Shift+F1-F4)
- `Shift+F1` = Canales
- `Shift+F2` = Sala
- `Shift+F3` = Telepatía
- `Shift+F4` = Eventos
- `Alt+Arriba/Abajo` = Mensaje anterior/siguiente
- `Alt+Izq/Der` = Canal anterior/siguiente
- `Alt+Inicio/Fin` = Primer/último mensaje

### Gestión
- `F1` = Ayuda
- `Ctrl+T` = Triggers/Aliases/Timers
- `Ctrl+Shift+V` = Toggle modo verboso
- `Enter` = Enviar comando
- `Escape` = Cerrar diálogo

---

## Solucionar Problemas

**"No se oye nada"**
- Verifica que tu PC tiene volumen
- Abre el gestor de volumen del sistema

**"No puedo escribir"**
- Presiona Tab hasta enfocar el campo de entrada
- Verifica que el cursor está en el campo (debe estar enfocado)

**"Módulo wxPython no encontrado"**
```bash
pip install --user wxPython pyttsx3
```

**"No puedo conectar al MUD"**
- Verifica tu conexión a Internet
- Intenta otro servidor (ej: `almarsrealm.com:4000`)
- Verifica que el servidor está en línea

**"Screen reader no lee nada"**
- Asegúrate que NVDA/JAWS está ejecutándose
- Presiona Ctrl+Alt+N para iniciar NVDA (Windows)
- Haz clic en la ventana de VipZhyla para enfocarla

---

## Recursos Adicionales

- **[README.md](README.md)** — Descripción general del proyecto
- **[CLAUDE.md](CLAUDE.md)** — Guía de arquitectura (para desarrolladores)
- **[accesibilidad.md](accesibilidad.md)** — Estándares WCAG 2.2 implementados
- **Ayuda en la app** — Presiona F1 para ayuda integrada

---

## Estado Actual (Alpha v0.1.0)

✓ Fases completadas:
- Fase 1: Infraestructura core (wxPython, keyboard, TTS)
- Fase 2: Conexión MUD (Telnet, GMCP, buffer)
- Fase 2.5: Historial de mensajes (Shift+F1-F4)
- Fase 3: Automación (triggers, aliases, timers)
- **Fase 4: Mapa y Navegación (NUEVO)**

⏳ Próximas fases:
- Fase 3.5: UI de edición mejorada para triggers
- Fase 5: Testing completo con screen readers reales

---

## ¿Encontraste un bug?

1. Nota qué hiciste (comandos, keybindings)
2. Qué esperabas que pasara
3. Qué pasó en realidad
4. Tu screen reader (NVDA, JAWS, Narrator, etc.)

Reporta en GitHub Issues o contacta al autor.

---

**¡Bienvenido a VipZhyla!** 🎮
