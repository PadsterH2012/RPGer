"""
MongoDB schema definition for Player Character entities.
"""

character_schema = {
    "name": {
        "type": "string",
        "required": True,
        "description": "Character name"
    },
    "userId": {
        "bsonType": "objectId",
        "required": True,
        "description": "User ID must be an ObjectId and is required"
    },
    "campaign_id": {
        "type": "string",
        "description": "Associated campaign"
    },
    "race": {
        "type": "string",
        "required": True,
        "description": "Species"
    },
    "class": {
        "type": "string",
        "required": True,
        "description": "Character class"
    },
    "subclass": {
        "type": "string",
        "description": "Class specialization"
    },
    "level": {
        "type": "number",
        "required": True,
        "description": "Experience level"
    },
    "experience_points": {
        "type": "number",
        "description": "XP total"
    },
    "alignment": {
        "type": "string",
        "description": "Moral alignment"
    },
    "background": {
        "type": "string",
        "description": "Character origin"
    },
    "appearance": {
        "type": "string",
        "description": "Physical description"
    },
    "personality": {
        "type": "object",
        "properties": {
            "traits": {"type": "array", "items": {"type": "string"}},
            "ideals": {"type": "array", "items": {"type": "string"}},
            "bonds": {"type": "array", "items": {"type": "string"}},
            "flaws": {"type": "array", "items": {"type": "string"}}
        }
    },
    "stats": {
        "type": "object",
        "required": True,
        "properties": {
            "strength": {"type": "number"},
            "dexterity": {"type": "number"},
            "constitution": {"type": "number"},
            "intelligence": {"type": "number"},
            "wisdom": {"type": "number"},
            "charisma": {"type": "number"},
            "armor_class": {"type": "number"},
            "hit_points": {"type": "number"},
            "max_hit_points": {"type": "number"},
            "temporary_hit_points": {"type": "number"},
            "speed": {"type": "number"}
        }
    },
    "saving_throws": {
        "type": "object",
        "properties": {
            "strength": {"type": "number"},
            "dexterity": {"type": "number"},
            "constitution": {"type": "number"},
            "intelligence": {"type": "number"},
            "wisdom": {"type": "number"},
            "charisma": {"type": "number"}
        }
    },
    "skills": {
        "type": "object",
        "properties": {
            "acrobatics": {"type": "number"},
            "animal_handling": {"type": "number"},
            "arcana": {"type": "number"},
            "athletics": {"type": "number"},
            "deception": {"type": "number"},
            "history": {"type": "number"},
            "insight": {"type": "number"},
            "intimidation": {"type": "number"},
            "investigation": {"type": "number"},
            "medicine": {"type": "number"},
            "nature": {"type": "number"},
            "perception": {"type": "number"},
            "performance": {"type": "number"},
            "persuasion": {"type": "number"},
            "religion": {"type": "number"},
            "sleight_of_hand": {"type": "number"},
            "stealth": {"type": "number"},
            "survival": {"type": "number"}
        }
    },
    "abilities": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "source": {"type": "string"}
            }
        },
        "description": "Special capabilities"
    },
    "inventory": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "item_id": {"type": "string"},
                "quantity": {"type": "number"},
                "equipped": {"type": "boolean"},
                "notes": {"type": "string"}
            }
        },
        "description": "Possessions"
    },
    "spells": {
        "type": "object",
        "properties": {
            "spellcasting_ability": {"type": "string"},
            "spell_save_dc": {"type": "number"},
            "spell_attack_bonus": {"type": "number"},
            "cantrips": {"type": "array", "items": {"type": "string"}},
            "level_1": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_2": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_3": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_4": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_5": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_6": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_7": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_8": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            },
            "level_9": {
                "type": "object",
                "properties": {
                    "slots": {"type": "number"},
                    "slots_used": {"type": "number"},
                    "spells": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    "companions": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "type": {"type": "string"},
                "description": {"type": "string"},
                "stats": {"type": "object"}
            }
        },
        "description": "Animal companions/familiars"
    },
    "background_details": {
        "type": "string",
        "description": "Personal history"
    },
    "relationships": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "relationship_type": {"type": "string"},
                "description": {"type": "string"}
            }
        },
        "description": "Connections to NPCs"
    },
    "quests": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string"},
                "rewards": {"type": "array", "items": {"type": "string"}}
            }
        },
        "description": "Active storylines"
    },
    "journal_entries": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "date": {"type": "string", "description": "Entry date (ISO format)"}
            }
        },
        "description": "Character notes"
    },
    "embedding_references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chroma_collection": {"type": "string"},
                "embedding_id": {"type": "string"},
                "content_type": {"type": "string"},  # e.g., "background", "personality", "journal"
                "content_index": {"type": "number"}  # For multiple embeddings of the same type
            }
        },
        "description": "References to vector embeddings in Chroma"
    },
    "extended_properties": {
        "type": "object",
        "properties": {
            "character_development_goals": {"type": "array", "items": {"type": "string"}},
            "personal_quests": {"type": "array", "items": {"type": "string"}},
            "character_hooks": {"type": "array", "items": {"type": "string"}}
        }
    },
    "created_at": {
        "type": "string",
        "description": "Creation timestamp (ISO format)"
    },
    "updated_at": {
        "type": "string",
        "description": "Last update timestamp (ISO format)"
    }
}
