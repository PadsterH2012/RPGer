#!/usr/bin/env python3
"""
Validator script for RPGer database schemas and test data.

This script validates:
1. Schema definitions for correctness
2. Test data against the schemas
3. Highlights any issues that need to be fixed
"""

import sys
import json
import datetime
import logging
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker
from .schemas import (
    monster_schema,
    spell_schema,
    item_schema,
    npc_schema,
    character_schema
)
from .test_data import (
    test_monsters,
    test_spells,
    test_items,
    test_npcs,
    test_characters
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def convert_schema_to_jsonschema(schema):
    """Convert our MongoDB schema format to JSON Schema format."""
    properties = {}
    required = []

    for field_name, field_def in schema.items():
        # Copy the field definition
        properties[field_name] = field_def.copy()

        # Check if the field is required
        if "required" in field_def and field_def["required"] is True:
            required.append(field_name)
            # Remove the required flag from the property definition
            del properties[field_name]["required"]

        # Convert MongoDB types to JSON Schema types
        if "type" in field_def:
            if field_def["type"] == "string":
                properties[field_name]["type"] = "string"
            elif field_def["type"] == "number":
                properties[field_name]["type"] = "number"
            elif field_def["type"] == "boolean":
                properties[field_name]["type"] = "boolean"
            elif field_def["type"] == "object":
                properties[field_name]["type"] = "object"
            elif field_def["type"] == "array":
                properties[field_name]["type"] = "array"
            elif field_def["type"] == "date":
                # Convert date type to string
                properties[field_name]["type"] = "string"

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": True
    }

def validate_schema(schema_name, schema, test_data, quiet=False):
    """Validate test data against a schema."""
    if not quiet:
        logger.info(f"Validating {schema_name} schema...")

    # Convert our schema to JSON Schema format
    json_schema = convert_schema_to_jsonschema(schema)

    # Create a validator with format checking
    validator = Draft7Validator(json_schema, format_checker=FormatChecker())

    # Validate each test data item
    valid_count = 0
    invalid_count = 0
    issues = []

    for i, item in enumerate(test_data):
        try:
            validator.validate(item)
            valid_count += 1
        except ValidationError as e:
            invalid_count += 1
            issues.append({
                "index": i,
                "item_name": item.get("name", f"Item {i}"),
                "error": str(e),
                "path": ".".join(str(p) for p in e.path)
            })

    # Report results
    if not quiet:
        logger.info(f"{schema_name}: {valid_count} valid, {invalid_count} invalid")

        if invalid_count > 0:
            logger.warning(f"Issues found in {schema_name}:")
            for issue in issues:
                logger.warning(f"  Item: {issue['item_name']}")
                logger.warning(f"  Path: {issue['path']}")
                logger.warning(f"  Error: {issue['error']}")
                logger.warning("")

    return valid_count, invalid_count, issues

def check_date_fields(test_data):
    """Check date fields in test data for proper format."""
    logger.info("Checking date fields...")

    date_issues = []

    for collection_name, collection_data in [
        ("monsters", test_monsters),
        ("spells", test_spells),
        ("items", test_items),
        ("npcs", test_npcs),
        ("characters", test_characters)
    ]:
        for i, item in enumerate(collection_data):
            # Check created_at and updated_at
            for field in ["created_at", "updated_at"]:
                if field in item:
                    if not isinstance(item[field], str):
                        date_issues.append({
                            "collection": collection_name,
                            "item_name": item.get("name", f"Item {i}"),
                            "field": field,
                            "issue": f"Field should be a string in ISO format, got {type(item[field]).__name__}"
                        })
                    elif isinstance(item[field], str):
                        try:
                            # Try to parse the date string
                            datetime.datetime.fromisoformat(item[field])
                        except ValueError:
                            date_issues.append({
                                "collection": collection_name,
                                "item_name": item.get("name", f"Item {i}"),
                                "field": field,
                                "issue": f"Invalid ISO format: {item[field]}"
                            })

            # Check journal entries in characters
            if collection_name == "characters" and "journal_entries" in item:
                for j, entry in enumerate(item["journal_entries"]):
                    if "date" in entry:
                        if not isinstance(entry["date"], str):
                            date_issues.append({
                                "collection": collection_name,
                                "item_name": item.get("name", f"Item {i}"),
                                "field": f"journal_entries[{j}].date",
                                "issue": f"Field should be a string in ISO format, got {type(entry['date']).__name__}"
                            })
                        elif isinstance(entry["date"], str):
                            try:
                                # Try to parse the date string
                                datetime.datetime.fromisoformat(entry["date"])
                            except ValueError:
                                date_issues.append({
                                    "collection": collection_name,
                                    "item_name": item.get("name", f"Item {i}"),
                                    "field": f"journal_entries[{j}].date",
                                    "issue": f"Invalid ISO format: {entry['date']}"
                                })

    # Report results
    if date_issues:
        logger.warning(f"Found {len(date_issues)} date field issues:")
        for issue in date_issues:
            logger.warning(f"  Collection: {issue['collection']}")
            logger.warning(f"  Item: {issue['item_name']}")
            logger.warning(f"  Field: {issue['field']}")
            logger.warning(f"  Issue: {issue['issue']}")
            logger.warning("")
    else:
        logger.info("All date fields are valid.")

    return date_issues

