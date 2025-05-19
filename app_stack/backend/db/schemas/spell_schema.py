"""
MongoDB schema definition for Spell entities.
"""

spell_schema = {
    "name": {
        "type": "string",
        "required": True,
        "description": "Spell name"
    },
    "level": {
        "type": "number",
        "required": True,
        "description": "Spell level"
    },
    "class": {
        "type": "array",
        "items": {"type": "string"},
        "required": True,
        "description": "Classes that can cast the spell"
    },
    "components": {
        "type": "object",
        "required": True,
        "properties": {
            "verbal": {"type": "boolean"},
            "somatic": {"type": "boolean"},
            "material": {"type": "boolean"},
            "material_components": {"type": "string"}
        }
    },
    "range": {
        "type": "string",
        "required": True,
        "description": "Effective range"
    },
    "duration": {
        "type": "string",
        "required": True,
        "description": "How long the spell lasts"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Spell effects"
    },
    "metadata": {
        "type": "object",
        "properties": {
            "school": {"type": "string"},
            "damage_type": {"type": "string"},
            "save": {"type": "string"},
            "casting_time": {"type": "string"},
            "concentration": {"type": "boolean"},
            "ritual": {"type": "boolean"}
        }
    },
    "embedding_references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chroma_collection": {"type": "string"},
                "embedding_id": {"type": "string"},
                "content_type": {"type": "string"},  # e.g., "description", "effects", "components"
                "content_index": {"type": "number"}  # For multiple embeddings of the same type
            }
        },
        "description": "References to vector embeddings in Chroma"
    },
    "extended_properties": {
        "type": "object",
        "properties": {
            "higher_level_casting": {"type": "string"},
            "ritual": {"type": "boolean"},
            "source": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}}
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
