# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VipZhyla is a collection of scripts and configurations for the **Reinos de Leyenda** MUD (Multi-User Dungeon), designed for the VipMud client (v2.0+). The scripts were originally written by Rhomdur and are optimized for accessibility, particularly for visually impaired players using screen readers.

The repository provides:
- Sound triggers and audio feedback for gameplay events
- Macros and keybindings for combat and movement
- Character class-specific configurations
- Pre-defined navigation paths (Paths) between game locations
- Accessibility features for blind/visually impaired players

### **Important: Read [accesibilidad.md](accesibilidad.md) First!**

If you're developing a desktop application for blind/visually impaired users, read **[accesibilidad.md](accesibilidad.md)** for comprehensive accessibility guidelines integrating WCAG 2.2 principles and proven patterns from ChannelHistory. This is foundational knowledge for the entire project.

## Repository Structure

```
VipZhyla/
├── Scripts/                    # ⭐ All game scripts and configurations
│   ├── Reinos de leyenda/      # Main game folder
│   │   ├── ScripsRL/           # Script library
│   │   │   ├── Clases/         # Character class scripts
│   │   │   ├── Paths/          # Navigation routes
│   │   │   ├── Ambientacion/   # Regional scripts
│   │   │   ├── Oficios/        # Trade/profession scripts
│   │   │   ├── Doc/            # Original documentation (Spanish)
│   │   │   └── [core scripts]  # Alias, Combat, Movimiento, etc.
│   │   └── Reinos de leyenda.set # Main game loader
│   ├── sounds/                 # Sound effects (.wav files)
│   ├── VipMud.set              # Client configuration
│   ├── start.set               # Startup script
│   └── speech.ini              # Screen reader config
├── scripts.md                  # ⭐ Quick reference for Scripts folder
├── accesibilidad.md            # Accessibility guidelines (WCAG 2.2 + ChannelHistory)
├── CLAUDE.md                   # This file
├── docs/WCAG2.2/               # WCAG 2.2 specification
└── [other documentation]
```

### **Quick Reference: See [scripts.md](scripts.md)**

The `Scripts/` folder contains 1700+ files. Don't browse it manually—use **[scripts.md](scripts.md)** as your index:
- Structure overview
- File purposes (when to edit, when to consult)
- Keyboard shortcuts summary
- Troubleshooting quick-fix table
- Examples of common tasks

## Where to Find Things

**⚠️ Don't browse Scripts/ manually—use [scripts.md](scripts.md) as your guide.**

