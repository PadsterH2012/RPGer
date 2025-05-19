Instructions for AI Agent: Creating Monster Records in MongoDB
Task Overview
Create detailed monster records in MongoDB for all demon and devil types from the Monster Manual, following the established schema and maintaining consistency with existing records.

Preparation Steps
Examine existing monster records in the database to understand the schema structure
View the source markdown files for each monster type to gather accurate information
Note any existing demon or devil records to avoid duplication
Identify relationships between monster types for cross-referencing
Record Creation Process
For each monster, create a MongoDB document with the following structure:
name: Use ALL CAPS format (e.g., "DEMON, TYPE II (HEZROU)")
category: Set to "Fiend" for all demons and devils
description: Copy exact wording from source material, maintaining all details
stats: Include frequency, no_appearing, armor_class, move, hit_dice, hit_points, etc.
path: Reference to the source markdown file
metadata: Include source, type, alignment, size, intelligence, etc.
habitat: Document primary environments and lair descriptions
ecology: Include diet, predators, prey, behavior, socialization, etc.
related_monsters: List all related demon/devil types for cross-referencing
campaign_usage: Add 2-3 plot hooks for each monster
abilities: List all special abilities categorized by type (attack, defense, special)
For each ability, include:
name: Descriptive name of the ability
description: Detailed explanation of how the ability works
type: Categorize as "attack", "defense", or "special"
For general information records (e.g., "DEMON (GENERAL INFORMATION)"):
Set category to "Reference" rather than "Monster"
Include comprehensive information about the monster type
List all subtypes in the related_monsters field
Quality Control
After creating each record, verify the insertion was successful
Ensure consistent formatting across all records
Verify all special abilities and powers are accurately documented
Check that cross-references are properly established between related monsters
Maintain exact wording from source material without embellishment
Verification
After completing all records, query the database to confirm all types are present
Count the total number of monsters to verify the additions were successful
Generate a summary of all created records
Important Guidelines
Maintain consistency with existing records in formatting and structure
Copy text exactly from source material without adding interpretations
Create comprehensive cross-references between related monster types
Include detailed abilities with accurate mechanics
Add practical campaign usage suggestions for each monster
Document immunities, resistances, and vulnerabilities in separate ability entries
Use timestamps for created_at and updated_at fields
MongoDB Commands
Use db.monsters.insertOne({...}) to create each record
Use db.monsters.find({name: {$regex: /DEMON|DEVIL/}}, {name: 1, _id: 0}).sort({name: 1}) to verify records
Use db.monsters.countDocuments() to check the total number of records
Follow these instructions precisely to create comprehensive, accurate, and consistent monster records that will enhance the RPGer system.