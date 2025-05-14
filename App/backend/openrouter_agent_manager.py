# openrouter_agent_manager.py
import os
import json
import requests
import logging
from typing import Dict, Any, Optional
import time

# Import config module
from config import get_openrouter_api_key

# Set up logging
logger = logging.getLogger('OpenRouterAgentManager')

class OpenRouterAgentManager:
    def __init__(self, api_key=None, model_tiers=None):
        """
        Initialize with OpenRouter API key and model tier configuration

        Args:
            api_key: The OpenRouter API key. If None, will try to get from environment variables.
            model_tiers: Dictionary of model tiers configuration. If None, will use defaults.
        """
        # If no API key provided, try to get from environment variables
        if api_key is None:
            logger.info("DMA: No API key provided, attempting to load from environment variables")
            api_key = get_openrouter_api_key()

            if api_key:
                logger.info("DMA: Successfully loaded OpenRouter API key from environment variables")
            else:
                logger.error("DMA: Failed to load OpenRouter API key from environment variables")

        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"

        # Check if API key is valid
        if not self.api_key:
            logger.error("DMA: No OpenRouter API key provided. OpenRouter functionality will not work.")
            print("ERROR: DMA: No OpenRouter API key provided. OpenRouter functionality will not work.")

        # Default model tiers if none provided
        self.model_tiers = model_tiers or {
            'tier1': 'mistralai/mistral-7b-instruct',
            'tier2': 'anthropic/claude-instant-1.2',
            'tier3': 'anthropic/claude-3-haiku-20240307'
        }

        # Model cost information
        self.model_costs = {
            'mistralai/mistral-7b-instruct': {
                'cost_per_1k_tokens': 0.0002,
                'output_cost_multiplier': 3,
                'max_tokens': 4096
            },
            'openai/gpt-3.5-turbo': {
                'cost_per_1k_tokens': 0.0005,
                'output_cost_multiplier': 2,
                'max_tokens': 4096
            },
            'anthropic/claude-instant-1.2': {
                'cost_per_1k_tokens': 0.0015,
                'output_cost_multiplier': 3,
                'max_tokens': 8192
            },
            'anthropic/claude-3-haiku-20240307': {
                'cost_per_1k_tokens': 0.003,
                'output_cost_multiplier': 4,
                'max_tokens': 16384
            }
        }

        self.agents = self._load_agents()
        self.usage_stats = {tier: 0 for tier in self.model_tiers}

    def _load_agents(self) -> Dict[str, Dict[str, str]]:
        """Load agent prompts from files with tier-specific variants"""
        agents = {}
        prompt_dir = "prompts"

        for filename in os.listdir(prompt_dir):
            if not filename.endswith("_prompt.txt"):
                continue

            parts = filename.split("_")
            if len(parts) >= 3 and parts[-2] in self.model_tiers:
                # Format: agent_tier_prompt.txt (e.g., dma_tier1_prompt.txt)
                agent_type = parts[0].upper()
                tier = parts[-2]

                if agent_type not in agents:
                    agents[agent_type] = {}

                with open(os.path.join(prompt_dir, filename), 'r') as f:
                    agents[agent_type][tier] = f.read()
            elif len(parts) == 2:
                # Legacy format without tier: agent_prompt.txt
                agent_type = parts[0].upper()

                if agent_type not in agents:
                    agents[agent_type] = {}

                with open(os.path.join(prompt_dir, filename), 'r') as f:
                    # Use the same prompt for all tiers as fallback
                    prompt = f.read()
                    for tier in self.model_tiers:
                        agents[agent_type][tier] = prompt

        return agents

    def query_agent(self, agent_type: str, message: str, context: Dict[str, Any] = None,
                    starting_tier: str = 'tier1', confidence_threshold: float = 0.7,
                    fallback_to_higher_tiers: bool = True) -> Dict[str, Any]:
        """
        Query an agent via OpenRouter.ai, starting with the specified tier
        and escalating if needed (based on confidence threshold)
        """
        logger.info(f"DMA: Querying agent {agent_type} with starting tier {starting_tier}")
        print(f"DMA: Querying agent {agent_type} with starting tier {starting_tier}")

        # Check if API key is available
        if not self.api_key:
            error_msg = "DMA: Cannot query agent - No OpenRouter API key available"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return {
                'error': True,
                'response': "Error: No OpenRouter API key available. Please configure the API key in the .env file."
            }

        if agent_type not in self.agents:
            error_msg = f"DMA: Unknown agent type: {agent_type}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)

        tiers = list(self.model_tiers.keys())
        try:
            start_idx = tiers.index(starting_tier)
        except ValueError:
            error_msg = f"DMA: Invalid tier: {starting_tier}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            raise ValueError(error_msg)

        # If we don't want to fall back, just use the specified tier
        if not fallback_to_higher_tiers:
            tier_range = [start_idx]
        else:
            tier_range = range(start_idx, len(tiers))

        last_response = None

        for tier_idx in tier_range:
            current_tier = tiers[tier_idx]

            # Skip if we don't have this tier for this agent
            if current_tier not in self.agents[agent_type]:
                continue

            model = self.model_tiers[current_tier]
            model_config = self.model_costs.get(model, {
                'max_tokens': 4096,
                'cost_per_1k_tokens': 0.0002,
                'output_cost_multiplier': 3
            })

            # Build the prompt
            prompt = self._build_prompt(agent_type, current_tier, message, context)

            # Make the API call to OpenRouter
            start_time = time.time()
            response_data = self._call_openrouter(
                prompt=prompt,
                model=model,
                max_tokens=model_config['max_tokens']
            )
            duration = time.time() - start_time

            # Process the response
            if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
                response_text = response_data['choices'][0]['message']['content']

                # Extract usage information
                usage = response_data.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', self._estimate_tokens(prompt))
                completion_tokens = usage.get('completion_tokens', self._estimate_tokens(response_text))
                total_tokens = prompt_tokens + completion_tokens

                # Calculate estimated cost
                input_cost = (prompt_tokens / 1000) * model_config['cost_per_1k_tokens']
                output_cost = (completion_tokens / 1000) * model_config['cost_per_1k_tokens'] * model_config['output_cost_multiplier']
                total_cost = input_cost + output_cost

                # Update usage statistics
                self.usage_stats[current_tier] += total_tokens

                # Log usage
                self._log_usage(agent_type, current_tier, model, prompt_tokens,
                               completion_tokens, total_cost, duration)

                # Try to estimate confidence (this is approximate without explicit confidence scores)
                confidence = self._estimate_confidence(response_text)

                # Store response
                last_response = {
                    'response': response_text,
                    'tier_used': current_tier,
                    'model_used': model,
                    'confidence': confidence,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'cost': total_cost,
                    'duration': duration
                }

                # If confidence meets threshold, return the response
                if confidence >= confidence_threshold:
                    return last_response
            else:
                # Handle API error
                last_response = {
                    'error': True,
                    'tier_used': current_tier,
                    'model_used': model,
                    'response': "Error: Failed to get valid response from OpenRouter API",
                    'raw_response': response_data
                }

        # If we got here, we tried all tiers and none met the threshold
        # Return the last response with a warning
        if last_response:
            last_response['warning'] = 'Low confidence across all attempted tiers'
        else:
            last_response = {
                'error': True,
                'response': "Error: No valid response from any tier",
            }

        return last_response

    def _call_openrouter(self, prompt: str, model: str, max_tokens: int = 1000,
                        temperature: float = 0.2) -> Dict[str, Any]:
        """Make an API call to OpenRouter.ai"""
        # Check if API key is available
        if not self.api_key:
            error_msg = "DMA: Cannot call OpenRouter API - No API key available"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return {"error": "No API key available"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rpger.app",  # Add a referer to help with API tracking
            "X-Title": "RPGer"  # Add a title to help with API tracking
        }

        # Check if model is a dictionary or string
        if isinstance(model, dict) and 'model' in model:
            model_name = model['model']
        else:
            model_name = model

        # Ensure model_name is a string
        if not isinstance(model_name, str):
            error_msg = f"DMA: Invalid model type: {type(model_name)}. Expected string."
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            model_name = "openai/gpt-3.5-turbo"  # Fallback to a reliable model

        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        logger.info(f"DMA: Calling OpenRouter API with model: {model_name}")
        print(f"DMA: Attempting to connect to OpenRouter with model: {model_name}")
        print(f"DMA: API Key (first 4 chars): {self.api_key[:4]}...")

        try:
            # Log the request data for debugging (without the full prompt for privacy)
            debug_data = data.copy()
            if 'messages' in debug_data and len(debug_data['messages']) > 0:
                for i, msg in enumerate(debug_data['messages']):
                    if 'content' in msg and isinstance(msg['content'], str) and len(msg['content']) > 100:
                        debug_data['messages'][i]['content'] = msg['content'][:100] + "... [truncated]"

            print(f"DMA: Request data: {json.dumps(debug_data, indent=2)}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )

            # Check if the response is successful
            if response.status_code == 200:
                logger.info(f"DMA: Successfully connected to OpenRouter API")
                print(f"DMA: Successfully connected to OpenRouter API")
                return response.json()
            else:
                error_msg = f"DMA: OpenRouter API returned error status code: {response.status_code}"
                logger.error(error_msg)
                print(f"ERROR: {error_msg}")

                # Try to get more details from the response
                try:
                    error_details = response.json()
                    error_detail_msg = f"DMA: OpenRouter API error details: {json.dumps(error_details, indent=2)}"
                    logger.error(error_detail_msg)
                    print(f"ERROR: {error_detail_msg}")
                    return {"error": f"API error: {response.status_code}", "details": error_details}
                except Exception as json_err:
                    error_text = response.text
                    print(f"ERROR: DMA: Could not parse error response as JSON: {str(json_err)}")
                    print(f"ERROR: DMA: Raw response: {error_text}")
                    return {"error": f"API error: {response.status_code}", "raw_response": error_text}

        except requests.exceptions.ConnectionError:
            error_msg = "DMA: Connection error when calling OpenRouter API - Check your internet connection"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return {"error": "Connection error"}

        except Exception as e:
            error_msg = f"DMA: Error calling OpenRouter API: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return {"error": f"Exception: {str(e)}"}

    def _build_prompt(self, agent_type: str, tier: str, message: str, context: Dict[str, Any]) -> str:
        """Build the complete prompt with tier-specific base prompt, message and context"""
        base_prompt = self.agents[agent_type][tier]

        # Add context information if available
        context_str = ""
        if context:
            # For efficiency, only include essential context based on tier
            if tier == 'tier1':
                # Minimal context for tier 1
                essential_keys = ['current_state', 'essential_rules']
                filtered_context = {k: context[k] for k in essential_keys if k in context}
                context_str = "CONTEXT:\n" + json.dumps(filtered_context, indent=2) + "\n\n"
            else:
                # More complete context for higher tiers
                context_str = "CONTEXT:\n" + json.dumps(context, indent=2) + "\n\n"

        # Add the message
        full_prompt = f"{base_prompt}\n\n{context_str}MESSAGE:\n{message}"

        return full_prompt

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for a string"""
        # Simple approximation: 4 characters per token
        return len(text) // 4

    def _estimate_confidence(self, response: str) -> float:
        """
        Estimate confidence from response content
        This is a simple heuristic approach since most models don't return confidence scores
        """
        # Check for hedging language
        hedging_phrases = ["I'm not sure", "might be", "possibly", "perhaps",
                          "I think", "may be", "could be", "I'm unsure"]

        confidence = 0.8  # Start with a default high confidence

        # Reduce confidence for each hedging phrase found
        for phrase in hedging_phrases:
            if phrase.lower() in response.lower():
                confidence -= 0.1

        # Check for explicit uncertainty markers
        if "I don't know" in response.lower() or "cannot determine" in response.lower():
            confidence -= 0.3

        # Look for confidence indicators in JSON responses
        if response.strip().startswith('{') and response.strip().endswith('}'):
            try:
                json_resp = json.loads(response)
                if 'confidence' in json_resp:
                    # Use explicit confidence if provided
                    return float(json_resp['confidence'])
                if 'success' in json_resp and not json_resp['success']:
                    confidence -= 0.3
            except:
                pass

        # Ensure confidence is in valid range
        return max(0.1, min(confidence, 1.0))

    def _log_usage(self, agent_type: str, tier: str, model: str,
                 prompt_tokens: int, completion_tokens: int, cost: float, duration: float):
        """Log usage statistics"""
        print(f"USAGE: {agent_type} ({tier} - {model})")
        print(f"  Tokens: {prompt_tokens} prompt + {completion_tokens} completion = {prompt_tokens + completion_tokens} total")
        print(f"  Cost: ${cost:.6f}, Duration: {duration:.2f}s")

    def get_usage_report(self) -> Dict[str, Any]:
        """Generate a usage report"""
        total_cost = 0
        total_tokens = 0

        tier_breakdown = {}

        for tier, tokens in self.usage_stats.items():
            model = self.model_tiers[tier]
            model_config = self.model_costs.get(model, {
                'cost_per_1k_tokens': 0.0002,
                'output_cost_multiplier': 3,
                'max_tokens': 4096
            })

            # Estimate cost (this is approximate since we don't track input/output separately in stats)
            # Assume 70% input, 30% output as a typical distribution
            input_tokens = int(tokens * 0.7)
            output_tokens = tokens - input_tokens

            tier_cost = (input_tokens / 1000) * model_config['cost_per_1k_tokens']
            tier_cost += (output_tokens / 1000) * model_config['cost_per_1k_tokens'] * model_config['output_cost_multiplier']

            tier_breakdown[tier] = {
                'tokens': tokens,
                'estimated_cost': tier_cost,
                'model': model
            }

            total_tokens += tokens
            total_cost += tier_cost

        return {
            'total_tokens': total_tokens,
            'total_estimated_cost': total_cost,
            'tier_breakdown': tier_breakdown
        }