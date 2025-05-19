/**
 * Example usage of the MongoDB MCP server with RPGer
 * 
 * This file demonstrates how to use the MongoDB MCP server tools
 * from within the RPGer application.
 */

// Example function to fetch characters from the database
async function fetchCharacters() {
  try {
    const result = await use_mcp_tool({
      server_name: "mongodb-rpger",
      tool_name: "query_collection",
      arguments: {
        collection: "characters",
        query: {},
        limit: 10
      }
    });
    
    if (result.success) {
      console.log(`Found ${result.count} characters:`);
      console.log(result.data);
      return result.data;
    } else {
      console.error("Error fetching characters:", result.error);
      return [];
    }
  } catch (error) {
    console.error("Error calling MCP tool:", error);
    return [];
  }
}

// Example function to create a new character
async function createCharacter(characterData) {
  try {
    const result = await use_mcp_tool({
      server_name: "mongodb-rpger",
      tool_name: "insert_document",
      arguments: {
        collection: "characters",
        document: characterData
      }
    });
    
    if (result.success) {
      console.log("Character created successfully with ID:", result.insertedId);
      return result.data;
    } else {
      console.error("Error creating character:", result.error);
      return null;
    }
  } catch (error) {
    console.error("Error calling MCP tool:", error);
    return null;
  }
}

// Example function to update a character
async function updateCharacter(characterId, updateData) {
  try {
    const result = await use_mcp_tool({
      server_name: "mongodb-rpger",
      tool_name: "update_document",
      arguments: {
        collection: "characters",
        id: characterId,
        update: { $set: updateData }
      }
    });
    
    if (result.success) {
      console.log("Character updated successfully");
      return result.data;
    } else {
      console.error("Error updating character:", result.error);
      return null;
    }
  } catch (error) {
    console.error("Error calling MCP tool:", error);
    return null;
  }
}

// Example function to delete a character
async function deleteCharacter(characterId) {
  try {
    const result = await use_mcp_tool({
      server_name: "mongodb-rpger",
      tool_name: "delete_document",
      arguments: {
        collection: "characters",
        id: characterId
      }
    });
    
    if (result.success) {
      console.log("Character deleted successfully");
      return true;
    } else {
      console.error("Error deleting character:", result.error);
      return false;
    }
  } catch (error) {
    console.error("Error calling MCP tool:", error);
    return false;
  }
}

// Example function to list all collections in the database
async function listCollections() {
  try {
    const result = await use_mcp_tool({
      server_name: "mongodb-rpger",
      tool_name: "list_collections",
      arguments: {}
    });
    
    if (result.success) {
      console.log("Available collections:");
      console.log(result.collections);
      return result.collections;
    } else {
      console.error("Error listing collections:", result.error);
      return [];
    }
  } catch (error) {
    console.error("Error calling MCP tool:", error);
    return [];
  }
}

// Example usage
async function exampleUsage() {
  // List all collections
  const collections = await listCollections();
  
  // Create a new character
  const newCharacter = {
    name: "Aragorn",
    class: "Ranger",
    level: 10,
    race: "Human",
    stats: {
      strength: 16,
      dexterity: 14,
      constitution: 15,
      intelligence: 12,
      wisdom: 14,
      charisma: 16
    },
    inventory: [
      { name: "Andúril", type: "weapon", damage: "1d10+2" },
      { name: "Ranger's Cloak", type: "armor", armorClass: 2 }
    ]
  };
  
  const createdCharacter = await createCharacter(newCharacter);
  
  if (createdCharacter) {
    // Update the character
    await updateCharacter(createdCharacter._id, {
      level: 11,
      "stats.strength": 17
    });
    
    // Fetch all characters
    const characters = await fetchCharacters();
    
    // Delete the character
    // await deleteCharacter(createdCharacter._id);
  }
}

// Note: This is just an example and won't run directly
// It demonstrates how to use the MongoDB MCP server tools
console.log("This is an example file showing how to use the MongoDB MCP server");