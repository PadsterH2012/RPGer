"""
Schema definitions for the RPGer database.
"""

from .monster_schema import monster_schema
from .spell_schema import spell_schema
from .item_schema import item_schema
from .npc_schema import npc_schema
from .character_schema import character_schema
from .chroma_schema import chroma_collections, embedding_function, distance_function, embedding_document_schema

# Export all schemas
__all__ = [
    'monster_schema',
    'spell_schema',
    'item_schema',
    'npc_schema',
    'character_schema',
    'chroma_collections',
    'embedding_function',
    'distance_function',
    'embedding_document_schema'
]
