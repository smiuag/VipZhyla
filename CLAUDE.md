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

## Repository Structure

```
Reinos de leyenda/
├── ScripsRL/
│   ├── Clases/           # Character class-specific scripts (Soldados.set, Khazads.set, etc.)
│   ├── Paths/            # Pre-defined navigation routes between game locations
│   ├── Ambientacion/     # Region/kingdom-specific scripts (Anduar, Dendra, Takome, etc.)
│   ├── Oficios/          # Trade/profession scripts (Minero, Herrero, Marinero, etc.)
│   ├── Doc/              # Installation and usage documentation
│   ├── Configuracion.set # Core configuration
│   ├── Alias_Macros.set  # Keybindings and macros
│   ├── Combate.set       # Combat system
│   ├── Modos.set         # Game mode toggles (XP, Expert, Silent, Idle)
│   └── [other core scripts for communication, movement, effects, etc.]
├── Reinos de leyenda.set # Main loader file for the game
sounds/
├── RL/                   # Sound files organized by category (Combat, Movement, Items, etc.)
VipMud.set               # VipMud client configuration
start.set                # Startup configuration
speech.ini               # Screen reader configuration
```

## Key Files and Their Purpose

- **Reinos de leyenda/ScripsRL/Clases/*.set** — Class-specific keybindings and combat macros. Add new classes here.
- **Reinos de leyenda/ScripsRL/Paths/*.set** — Navigation routes. Each file represents paths from/to a specific location.
- **Reinos de leyenda/ScripsRL/Doc/*.txt** — Installation instructions and usage guide (in Spanish).
- **sounds/RL/** — Sound event triggers. Organized by event type (Combate, Movimiento, Items, etc.).

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

## Contribution Notes

- The project is written in Spanish and maintains Spanish names for game elements
- Scripts are in active development; suggestions and improvements are welcomed
- If a character class is not yet supported, use generic templates: `Combate_fisico.set` or `Centrar.set`
- Test changes in VipMud before committing (reload with Ctrl+Shift+R)

## Documentation

- **Installation**: Reinos de leyenda/ScripsRL/Doc/Instrucciones instalación.txt
- **Usage Guide**: Reinos de leyenda/ScripsRL/Doc/Instrucciones manejo.txt
- **Change Log**: Reinos de leyenda/ScripsRL/Doc/Historial de cambios.txt
