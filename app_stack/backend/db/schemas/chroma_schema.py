"""
Schema definition for Chroma vector database collections.
"""

# Define the collections that will be used in Chroma
chroma_collections = {
    "monsters": {
        "description": "Monster descriptions and attributes",
        "metadata_fields": [
            "monster_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (description, habitat, ecology, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "name",  # Monster name
            "category",  # Monster category
            "challenge_rating"  # Challenge rating
        ]
    },
    "spells": {
        "description": "Spell descriptions and attributes",
        "metadata_fields": [
            "spell_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (description, effects, components, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "name",  # Spell name
            "level",  # Spell level
            "school",  # Magic school
            "class"  # Classes that can cast the spell
        ]
    },
    "items": {
        "description": "Item descriptions and attributes",
        "metadata_fields": [
            "item_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (description, magical_properties, lore, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "name",  # Item name
            "type",  # Item type
            "rarity"  # Item rarity
        ]
    },
    "npcs": {
        "description": "NPC descriptions and attributes",
        "metadata_fields": [
            "npc_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (description, personality, background, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "name",  # NPC name
            "race",  # NPC race
            "class",  # NPC class
            "location"  # NPC location
        ]
    },
    "characters": {
        "description": "Player character descriptions and attributes",
        "metadata_fields": [
            "character_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (background, personality, journal, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "name",  # Character name
            "player_id",  # Player ID
            "race",  # Character race
            "class"  # Character class
        ]
    },
    "campaign_notes": {
        "description": "Campaign notes and descriptions",
        "metadata_fields": [
            "note_id",  # Reference to MongoDB _id
            "content_type",  # Type of content (location, event, plot, etc.)
            "content_index",  # Index for multiple embeddings of the same type
            "campaign_id",  # Campaign ID
            "title",  # Note title
            "tags"  # Note tags
        ]
    }
}

# Define the embedding function to use
embedding_function = {
    "name": "text-embedding-ada-002",  # Default OpenAI embedding model
    "dimensions": 1536,  # Dimensions of the embedding vector
    "metadata": {
        "description": "OpenAI's text-embedding-ada-002 model",
        "provider": "openai"
    }
}

# Define the distance function to use for similarity search
distance_function = "cosine"  # Options: cosine, euclidean, dot_product

# Define the schema for embedding documents
embedding_document_schema = {
    "id": {
        "type": "string",
        "description": "Unique identifier for the embedding"
    },
    "document_id": {
        "type": "string",
        "description": "Reference to the MongoDB document ID"
    },
    "collection_name": {
        "type": "string",
        "description": "Name of the collection in Chroma"
    },
    "content": {
        "type": "string",
        "description": "Text content to be embedded"
    },
    "metadata": {
        "type": "object",
        "description": "Metadata for the embedding"
    },
    "embedding": {
        "type": "array",
        "items": {"type": "number"},
        "description": "Vector embedding of the content"
    }
}