def check_embedding_references(test_data):
    """Check embedding_references fields in test data."""
    logger.info("Checking embedding_references fields...")

    embedding_issues = []

    for collection_name, collection_data in [
        ("monsters", test_monsters),
        ("spells", test_spells),
        ("items", test_items),
        ("npcs", test_npcs),
        ("characters", test_characters)
    ]:
        for i, item in enumerate(collection_data):
            if "embedding_references" in item:
                if not isinstance(item["embedding_references"], list):
                    embedding_issues.append({
                        "collection": collection_name,
                        "item_name": item.get("name", f"Item {i}"),
                        "issue": f"embedding_references should be a list, got {type(item['embedding_references']).__name__}"
                    })
                else:
                    for j, ref in enumerate(item["embedding_references"]):
                        if not isinstance(ref, dict):
                            embedding_issues.append({
                                "collection": collection_name,
                                "item_name": item.get("name", f"Item {i}"),
                                "issue": f"embedding_references[{j}] should be a dictionary, got {type(ref).__name__}"
                            })
                        else:
                            for field in ["chroma_collection", "embedding_id", "content_type"]:
                                if field not in ref:
                                    embedding_issues.append({
                                        "collection": collection_name,
                                        "item_name": item.get("name", f"Item {i}"),
                                        "issue": f"embedding_references[{j}] missing required field: {field}"
                                    })

    # Report results
    if embedding_issues:
        logger.warning(f"Found {len(embedding_issues)} embedding reference issues:")
        for issue in embedding_issues:
            logger.warning(f"  Collection: {issue['collection']}")
            logger.warning(f"  Item: {issue['item_name']}")
            logger.warning(f"  Issue: {issue['issue']}")
            logger.warning("")
    else:
        logger.info("All embedding_references fields are valid.")

    return embedding_issues

def main():
    """Main validation function."""
    logger.info("Starting schema and test data validation...")

    # Validate schemas and test data
    validation_results = [
        validate_schema("Monster", monster_schema, test_monsters),
        validate_schema("Spell", spell_schema, test_spells),
        validate_schema("Item", item_schema, test_items),
        validate_schema("NPC", npc_schema, test_npcs),
        validate_schema("Character", character_schema, test_characters)
    ]

    # Check date fields
    date_issues = check_date_fields({
        "monsters": test_monsters,
        "spells": test_spells,
        "items": test_items,
        "npcs": test_npcs,
        "characters": test_characters
    })

    # Check embedding references
    embedding_issues = check_embedding_references({
        "monsters": test_monsters,
        "spells": test_spells,
        "items": test_items,
        "npcs": test_npcs,
        "characters": test_characters
    })

    # Summarize results
    total_valid = sum(result[0] for result in validation_results)
    total_invalid = sum(result[1] for result in validation_results)
    total_issues = sum(len(result[2]) for result in validation_results)

    logger.info("Validation summary:")
    logger.info(f"  Valid items: {total_valid}")
    logger.info(f"  Invalid items: {total_invalid}")
    logger.info(f"  Schema issues: {total_issues}")
    logger.info(f"  Date issues: {len(date_issues)}")
    logger.info(f"  Embedding issues: {len(embedding_issues)}")

    if total_invalid > 0 or len(date_issues) > 0 or len(embedding_issues) > 0:
        logger.error("Validation failed. Please fix the issues before importing data.")
        return 1
    else:
        logger.info("Validation successful! Data is ready to be imported.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
