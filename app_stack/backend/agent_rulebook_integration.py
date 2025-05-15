import os
import re
import logging
from typing import Dict, Any, List, Optional
from rulebook_manager import RuleBookManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AgentRulebookIntegration')

class AgentRulebookIntegration:
    """
    Integrates the RuleBookManager with the agent system to allow agents to query rulebooks.
    """

    def __init__(self, reference_dir: str = "Reference_Material"):
        """Initialize the integration with the reference directory."""
        logger.info("Initializing AgentRulebookIntegration")
        self.rulebook_manager = RuleBookManager(reference_dir, load_all=True)
        logger.info("RuleBookManager initialized")

    def query_rules(self, query: str, agent_type: str = None, max_results: int = 3) -> str:
        """
        Query the rulebooks based on agent type and query.

        Args:
            query: The query string
            agent_type: Type of agent (DMA, CRA, etc.)
            max_results: Maximum number of results to return

        Returns:
            Formatted string with relevant rules
        """
        logger.info(f"Agent {agent_type} querying rules: {query}")

        # Determine query type based on agent and query content
        if agent_type == "CRA" or "combat" in query.lower():
            results = self.rulebook_manager.query_combat_rules(query, max_results)
        elif agent_type == "CMA" or "character" in query.lower():
            results = self.rulebook_manager.query_character_rules(query, max_results)
        elif agent_type == "NEA" or any(keyword in query.lower() for keyword in ["npc", "monster", "encounter", "treasure"]):
            results = self.rulebook_manager.query_npc_rules(query, max_results)
        elif agent_type == "EEA" or any(keyword in query.lower() for keyword in ["exploration", "movement", "search", "trap"]):
            results = self.rulebook_manager.query_exploration_rules(query, max_results)
        elif agent_type == "WEA" or any(keyword in query.lower() for keyword in ["time", "weather", "environment", "resource"]):
            results = self.rulebook_manager.query_world_rules(query, max_results)
        else:
            results = self.rulebook_manager.query(query, max_results)

        # Format results for agent consumption
        formatted_results = self.rulebook_manager.format_results_for_agent(results)

        logger.info(f"Found {len(results)} relevant rules")
        return formatted_results

    def enhance_agent_prompt(self, base_prompt: str, query: str = None,
                            agent_type: str = None, max_results: int = 2) -> str:
        """
        Enhance an agent prompt with relevant rules.

        Args:
            base_prompt: The base prompt for the agent
            query: Optional query to find relevant rules (if None, uses the agent type)
            agent_type: Type of agent (DMA, CRA, etc.)
            max_results: Maximum number of results to include

        Returns:
            Enhanced prompt with relevant rules
        """
        # If no specific query, use default queries based on agent type
        if not query:
            if agent_type == "CRA":
                query = "combat resolution rules AD&D"
            elif agent_type == "CMA":
                query = "character creation and advancement rules AD&D"
            elif agent_type == "DMA":
                query = "dungeon master responsibilities and game flow AD&D"
            elif agent_type == "NEA":
                query = "NPC reactions, monster tactics, and encounter generation AD&D"
            elif agent_type == "EEA":
                query = "dungeon exploration, movement, searching, and wilderness travel AD&D"
            elif agent_type == "WEA":
                query = "time tracking, weather, environment, and resource management AD&D"
            else:
                query = "general rules AD&D"

        # Get relevant rules
        rules = self.query_rules(query, agent_type, max_results)

        # Enhance the prompt with rules
        enhanced_prompt = f"{base_prompt}\n\nRELEVANT RULES AND REFERENCES:\n{rules}"

        return enhanced_prompt

    def get_combat_workflow(self) -> str:
        """
        Get the complete combat workflow as a formatted string.

        Returns:
            Formatted string with the combat workflow
        """
        workflow_sections = self.rulebook_manager.get_workflow("Combat")

        if not workflow_sections:
            return "Combat workflow not found."

        # Sort sections by their position in the original document
        workflow_sections.sort(key=lambda x: x['id'])

        # Format the workflow
        formatted = "# AD&D 1st Edition Combat Workflow\n\n"
        for section in workflow_sections:
            # Remove the title from the section text if it appears in the title
            section_text = section['text']
            section_title = section['title'].replace('#', '').strip()
            if section_text.startswith(section_title):
                section_text = section_text[len(section_title):].strip()

            formatted += f"{section['title']}\n{section_text}\n\n"

        return formatted

    def get_specific_rule(self, rule_name: str) -> str:
        """
        Get a specific rule by name.

        Args:
            rule_name: Name of the rule to retrieve

        Returns:
            Formatted string with the rule
        """
        # Search for the rule by name
        results = self.rulebook_manager.query(rule_name, max_results=1)

        if not results:
            return f"Rule '{rule_name}' not found."

        # Format the rule
        rule = results[0]
        formatted = f"# {rule['title']}\n\n"
        formatted += f"Source: {rule['source']}\n\n"
        formatted += rule['text']

        return formatted
