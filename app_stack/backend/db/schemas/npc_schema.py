"""
MongoDB schema definition for NPC entities.
"""

npc_schema = {
    "name": {
        "type": "string",
        "required": True,
        "description": "NPC name"
    },
    "race": {
        "type": "string",
        "required": True,
        "description": "Species"
    },
    "class": {
        "type": "string",
        "description": "Character class"
    },
    "level": {
        "type": "number",
        "description": "Experience level"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Physical description"
    },
    "appearance": {
        "type": "string",
        "description": "Detailed physical traits"
    },
    "personality": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Character traits"
    },
    "voice": {
        "type": "object",
        "properties": {
            "speech_pattern": {"type": "string"},
            "common_phrases": {"type": "array", "items": {"type": "string"}},
            "tone": {"type": "string"}
        }
    },
    "background": {
        "type": "string",
        "description": "Personal history"
    },
    "stats": {
        "type": "object",
        "properties": {
            "strength": {"type": "number"},
            "dexterity": {"type": "number"},
            "constitution": {"type": "number"},
            "intelligence": {"type": "number"},
            "wisdom": {"type": "number"},
            "charisma": {"type": "number"},
            "armor_class": {"type": "number"},
            "hit_points": {"type": "number"}
        }
    },
    "combat_style": {
        "type": "string",
        "description": "Fighting approach"
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
        "description": "Connections to others"
    },
    "knowledge": {
        "type": "array",
        "items": {"type": "string"},
        "description": "What they know"
    },
    "locations": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Where they can be found"
    },
    "hooks": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Adventure hooks"
    },
    "behavior_patterns": {
        "type": "object",
        "properties": {
            "interaction_patterns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pattern_id": {"type": "string"},
                        "pattern_type": {"type": "string"},
                        "trigger_conditions": {"type": "string"},
                        "response_tendencies": {"type": "string"}
                    }
                }
            },
            "decision_making": {
                "type": "object",
                "properties": {
                    "priorities": {"type": "array", "items": {"type": "string"}},
                    "risk_tolerance": {"type": "string"},
                    "moral_framework": {"type": "string"}
                }
            },
            "emotional_responses": {
                "type": "object",
                "properties": {
                    "primary_emotions": {"type": "array", "items": {"type": "string"}},
                    "emotional_triggers": {"type": "object"},
                    "expression_style": {"type": "string"}
                }
            },
            "routine_behaviors": {
                "type": "object",
                "properties": {
                    "daily_routines": {"type": "array", "items": {"type": "string"}},
                    "quirks": {"type": "array", "items": {"type": "string"}},
                    "comfort_behaviors": {"type": "array", "items": {"type": "string"}},
                    "stress_behaviors": {"type": "array", "items": {"type": "string"}}
                }
            },
            "social_dynamics": {
                "type": "object",
                "properties": {
                    "leadership_style": {"type": "string"},
                    "group_role": {"type": "string"},
                    "status_signals": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    },
    "novel_extraction_metadata": {
        "type": "object",
        "properties": {
            "description_pattern_id": {"type": "string"},
            "dialogue_pattern_ids": {"type": "array", "items": {"type": "string"}},
            "personality_pattern_id": {"type": "string"},
            "behavior_pattern_ids": {"type": "array", "items": {"type": "string"}},
            "transformation_methods": {"type": "array", "items": {"type": "string"}}
        }
    },
    "embedding_references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chroma_collection": {"type": "string"},
                "embedding_id": {"type": "string"},
                "content_type": {"type": "string"},  # e.g., "description", "personality", "background"
                "content_index": {"type": "number"}  # For multiple embeddings of the same type
            }
        },
        "description": "References to vector embeddings in Chroma"
    },
    "extended_properties": {
        "type": "object",
        "properties": {
            "faction_memberships": {"type": "array", "items": {"type": "string"}},
            "secrets": {"type": "array", "items": {"type": "string"}},
            "possessions": {"type": "array", "items": {"type": "string"}}
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
