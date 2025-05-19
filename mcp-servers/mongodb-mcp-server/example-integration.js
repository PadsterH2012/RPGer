/**
 * Comprehensive Example of MongoDB MCP Server Integration with RPGer
 * 
 * This script demonstrates how to use the MongoDB MCP server 
 * in various scenarios within the RPGer application.
 */

const { use_mcp_tool } = require('@modelcontextprotocol/client');

class RPGerDatabaseManager {
  /**
   * Create a new character in the database
   * @param {Object} characterData Character details to be stored
   * @returns {Promise<Object>} Created character with database ID
   */
  static async createCharacter(characterData) {
    try {
      const result = await use_mcp_tool({
        server_name: 'mongodb-rpger',
        tool_name: 'insert_document',
        arguments: {
          collection: 'characters',
          document: {
            ...characterData,
            createdAt: new Date(),
            lastUpdated: new Date()
          }
        }
      });

      if (!result.success) {
        throw new Error(`Character creation failed: ${result.error}`);
      }

      console.log('Character created successfully:', result.insertedId);
      return result.data;
    } catch (error) {
      console.error('Error creating character:', error);
      throw error;
    }
  }

  /**
   * Fetch characters based on query criteria
   * @param {Object} query Search criteria
   * @param {Object} options Query options like limit and sorting
   * @returns {Promise<Array>} List of matching characters
   */
  static async findCharacters(query = {}, options = {}) {
    try {
      const result = await use_mcp_tool({
        server_name: 'mongodb-rpger',
        tool_name: 'query_collection',
        arguments: {
          collection: 'characters',
          query,
          limit: options.limit || 10,
          skip: options.skip || 0,
          sort: options.sort || { level: -1 }
        }
      });

      if (!result.success) {
        throw new Error(`Character search failed: ${result.error}`);
      }

      console.log(`Found ${result.count} characters`);
      return result.data;
    } catch (error) {
      console.error('Error finding characters:', error);
      throw error;
    }
  }

  /**
   * Update a character's details
   * @param {string} characterId Character's unique identifier
   * @param {Object} updateData Fields to update
   * @returns {Promise<Object>} Updated character details
   */
  static async updateCharacter(characterId, updateData) {
    try {
      const result = await use_mcp_tool({
        server_name: 'mongodb-rpger',
        tool_name: 'update_document',
        arguments: {
          collection: 'characters',
          id: characterId,
          update: { 
            $set: {
              ...updateData,
              lastUpdated: new Date()
            }
          }
        }
      });

      if (!result.success) {
        throw new Error(`Character update failed: ${result.error}`);
      }

      console.log('Character updated successfully');
      return result.data;
    } catch (error) {
      console.error('Error updating character:', error);
      throw error;
    }
  }

  /**
   * Delete a character from the database
   * @param {string} characterId Character's unique identifier
   * @returns {Promise<boolean>} Deletion success status
   */
  static async deleteCharacter(characterId) {
    try {
      const result = await use_mcp_tool({
        server_name: 'mongodb-rpger',
        tool_name: 'delete_document',
        arguments: {
          collection: 'characters',
          id: characterId
        }
      });

      if (!result.success) {
        throw new Error(`Character deletion failed: ${result.error}`);
      }

      console.log('Character deleted successfully');
      return true;
    } catch (error) {
      console.error('Error deleting character:', error);
      throw error;
    }
  }

  /**
   * Advanced query example: Find high-level characters
   * @returns {Promise<Array>} List of high-level characters
   */
  static async findHighLevelCharacters() {
    return this.findCharacters(
      { level: { $gte: 10 } },
      { 
        limit: 5, 
        sort: { experience: -1 } 
      }
    );
  }
}

// Example usage demonstrating the full workflow
async function characterManagementWorkflow() {
  try {
    // Create a new character
    const newCharacter = await RPGerDatabaseManager.createCharacter({
      name: 'Eldrin Stormwind',
      race: 'Half-Elf',
      class: 'Wizard',
      level: 5,
      experience: 6500,
      stats: {
        strength: 8,
        dexterity: 12,
        constitution: 10,
        intelligence: 18,
        wisdom: 14,
        charisma: 12
      }
    });

    // Update the character
    const updatedCharacter = await RPGerDatabaseManager.updateCharacter(
      newCharacter._id, 
      { level: 6, experience: 7200 }
    );

    // Find high-level characters
    const highLevelCharacters = await RPGerDatabaseManager.findHighLevelCharacters();
    console.log('High-Level Characters:', highLevelCharacters);

    // Optional: Delete the character
    // await RPGerDatabaseManager.deleteCharacter(newCharacter._id);

  } catch (error) {
    console.error('Workflow error:', error);
  }
}

// Export for potential use in other modules
module.exports = {
  RPGerDatabaseManager,
  characterManagementWorkflow
};

// Uncomment to run the workflow directly
// characterManagementWorkflow();