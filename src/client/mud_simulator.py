"""MUD Simulator for testing without live connection.

Generates realistic MUD output sequences for trigger testing,
character state changes, and complex scenarios.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Callable
import time


class SimulatorEventType(Enum):
    """Types of simulator events."""
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    TAKE_DAMAGE = "take_damage"
    RECEIVE_BUFF = "receive_buff"
    RECEIVE_DEBUFF = "receive_debuff"
    LEVEL_UP = "level_up"
    ITEM_FOUND = "item_found"
    ENEMY_SPOTTED = "enemy_spotted"
    CONVERSATION = "conversation"
    SYSTEM_MESSAGE = "system_message"


@dataclass
class SimulatorScenario:
    """A scenario with events that occur over time."""
    name: str
    description: str
    events: List[tuple]  # (delay_seconds, event_type, data)
    repeatable: bool = False


class MUDSimulator:
    """Simulates MUD output for testing."""

    def __init__(self):
        """Initialize the simulator."""
        self.callback: Callable[[str], None] = None
        self.running = False

    def set_output_callback(self, callback: Callable[[str], None]):
        """Set callback to receive simulated MUD output.

        Args:
            callback: Function to call with MUD output lines
        """
        self.callback = callback

    def emit(self, text: str):
        """Emit a line of MUD output.

        Args:
            text: Text to emit
        """
        if self.callback:
            self.callback(text)

    # Scenario: Combat Encounter
    def scenario_combat_encounter(self):
        """Simulate a combat encounter with damage, buffs, and healing."""
        self.emit("You see a fierce orc approaching!")
        time.sleep(0.5)
        self.emit("The orc attacks you! You take 25 damage.")
        time.sleep(0.5)
        self.emit("Your health is low!")
        time.sleep(0.5)
        self.emit("You cast a healing spell on yourself.")
        time.sleep(0.5)
        self.emit("You feel the warmth of healing magic!")
        time.sleep(0.5)
        self.emit("You feel blessed and stronger!")
        time.sleep(0.5)
        self.emit("You strike the orc for 40 damage!")
        time.sleep(0.5)
        self.emit("The orc is defeated!")
        time.sleep(0.5)
        self.emit("Combat has ended.")

    # Scenario: Poison & Cure
    def scenario_poison_cure(self):
        """Simulate being poisoned and cured."""
        self.emit("You are suddenly poisoned!")
        time.sleep(0.5)
        self.emit("The poison courses through your veins.")
        time.sleep(0.5)
        self.emit("Your health is deteriorating rapidly.")
        time.sleep(0.5)
        self.emit("You drink an antidote potion.")
        time.sleep(0.5)
        self.emit("You feel the poison leaving your body.")

    # Scenario: Level Up & New Abilities
    def scenario_level_up(self):
        """Simulate leveling up and gaining new abilities."""
        self.emit("You have gained enough experience!")
        time.sleep(0.5)
        self.emit("You are now level 20!")
        time.sleep(0.5)
        self.emit("You learn a new skill: Fireball Mastery")
        time.sleep(0.5)
        self.emit("Your maximum health increases to 500!")

    # Scenario: Complex Combat with Multiple Enemies
    def scenario_multi_enemy_combat(self):
        """Simulate combat with multiple enemies."""
        self.emit("Three bandits surround you!")
        time.sleep(0.3)
        self.emit("First bandit attacks! You take 15 damage.")
        time.sleep(0.3)
        self.emit("Second bandit attacks! You take 12 damage.")
        time.sleep(0.3)
        self.emit("Your health is low!")
        time.sleep(0.3)
        self.emit("You cast protection spell on yourself.")
        time.sleep(0.3)
        self.emit("You feel protected and stronger!")
        time.sleep(0.3)
        self.emit("You counter-attack the first bandit!")
        time.sleep(0.3)
        self.emit("First bandit is defeated!")
        time.sleep(0.3)
        self.emit("Second bandit flees in fear!")
        time.sleep(0.3)
        self.emit("Third bandit surrenders!")

    # Scenario: Boss Fight
    def scenario_boss_fight(self):
        """Simulate a boss encounter."""
        self.emit("You see the legendary dragon!")
        time.sleep(0.5)
        self.emit("The dragon roars and begins the battle!")
        time.sleep(0.5)
        self.emit("Dragon breathes fire! You take 40 damage!")
        time.sleep(0.5)
        self.emit("Your health is critical!")
        time.sleep(0.5)
        self.emit("You cast your most powerful spell!")
        time.sleep(0.5)
        self.emit("Direct hit! Dragon takes massive damage!")
        time.sleep(0.5)
        self.emit("You are blessed by ancient magic!")
        time.sleep(0.5)
        self.emit("You feel invincible!")
        time.sleep(0.5)
        self.emit("Dragon's final attack!")
        time.sleep(0.5)
        self.emit("Dragon is defeated!")
        time.sleep(0.5)
        self.emit("You have gained legendary status!")

    # Scenario: Exploration & Discovery
    def scenario_exploration(self):
        """Simulate exploring and discovering items."""
        self.emit("You explore the ancient ruins.")
        time.sleep(0.5)
        self.emit("You find a hidden chest!")
        time.sleep(0.5)
        self.emit("Inside you find: legendary sword, 1000 gold coins")
        time.sleep(0.5)
        self.emit("You equip the legendary sword.")
        time.sleep(0.5)
        self.emit("You feel the power of the sword!")
        time.sleep(0.5)
        self.emit("You discovered the Lost Tomb of Kings!")

    # Scenario: Social Interaction
    def scenario_conversation(self):
        """Simulate NPC conversation."""
        self.emit("Merchant: Welcome to my shop, adventurer!")
        time.sleep(0.5)
        self.emit("Merchant: I have rare potions and equipment.")
        time.sleep(0.5)
        self.emit("You: What do you recommend?")
        time.sleep(0.5)
        self.emit("Merchant: The dragon slayer's armor is excellent.")
        time.sleep(0.5)
        self.emit("You purchase dragon slayer's armor for 500 gold.")
        time.sleep(0.5)
        self.emit("You equip the dragon slayer's armor.")
        time.sleep(0.5)
        self.emit("Your defense has increased significantly!")

    # Scenario: Status Updates
    def scenario_status_updates(self):
        """Simulate various status updates."""
        self.emit("Status: HP 450/500, MP 180/200, EXP 45%")
        time.sleep(1.0)
        self.emit("Status: HP 425/500, MP 160/200, EXP 48%")
        time.sleep(1.0)
        self.emit("Status: HP 400/500, MP 140/200, EXP 50%")
        time.sleep(1.0)
        self.emit("Level up! You are now level 25!")

    # Scenario: Quest Line
    def scenario_quest(self):
        """Simulate a quest."""
        self.emit("Quest received: Defeat the goblin king")
        time.sleep(0.5)
        self.emit("Travel to the goblin fortress to the north.")
        time.sleep(0.5)
        self.emit("You arrive at the goblin fortress.")
        time.sleep(0.5)
        self.emit("The goblin king appears!")
        time.sleep(0.5)
        self.emit("Goblin King: You dare challenge me?")
        time.sleep(0.5)
        self.emit("Combat begins!")
        time.sleep(0.5)
        self.emit("You are poisoned!")
        time.sleep(0.5)
        self.emit("You take 30 damage from poison!")
        time.sleep(0.5)
        self.emit("You drink an antidote.")
        time.sleep(0.5)
        self.emit("You defeat the Goblin King!")
        time.sleep(0.5)
        self.emit("Quest completed! You receive 5000 gold and experience!")

    # Scenario: Rapid Combat (rapid-fire triggers)
    def scenario_rapid_combat(self):
        """Simulate rapid combat with many triggers firing."""
        self.emit("Combat starts!")
        time.sleep(0.1)
        self.emit("Enemy attacks!")
        time.sleep(0.1)
        self.emit("You take damage!")
        time.sleep(0.1)
        self.emit("Your health is low!")
        time.sleep(0.1)
        self.emit("You counter-attack!")
        time.sleep(0.1)
        self.emit("Enemy takes damage!")
        time.sleep(0.1)
        self.emit("Enemy attacks again!")
        time.sleep(0.1)
        self.emit("You are poisoned!")
        time.sleep(0.1)
        self.emit("You cast shield!")
        time.sleep(0.1)
        self.emit("Shield is active!")
        time.sleep(0.1)
        self.emit("Enemy defeated!")

    def get_scenarios(self) -> dict:
        """Get all available scenarios.

        Returns:
            Dict of scenario names and methods
        """
        return {
            "combat": ("Basic Combat Encounter", self.scenario_combat_encounter),
            "poison": ("Poison & Cure", self.scenario_poison_cure),
            "levelup": ("Level Up & New Abilities", self.scenario_level_up),
            "multi": ("Multi-Enemy Combat", self.scenario_multi_enemy_combat),
            "boss": ("Boss Fight", self.scenario_boss_fight),
            "explore": ("Exploration & Discovery", self.scenario_exploration),
            "talk": ("Social Interaction", self.scenario_conversation),
            "status": ("Status Updates", self.scenario_status_updates),
            "quest": ("Quest Line", self.scenario_quest),
            "rapid": ("Rapid-Fire Combat", self.scenario_rapid_combat),
        }

    def run_scenario(self, scenario_key: str):
        """Run a specific scenario.

        Args:
            scenario_key: Key of scenario to run
        """
        scenarios = self.get_scenarios()
        if scenario_key in scenarios:
            name, method = scenarios[scenario_key]
            print(f"\n[MUD Simulator] Running: {name}")
            print("=" * 50)
            method()
            print("=" * 50)
            print("[MUD Simulator] Scenario complete\n")
        else:
            print(f"Unknown scenario: {scenario_key}")
            print(f"Available: {', '.join(scenarios.keys())}")

    def list_scenarios(self):
        """List all available scenarios."""
        scenarios = self.get_scenarios()
        print("\nAvailable MUD Simulator Scenarios:")
        print("=" * 50)
        for key, (name, _) in scenarios.items():
            print(f"  {key:12} - {name}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    # Example usage
    simulator = MUDSimulator()

    # Set a simple callback to print output
    def print_output(text: str):
        print(f"[MUD] {text}")

    simulator.set_output_callback(print_output)

    # List and run a scenario
    simulator.list_scenarios()
    print("Running 'combat' scenario...\n")
    simulator.run_scenario("combat")
