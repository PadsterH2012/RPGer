"""
MongoDB schema definition for Item entities.
"""

item_schema = {
    "name": {
        "type": "string",
        "required": True,
        "description": "Item name"
    },
    "type": {
        "type": "string",
        "required": True,
        "description": "Item category (e.g., Weapon, Armor, Potion)"
    },
    "subtype": {
        "type": "string",
        "description": "Specific type (e.g., Longsword, Plate Armor)"
    },
    "rarity": {
        "type": "string",
        "description": "How rare the item is (e.g., Common, Uncommon, Rare)"
    },
    "description": {
        "type": "string",
        "required": True,
        "description": "Item description"
    },
    "properties": {
        "type": "object",
        "properties": {
            "damage": {"type": "string"},
            "damage_type": {"type": "string"},
            "weight": {"type": "number"},
            "properties": {"type": "array", "items": {"type": "string"}},
            "armor_class": {"type": "number"},
            "strength_requirement": {"type": "number"},
            "stealth_disadvantage": {"type": "boolean"}
        }
    },
    "magical_properties": {
        "type": "object",
        "properties": {
            "bonus": {"type": "number"},
            "abilities": {"type": "array", "items": {"type": "string"}},
            "attunement": {"type": "boolean"},
            "charges": {"type": "number"},
            "recharge": {"type": "string"}
        }
    },
    "embedding_references": {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "chroma_collection": {"type": "string"},
                "embedding_id": {"type": "string"},
                "content_type": {"type": "string"},  # e.g., "description", "magical_properties", "lore"
                "content_index": {"type": "number"}  # For multiple embeddings of the same type
            }
        },
        "description": "References to vector embeddings in Chroma"
    },
    "extended_properties": {
        "type": "object",
        "properties": {
            "creator": {"type": "string"},
            "lore": {"type": "string"},
            "variants": {"type": "array", "items": {"type": "string"}},
            "value": {"type": "number"},
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
