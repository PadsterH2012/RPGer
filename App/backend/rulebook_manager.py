import os
import re
import json
from collections import defaultdict
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RuleBookManager')

class RuleBookManager:
    """
    Manages AD&D rulebooks and provides query functionality for agents.
    This class handles loading, indexing, and querying markdown files containing game rules.
    """

    def __init__(self, reference_dir: str = "Reference_Material", load_all: bool = True):
        """
        Initialize the RuleBookManager with the reference directory.

        Args:
            reference_dir: Directory containing reference materials
            load_all: Whether to load all rulebooks on initialization
        """
        self.reference_dir = reference_dir
        self.sections = []  # List of all sections from all rulebooks
        self.index = defaultdict(list)  # Word -> list of section IDs
        self.category_index = defaultdict(list)  # Category -> list of section IDs
        self.workflow_index = defaultdict(list)  # Workflow -> list of section IDs
        self.loaded_files = set()  # Track which files have been loaded

        # Load all rulebooks on initialization if requested
        if load_all:
            self.load_all_rulebooks()

    def load_all_rulebooks(self) -> None:
        """Load all rulebooks from the reference directory."""
        logger.info(f"Loading rulebooks from {self.reference_dir}")

        # Walk through the reference directory
        for root, _, files in os.walk(self.reference_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    self.add_rulebook(file_path)

        logger.info(f"Loaded {len(self.sections)} sections from {len(self.loaded_files)} files")
        logger.info(f"Indexed {len(self.index)} unique terms")
        logger.info(f"Created {len(self.category_index)} category indices")
        logger.info(f"Created {len(self.workflow_index)} workflow indices")

    def add_rulebook(self, file_path: str) -> None:
        """Add a rulebook file to the index."""
        if file_path in self.loaded_files:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Extract relative path for categorization
            rel_path = os.path.relpath(file_path, self.reference_dir)
            path_parts = rel_path.split(os.sep)

            # Determine category and subcategory
            category = path_parts[0] if len(path_parts) > 0 else "Unknown"
            subcategory = path_parts[1] if len(path_parts) > 1 else "General"

            # Special handling for workflows
            is_workflow = "WorkFlows" in path_parts
            workflow_type = path_parts[1] if is_workflow and len(path_parts) > 1 else None

            # Split into sections (by headers)
            sections = self._split_into_sections(content)

            # Process each section
            for section_title, section_text in sections:
                section_id = len(self.sections)

                # Create section metadata
                section = {
                    'id': section_id,
                    'title': section_title,
                    'text': section_text,
                    'source': file_path,
                    'category': category,
                    'subcategory': subcategory,
                    'is_workflow': is_workflow,
                    'workflow_type': workflow_type
                }

                # Add to sections list
                self.sections.append(section)

                # Index words in title and text
                self._index_section(section_id, section_title, section_text)

                # Add to category index
                self.category_index[category].append(section_id)

                # Add to workflow index if applicable
                if is_workflow and workflow_type:
                    self.workflow_index[workflow_type].append(section_id)

            # Mark file as loaded
            self.loaded_files.add(file_path)

        except Exception as e:
            logger.error(f"Error loading rulebook {file_path}: {e}")

    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """Split content into sections based on markdown headers."""
        # Pattern to match headers and their content
        pattern = r'(#+\s+.+?)\n(.*?)(?=\n#+\s+|\Z)'
        matches = re.finditer(pattern, content, re.DOTALL)

        sections = []
        for match in matches:
            header = match.group(1).strip()
            text = match.group(2).strip()
            sections.append((header, text))

        # If no sections found (no headers), treat the whole content as one section
        if not sections and content.strip():
            filename = os.path.basename(content[:100])  # Use beginning of content as fallback title
            sections.append((f"Content from {filename}", content.strip()))

        return sections

    def _index_section(self, section_id: int, title: str, text: str) -> None:
        """Index a section by its words."""
        # Combine title and text for indexing
        combined_text = f"{title} {text}"

        # Extract words, normalize to lowercase, remove punctuation
        words = set(re.findall(r'\b\w+\b', combined_text.lower()))

        # Add section_id to index for each word
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.index[word].append(section_id)

    def query(self, question: str, max_results: int = 5,
              category_filter: Optional[str] = None,
              workflow_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query the rulebooks for information related to the question.

        Args:
            question: The question to search for
            max_results: Maximum number of results to return
            category_filter: Optional filter for specific category
            workflow_filter: Optional filter for specific workflow type

        Returns:
            List of relevant sections
        """
        # Extract keywords from question
        keywords = set(re.findall(r'\b\w+\b', question.lower()))
        keywords = {word for word in keywords if len(word) > 2}

        # Score sections based on keyword matches
        section_scores = defaultdict(int)

        # Apply filters if specified
        candidate_sections = set()
        if category_filter:
            candidate_sections.update(self.category_index.get(category_filter, []))
        if workflow_filter:
            candidate_sections.update(self.workflow_index.get(workflow_filter, []))

        # If no filters applied, consider all sections
        if not candidate_sections:
            candidate_sections = set(range(len(self.sections)))

        # Score sections based on keyword matches
        for word in keywords:
            if word in self.index:
                for section_id in self.index[word]:
                    if section_id in candidate_sections:
                        section_scores[section_id] += 1

        # Sort by score
        ranked_sections = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)

        # Return top results
        results = []
        for section_id, score in ranked_sections[:max_results]:
            section = self.sections[section_id]
            results.append({
                'title': section['title'],
                'text': section['text'],
                'source': section['source'],
                'category': section['category'],
                'subcategory': section['subcategory'],
                'relevance_score': score,
                'is_workflow': section['is_workflow'],
                'workflow_type': section['workflow_type']
            })

        return results

    def query_combat_rules(self, question: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Specialized query for combat rules."""
        return self.query(question, max_results, workflow_filter="Combat")

    def query_character_rules(self, question: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Specialized query for character rules."""
        return self.query(question, max_results, workflow_filter="Character_Generation")

    def query_npc_rules(self, question: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Specialized query for NPC and encounter rules."""
        # First try to find specific NPC rules
        results = self.query(question, max_results, category_filter="Books")

        # Filter results to prioritize NPC-related content
        keywords = ["npc", "monster", "creature", "encounter", "reaction", "morale", "treasure"]
        filtered_results = []

        for result in results:
            text = (result.get('title', '') + ' ' + result.get('text', '')).lower()
            if any(keyword in text for keyword in keywords):
                filtered_results.append(result)

        # If we found specific results, return them
        if filtered_results:
            return filtered_results[:max_results]

        # Otherwise, return general results
        return results

    def query_exploration_rules(self, question: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Specialized query for exploration rules."""
        # Try to find exploration-specific content
        exploration_results = self.query(question, max_results, workflow_filter="Exploration")

        # If we have workflow results, return them
        if exploration_results:
            return exploration_results

        # Otherwise, search more broadly
        keywords = ["exploration", "movement", "search", "trap", "door", "wilderness", "travel"]
        results = self.query(question, max_results)

        filtered_results = []
        for result in results:
            text = (result.get('title', '') + ' ' + result.get('text', '')).lower()
            if any(keyword in text for keyword in keywords):
                filtered_results.append(result)

        # If we found specific results, return them
        if filtered_results:
            return filtered_results[:max_results]

        # Otherwise, return general results
        return results

    def query_world_rules(self, question: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """Specialized query for world and environment rules."""
        # Try to find specific content about the world and environment
        keywords = ["time", "weather", "light", "darkness", "resource", "encounter", "environment"]
        results = self.query(question, max_results)

        filtered_results = []
        for result in results:
            text = (result.get('title', '') + ' ' + result.get('text', '')).lower()
            if any(keyword in text for keyword in keywords):
                filtered_results.append(result)

        # If we found specific results, return them
        if filtered_results:
            return filtered_results[:max_results]

        # Otherwise, return general results
        return results

    def get_workflow(self, workflow_name: str) -> List[Dict[str, Any]]:
        """Get all sections for a specific workflow."""
        workflow_sections = self.workflow_index.get(workflow_name, [])
        return [self.sections[section_id] for section_id in workflow_sections]

    def format_results_for_agent(self, results: List[Dict[str, Any]]) -> str:
        """Format query results for agent consumption."""
        if not results:
            return "No relevant rules found."

        formatted = "RELEVANT RULES:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"--- RULE {i} ---\n"
            formatted += f"Title: {result['title']}\n"
            formatted += f"Source: {os.path.basename(result['source'])}\n"
            formatted += f"Category: {result['category']}/{result['subcategory']}\n\n"
            formatted += f"{result['text']}\n\n"

        return formatted
