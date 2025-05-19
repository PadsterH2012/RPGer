"""
MongoDB schema definition for Monster entities.
"""

monster_schema = {
    "name": {
        "type": "string",
        "required": True,
        "description": "Monster name"
    },
    "category": {
        "type": "string",
        "required": True,
        "description": "Classification (e.g., Aberration, Beast, Dragon)"
    },
    "stats": {
        "type": "object",
        "required": True,
        "properties": {
            "frequency": {"type": "string"},
            "no_appearing": {"type": "string"},
            "armor_class": {"type": "number"},
            "move": {"type": "string"},
            "hit_dice": {"type": "string"},
            "treasure_type": {"type": "string"}
        }
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Textual description"
    },
    "path": {
        "type": "string",
        "description": "Reference to source file"
    },
    "metadata": {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "alignment": {"type": "string"},
            "challenge_rating": {"type": "string"},
            "size": {"type": "string"},
            "languages": {"type": "array", "items": {"type": "string"}},
            "senses": {"type": "array", "items": {"type": "string"}}
        }
    },
    "habitat": {
        "type": "object",
        "properties": {
            "primary_environments": {"type": "array", "items": {"type": "string"}},
            "terrain_preferences": {"type": "array", "items": {"type": "string"}},
            "climate_preferences": {"type": "array", "items": {"type": "string"}},
            "regional_distribution": {"type": "array", "items": {"type": "string"}},
            "specific_locations": {"type": "array", "items": {"type": "string"}},
            "migration_patterns": {"type": "string"},
            "lair_description": {"type": "string"}
        }
    },
    "ecology": {
        "type": "object",
        "properties": {
            "diet": {"type": "string"},
            "predators": {"type": "array", "items": {"type": "string"}},
            "prey": {"type": "array", "items": {"type": "string"}},
            "behavior": {"type": "string"},
            "lifecycle": {"type": "string"},
            "socialization": {"type": "string"},
            "interaction_with_civilization": {"type": "string"}
        }
    },
    "embedding_references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chroma_collection": {"type": "string"},
                "embedding_id": {"type": "string"},
                "content_type": {"type": "string"},  # e.g., "description", "habitat", "ecology"
                "content_index": {"type": "number"}  # For multiple embeddings of the same type
            }
        },
        "description": "References to vector embeddings in Chroma"
    },
    "related_monsters": {
        "type": "array",
        "items": {"type": "string"},
        "description": "References to similar creatures"
    },
    "encounter_suggestions": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Pre-built encounter ideas"
    },
    "campaign_usage": {
        "type": "object",
        "properties": {
            "plot_hooks": {"type": "array", "items": {"type": "string"}},
            "regional_variants": {"type": "array", "items": {"type": "string"}}
        }
    },
    "extended_properties": {
        "type": "object",
        "properties": {
            "legendary_actions": {"type": "array", "items": {"type": "string"}},
            "lair_actions": {"type": "array", "items": {"type": "string"}},
            "regional_effects": {"type": "array", "items": {"type": "string"}},
            "custom_abilities": {"type": "array", "items": {"type": "string"}}
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
