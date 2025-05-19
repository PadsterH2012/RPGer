"""
Generate test data for the RPGer database.
"""

import datetime
import logging
from bson import ObjectId
from . import get_mongodb_database

# Configure logging
logger = logging.getLogger(__name__)

# Sample monster data
test_monsters = [
    {
        "name": "Ancient Red Dragon",
        "category": "Dragon",
        "stats": {
            "frequency": "Very Rare",
            "no_appearing": "1",
            "armor_class": 22,
            "move": "40 ft., fly 80 ft.",
            "hit_dice": "28d20+252",
            "treasure_type": "H"
        },
        "description": "This colossal dragon's scales shimmer with a deep crimson hue. Heat ripples the air around its massive form, and smoke curls from its nostrils. Ancient red dragons are the most avaricious and cruel of all dragonkind, hoarding vast treasures and burning all who dare challenge their supremacy.",
        "metadata": {
            "type": "Dragon",
            "alignment": "Chaotic Evil",
            "challenge_rating": "24",
            "size": "Gargantuan",
            "languages": ["Common", "Draconic"],
            "senses": ["Blindsight 60 ft.", "Darkvision 120 ft."]
        },
        "habitat": {
            "primary_environments": ["Mountains", "Volcanoes"],
            "terrain_preferences": ["Volcanic Caves", "Mountain Peaks"],
            "climate_preferences": ["Hot"],
            "regional_distribution": ["Burning Mountains", "Ashen Wastes"],
            "specific_locations": ["Mount Infernus", "The Scorched Peaks"],
            "migration_patterns": "Sedentary, rarely leaves territory",
            "lair_description": "Vast volcanic caverns filled with treasure hoards and the charred remains of previous challengers."
        },
        "ecology": {
            "diet": "Carnivorous, preferring large mammals and humanoids",
            "predators": ["None"],
            "prey": ["Cattle", "Horses", "Humanoids", "Other Dragons"],
            "behavior": "Territorial, aggressive, and domineering",
            "lifecycle": "Lives for over a thousand years, reaching ancient status after 800 years",
            "socialization": "Solitary except during mating season",
            "interaction_with_civilization": "Demands tribute, destroys settlements that refuse"
        },
        "related_monsters": ["Adult Red Dragon", "Young Red Dragon", "Ancient Gold Dragon"],
        "encounter_suggestions": [
            "The dragon attacks a caravan carrying a valuable artifact",
            "The dragon demands tribute from a nearby town",
            "Adventurers stumble upon the dragon's lair while seeking shelter"
        ],
        "campaign_usage": {
            "plot_hooks": [
                "The dragon has kidnapped a noble's child",
                "The dragon possesses an artifact needed to stop a greater threat"
            ],
            "regional_variants": [
                "Volcanic dragons have lava-like blood",
                "Desert red dragons have adapted to sandstorms"
            ]
        },
        "extended_properties": {
            "legendary_actions": [
                "Tail Attack: The dragon makes a tail attack.",
                "Wing Attack (Costs 2 Actions): The dragon beats its wings, causing a powerful gust."
            ],
            "lair_actions": [
                "Magma erupts from a point on the ground",
                "Volcanic gases form a cloud of poison"
            ],
            "regional_effects": [
                "Small earthquakes are common within 6 miles of the dragon's lair",
                "Water sources within 1 mile of the lair are supernaturally warm and tainted by sulfur"
            ],
            "custom_abilities": [
                "Fire Aura: Creatures within 10 feet take 10 fire damage at the start of their turn",
                "Molten Scales: Melee attackers take 7 (2d6) fire damage when they hit the dragon"
            ]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    },
    {
        "name": "Goblin",
        "category": "Humanoid",
        "stats": {
            "frequency": "Common",
            "no_appearing": "4d6",
            "armor_class": 15,
            "move": "30 ft.",
            "hit_dice": "2d6",
            "treasure_type": "C"
        },
        "description": "This small, grotesque humanoid has a flat face with a broad nose, pointed ears, and a wide mouth filled with sharp teeth. Its skin is a sickly green, and it wears piecemeal armor cobbled together from scavenged materials. Goblins are known for their cunning, cruelty, and cowardice.",
        "metadata": {
            "type": "Humanoid",
            "alignment": "Neutral Evil",
            "challenge_rating": "1/4",
            "size": "Small",
            "languages": ["Common", "Goblin"],
            "senses": ["Darkvision 60 ft."]
        },
        "habitat": {
            "primary_environments": ["Forests", "Caves", "Ruins"],
            "terrain_preferences": ["Underground Warrens", "Abandoned Structures"],
            "climate_preferences": ["Temperate", "Cold"],
            "regional_distribution": ["Darkwood Forest", "Broken Tooth Mountains"],
            "specific_locations": ["Ratskull Warren", "The Abandoned Mines"],
            "migration_patterns": "Nomadic tribes following food sources",
            "lair_description": "Cramped, filthy warrens with crude traps and stolen goods."
        },
        "ecology": {
            "diet": "Omnivorous, with a preference for meat",
            "predators": ["Wolves", "Owlbears", "Humans"],
            "prey": ["Rodents", "Birds", "Livestock"],
            "behavior": "Opportunistic raiders who avoid direct confrontation",
            "lifecycle": "Mature quickly, living up to 50 years but rarely surviving past 20",
            "socialization": "Tribal, with strict hierarchies based on strength and cunning",
            "interaction_with_civilization": "Raid settlements for food and supplies"
        },
        "related_monsters": ["Hobgoblin", "Bugbear", "Orc"],
        "encounter_suggestions": [
            "A goblin ambush on a forest path",
            "A goblin raiding party attacking a farm",
            "Goblins using traps to capture travelers"
        ],
        "campaign_usage": {
            "plot_hooks": [
                "Goblins have stolen a valuable item from a local merchant",
                "A goblin tribe is being forced to raid by a more powerful creature"
            ],
            "regional_variants": [
                "Forest goblins use poison darts and are excellent climbers",
                "Cave goblins have pale skin and are sensitive to light"
            ]
        },
        "extended_properties": {
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "custom_abilities": [
                "Nimble Escape: The goblin can take the Disengage or Hide action as a bonus action on each of its turns."
            ]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
]

# Sample spell data
test_spells = [
    {
        "name": "Fireball",
        "level": 3,
        "class": ["Wizard", "Sorcerer"],
        "components": {
            "verbal": True,
            "somatic": True,
            "material": True,
            "material_components": "A tiny ball of bat guano and sulfur"
        },
        "range": "150 feet",
        "duration": "Instantaneous",
        "description": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one. The fire spreads around corners. It ignites flammable objects in the area that aren't being worn or carried.",
        "metadata": {
            "school": "Evocation",
            "damage_type": "Fire",
            "save": "Dexterity",
            "casting_time": "1 action",
            "concentration": False,
            "ritual": False
        },
        "extended_properties": {
            "higher_level_casting": "When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.",
            "source": "Player's Handbook",
            "tags": ["Damage", "Area Effect"]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    },
    {
        "name": "Healing Word",
        "level": 1,
        "class": ["Bard", "Cleric", "Druid"],
        "components": {
            "verbal": True,
            "somatic": False,
            "material": False,
            "material_components": ""
        },
        "range": "60 feet",
        "duration": "Instantaneous",
        "description": "A creature of your choice that you can see within range regains hit points equal to 1d4 + your spellcasting ability modifier. This spell has no effect on undead or constructs.",
        "metadata": {
            "school": "Evocation",
            "damage_type": "",
            "save": "",
            "casting_time": "1 bonus action",
            "concentration": False,
            "ritual": False
        },
        "extended_properties": {
            "higher_level_casting": "When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d4 for each slot level above 1st.",
            "source": "Player's Handbook",
            "tags": ["Healing", "Support"]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
]

# Sample item data
test_items = [
    {
        "name": "Vorpal Sword",
        "type": "Weapon",
        "subtype": "Longsword",
        "rarity": "Legendary",
        "description": "This legendary blade appears to be a finely crafted longsword with a razor-sharp edge that seems to distort the air around it. The hilt is adorned with intricate runes that pulse with a faint blue light. When wielded, the sword emits a soft humming sound that intensifies when it strikes a target.",
        "properties": {
            "damage": "1d8",
            "damage_type": "Slashing",
            "weight": 3,
            "properties": ["Versatile (1d10)", "Finesse"]
        },
        "magical_properties": {
            "bonus": 3,
            "abilities": [
                "On a natural 20 attack roll, the target is decapitated if it has a head",
                "Grants advantage on initiative rolls"
            ],
            "attunement": True,
            "charges": 0,
            "recharge": ""
        },
        "extended_properties": {
            "creator": "Archmage Zarathustra",
            "lore": "The Vorpal Sword was created during the Age of Dragons to combat the draconic threat. It has decapitated three ancient dragons in its history.",
            "variants": ["Vorpal Axe", "Vorpal Scimitar"],
            "value": 50000,
            "source": "Dungeon Master's Guide",
            "tags": ["Combat", "Legendary", "Decapitation"]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    },
    {
        "name": "Potion of Healing",
        "type": "Potion",
        "subtype": "Healing",
        "rarity": "Common",
        "description": "A small vial containing a red liquid that glimmers with magical energy. When consumed, it heals wounds and restores vitality to the drinker.",
        "properties": {
            "weight": 0.5
        },
        "magical_properties": {
            "abilities": ["Restores 2d4+2 hit points when consumed"],
            "attunement": False,
            "charges": 1,
            "recharge": "None"
        },
        "extended_properties": {
            "creator": "Various alchemists",
            "lore": "Healing potions are among the most common magical items in the world, created by apprentice alchemists as part of their training.",
            "variants": ["Potion of Greater Healing", "Potion of Superior Healing", "Potion of Supreme Healing"],
            "value": 50,
            "source": "Player's Handbook",
            "tags": ["Consumable", "Healing"]
        },
        "embedding_references": [],
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
]

# Sample NPC data
test_npcs = [
    {
        "name": "Harbormaster Selene",
        "race": "Human",
        "class": "Expert",
        "level": 5,
        "description": "Harbormaster Selene stands by the tide charts, her compact frame bent intently over the ink-marked parchment. The lantern light catches the silver in her braided hair as she traces the current patterns with a weathered finger.",
        "appearance": "A middle-aged woman with sun-weathered skin, silver-streaked dark hair in a practical braid, and sharp blue eyes that miss nothing. She wears sturdy, practical clothing with a harbormaster's insignia.",
        "personality": ["practical", "authoritative", "protective", "experienced"],
        "voice": {
            "speech_pattern": "Direct and technical, using maritime terminology naturally",
            "common_phrases": ["Mark my words", "I've seen it before", "Safety first, always"],
            "tone": "Firm but not unkind"
        },
        "background": "Selene has been the harbormaster for fifteen years, having worked her way up from a deckhand on merchant vessels. She knows every current, reef, and sandbar in the region and takes her responsibility for the safety of ships and sailors very seriously.",
        "stats": {
            "strength": 12,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 15,
            "wisdom": 16,
            "charisma": 13,
            "armor_class": 12,
            "hit_points": 38
        },
        "combat_style": "Selene avoids combat when possible but carries a short sword and knows how to use it. She prefers to talk her way out of dangerous situations.",
        "relationships": [
            {
                "name": "Captain Thorne",
                "relationship_type": "Rival",
                "description": "A smuggler who constantly tries to circumvent harbor regulations"
            },
            {
                "name": "Guildmaster Orlen",
                "relationship_type": "Ally",
                "description": "Head of the Merchant's Guild who respects Selene's dedication"
            }
        ],
        "knowledge": [
            "Detailed knowledge of local waters and navigation",
            "Shipping schedules and cargo manifests",
            "Weather patterns and seasonal changes",
            "Local smuggling operations (though she keeps this quiet)"
        ],
        "locations": [
            "Harbor Office",
            "The Salty Seagull Tavern",
            "Lighthouse Point"
        ],
        "hooks": [
            "Selene has noticed unusual ship movements that suggest smuggling of dangerous cargo",
            "She needs help investigating the disappearance of several fishing boats",
            "A valuable shipment has gone missing, and she suspects foul play"
        ],
        "behavior_patterns": {
            "interaction_patterns": [
                {
                    "pattern_id": "IP-042",
                    "pattern_type": "authority-expertise",
                    "trigger_conditions": "When safety or regulations are questioned",
                    "response_tendencies": "Provides historical examples that validate her position"
                },
                {
                    "pattern_id": "IP-089",
                    "pattern_type": "mentorship",
                    "trigger_conditions": "When interacting with inexperienced sailors",
                    "response_tendencies": "Offers advice wrapped in personal anecdotes"
                }
            ],
            "decision_making": {
                "priorities": ["safety of vessels", "efficiency of harbor", "upholding regulations"],
                "risk_tolerance": "Low for others' safety, moderate for personal risk",
                "moral_framework": "Utilitarian with strong sense of duty"
            },
            "emotional_responses": {
                "primary_emotions": ["concern", "pride", "frustration"],
                "emotional_triggers": {
                    "concern": "Dangerous weather or reckless behavior",
                    "pride": "Well-run harbor operations, successful navigation of difficult conditions",
                    "frustration": "Bureaucratic obstacles, disregard for expertise"
                },
                "expression_style": "Restrained but visible in body language and tone"
            }
        },
        "novel_extraction_metadata": {
            "description_pattern_id": "PD-127",
            "dialogue_pattern_ids": ["DP-089", "DP-142"],
            "personality_pattern_id": "PP-056",
            "behavior_pattern_ids": ["BP-042", "BP-089"],
            "transformation_methods": ["context shift", "gender variation", "role adaptation"]
        },
        "embedding_references": [],
        "extended_properties": {
            "faction_memberships": ["Harbor Authority", "Sailor's Guild"],
            "secrets": ["Knows the location of a sunken treasure ship", "Has a map of hidden smuggler's coves"],
            "possessions": ["Harbormaster's seal", "Antique sextant", "Logbook of unusual maritime events"]
        },
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
]

# Sample character data
test_characters = [
    {
        "name": "Thorne Ironheart",
        "userId": ObjectId("507f1f77bcf86cd799439011"),
        "campaign_id": "campaign456",
        "race": "Dwarf",
        "class": "Fighter",
        "subclass": "Battle Master",
        "level": 5,
        "experience_points": 6500,
        "alignment": "Lawful Good",
        "background": "Soldier",
        "appearance": "Stocky dwarf with a thick red beard braided with metal rings. Deep-set eyes and a scar across his left cheek. Wears well-maintained plate armor adorned with his clan's symbols.",
        "personality": {
            "traits": ["Brave", "Loyal", "Stubborn"],
            "ideals": ["Honor", "Duty", "Protection"],
            "bonds": ["My clan comes first", "I owe my life to my commander"],
            "flaws": ["I never back down from a challenge", "I'm suspicious of strangers"]
        },
        "stats": {
            "strength": 16,
            "dexterity": 12,
            "constitution": 16,
            "intelligence": 10,
            "wisdom": 13,
            "charisma": 8,
            "armor_class": 18,
            "hit_points": 49,
            "max_hit_points": 49,
            "temporary_hit_points": 0,
            "speed": 25
        },
        "saving_throws": {
            "strength": 6,
            "dexterity": 1,
            "constitution": 6,
            "intelligence": 0,
            "wisdom": 1,
            "charisma": -1
        },
        "skills": {
            "athletics": 6,
            "intimidation": 2,
            "perception": 4,
            "survival": 4
        },
        "abilities": [
            {
                "name": "Second Wind",
                "description": "Regain 1d10 + fighter level hit points as a bonus action. Once per short rest.",
                "source": "Fighter"
            },
            {
                "name": "Action Surge",
                "description": "Take an additional action on your turn. Once per short rest.",
                "source": "Fighter"
            },
            {
                "name": "Combat Superiority",
                "description": "4 superiority dice (d8) for maneuvers.",
                "source": "Battle Master"
            }
        ],
        "inventory": [
            {
                "item_id": "warhammer001",
                "quantity": 1,
                "equipped": True,
                "notes": "Family heirloom"
            },
            {
                "item_id": "platearmor001",
                "quantity": 1,
                "equipped": True,
                "notes": "Well-maintained"
            },
            {
                "item_id": "potion_healing001",
                "quantity": 3,
                "equipped": False,
                "notes": ""
            }
        ],
        "spells": {},
        "companions": [],
        "background_details": "Thorne served in the Ironheart Clan's elite guard for ten years before setting out to seek glory and honor for his clan. He fought in the Battle of Broken Ridge, where he saved his commander's life but received the scar on his cheek.",
        "relationships": [
            {
                "name": "Commander Durgath",
                "relationship_type": "Mentor",
                "description": "Former commander who taught Thorne everything he knows about combat"
            },
            {
                "name": "Elindra Swiftarrow",
                "relationship_type": "Ally",
                "description": "Elven ranger who once saved Thorne from an ambush"
            }
        ],
        "quests": [
            {
                "title": "Reclaim the Ironheart Hammer",
                "description": "Find and recover the legendary hammer of the Ironheart Clan, stolen by frost giants.",
                "status": "In Progress",
                "rewards": ["Clan recognition", "Magical weapon"]
            }
        ],
        "journal_entries": [
            {
                "title": "Strange Dreams",
                "content": "I've been having recurring dreams about a mountain cave filled with blue light. Could it be related to the Ironheart Hammer?",
                "date": (datetime.datetime.utcnow() - datetime.timedelta(days=5)).isoformat()
            }
        ],
        "embedding_references": [],
        "extended_properties": {
            "character_development_goals": ["Become clan leader", "Master the art of dwarven smithing"],
            "personal_quests": ["Find my long-lost brother"],
            "character_hooks": ["Has recurring visions of an ancient dwarven city"]
        },
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat()
    }
]

# Function to insert test data
def insert_test_data():
    """Insert test data into MongoDB."""
    db = get_mongodb_database()

    try:
        # Insert monsters
        if db.monsters.count_documents({}) == 0:
            db.monsters.insert_many(test_monsters)
            logger.info(f"Inserted {len(test_monsters)} test monsters")

        # Insert spells
        if db.spells.count_documents({}) == 0:
            db.spells.insert_many(test_spells)
            logger.info(f"Inserted {len(test_spells)} test spells")

        # Insert items
        if db.items.count_documents({}) == 0:
            db.items.insert_many(test_items)
            logger.info(f"Inserted {len(test_items)} test items")

        # Insert NPCs
        if db.npcs.count_documents({}) == 0:
            db.npcs.insert_many(test_npcs)
            logger.info(f"Inserted {len(test_npcs)} test NPCs")

        # Insert characters
        if db.characters.count_documents({}) == 0:
            db.characters.insert_many(test_characters)
            logger.info(f"Inserted {len(test_characters)} test characters")

        logger.info("Test data insertion complete")
    except Exception as e:
        logger.error(f"Failed to insert test data: {e}")
        raise

# Function to generate embeddings for test data
def generate_test_embeddings():
    """Generate embeddings for test data and store in Chroma."""
    # This is a placeholder function
    # In a real implementation, you would:
    # 1. Retrieve documents from MongoDB
    # 2. Generate embeddings using an embedding model
    # 3. Store the embeddings in Chroma with references to MongoDB documents
    # 4. Update the MongoDB documents with references to the Chroma embeddings

    logger.info("Test embeddings generation would happen here")
    logger.info("This requires an embedding model and is not implemented in this test script")

# Main function to initialize test data
def init_test_data():
    """Initialize test data in MongoDB and Chroma."""
    try:
        insert_test_data()
        # generate_test_embeddings()  # Uncomment when implemented
        logger.info("Test data initialization complete")
    except Exception as e:
        logger.error(f"Test data initialization failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_test_data()