| Need | Location | Reference |
|------|----------|-----------|
| New character class | `Scripts/Reinos de leyenda/ScripsRL/Clases/` | [scripts.md § Carpeta Clases/](scripts.md#carpeta-clases) |
| Navigation route | `Scripts/Reinos de leyenda/ScripsRL/Paths/` | [scripts.md § Carpeta Paths/](scripts.md#carpeta-paths) |
| Regional content | `Scripts/Reinos de leyenda/ScripsRL/Ambientacion/` | [scripts.md § Carpeta Ambientacion/](scripts.md#carpeta-ambientacion) |
| Trade/profession | `Scripts/Reinos de leyenda/ScripsRL/Oficios/` | [scripts.md § Carpeta Oficios/](scripts.md#carpeta-oficios) |
| Sound file | `Scripts/sounds/RL/[Category]/` | [scripts.md § Carpeta sounds/RL/](scripts.md#carpeta-soundsrl) |
| Global aliases | `Scripts/Reinos de leyenda/ScripsRL/Alias_Macros.set` | [scripts.md § Core Scripts](scripts.md#core-scripts-sistema-principal) |
| Combat system | `Scripts/Reinos de leyenda/ScripsRL/Combate.set` | [scripts.md § Core Scripts](scripts.md#core-scripts-sistema-principal) |
| Original docs | `Scripts/Reinos de leyenda/ScripsRL/Doc/` | [scripts.md § Referencias Documentación](scripts.md#referencias-documentación-original) |

## Working with Script Files

Scripts use `.set` file format (plain text containing VipMud scripting syntax: triggers, aliases, keybindings, etc.).

**Important:**
- Always edit `.set` files with Notepad only. Other editors may add unwanted line breaks that corrupt the files.
- Use `#Load` directives to include/inherit configuration from other files (e.g., `#Load ScripsRL\Clases\Soldados.set`).
- Reload scripts after editing by pressing `Ctrl+Shift+R` in VipMud to activate changes.
- Do not modify original files directly. Instead, create new `.set` files or extend existing ones to preserve compatibility with updates.

## Common Tasks

### Adding a New Character Class Script
1. Create a new file: `Reinos de leyenda/ScripsRL/Clases/YourClassName.set`
2. Define keybindings, combat macros, and sound triggers for the class
3. In the character's personal `.set` file, add: `#Load ScripsRL\Clases\YourClassName.set`
4. Reload scripts with `Ctrl+Shift+R`

### Adding Navigation Paths
1. Create a new file in `Reinos de leyenda/ScripsRL/Paths/` with directions linking two game locations
2. Update the path loader configuration to include the new route
3. Players will hear "Path disponible.wav" and see the route with `Ctrl+Shift+M`

### Adding Sound Triggers
1. Add `.wav` files to `sounds/RL/` in the appropriate category folder
2. Configure triggers in the appropriate `.set` file to play sounds on game events

## Installation & Setup

Full installation instructions are in **Reinos de leyenda/ScripsRL/Doc/Instrucciones instalación.txt** (Spanish).

Brief overview:
1. Download/install VipMud client (2.0+)
2. Create a character in VipMud pointing to rlmud.org:5001
3. Copy this repository to VipMud's user data folder
4. Run `configurarficha` command in-game to apply config
5. Run `configurarprompt[variant]` to set up the combat prompt for your character type

## Game Modes (Togglable)

- **Original** (F11) — Standard MUD text, no filtering
- **Combat** (F11) — Optimized for PvP/NPC combat, reduced spam
- **XP** (F11) — Minimal feedback for experience grinding
- **Idle** (F11) — Silenced for AFK gameplay
- **Expert** (F10) — Toggle; abbreviates common text for experienced players
- **Auto-center** (F7) — For classes with "centrar" ability; auto-cast before each attack

## Keybinding Conventions

- **Alt + letter** — Combat macros and movement (qwerty-based)
- **Ctrl + key** — General game commands (crouch, stand, bury, etc.)
- **Shift + Alt + key** — Extended combat/utility options
- **F1–F6** — Chat/communication history and info queries
- **Ctrl+Shift+M** — Display available navigation paths
- **Ctrl+Shift+R** — Reload all scripts

See **Reinos de leyenda/ScripsRL/Doc/Instrucciones manejo.txt** for complete keybinding reference (Spanish).

## Accessibility Features

This project prioritizes screen reader support and audio feedback for blind/visually impaired players. Key features include:
- Extensive sound triggers for combat, movement, and item events
- Screen-reader-friendly prompt design
- Chat history lists for reviewing communications
- Audio-based combat awareness (enemy entry/exit, skill confirmations)
- Configurable accessibility modes

**For development guidelines and best practices:** See **[accesibilidad.md](accesibilidad.md)**
- WCAG 2.2 principles adapted for desktop apps
- ChannelHistory accessibility patterns
- Keyboard navigation standards
- Screen reader integration examples
- Practical implementation checklist

## Contribution Notes

- The project is written in Spanish and maintains Spanish names for game elements
- Scripts are in active development; suggestions and improvements are welcomed
- If a character class is not yet supported, use generic templates: `Combate_fisico.set` or `Centrar.set`
- Test changes in VipMud before committing (reload with Ctrl+Shift+R)

## Documentation

- **Installation**: Reinos de leyenda/ScripsRL/Doc/Instrucciones instalación.txt
- **Usage Guide**: Reinos de leyenda/ScripsRL/Doc/Instrucciones manejo.txt
- **Change Log**: Reinos de leyenda/ScripsRL/Doc/Historial de cambios.txt
