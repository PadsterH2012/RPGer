# OpenRouter Integration

## Overview

This document describes the integration between the RPGer application and the OpenRouter API. The integration enables the Dungeon Master Agent (DMA) and other AI agents to process commands and generate responses using various AI models available through OpenRouter.

## Components

The OpenRouter integration consists of the following components:

1. **OpenRouterAgentManager**: A Python class that handles connections to the OpenRouter API
2. **Configuration System**: Environment variables and configuration files for API key management
3. **Model Tier System**: A tiered approach to using different AI models based on complexity
4. **Agent Prompts**: Text files containing prompts for different AI agents
5. **Debug Messages**: Real-time debug information about OpenRouter connections

## OpenRouterAgentManager

The `OpenRouterAgentManager` class is the core component of the OpenRouter integration. It handles:

- API key management
- Model tier configuration
- API requests to OpenRouter
- Response processing
- Error handling
- Usage tracking

### Initialization

```python
from openrouter_agent_manager import OpenRouterAgentManager

# Initialize with default settings (API key from environment variables)
agent_manager = OpenRouterAgentManager()

# Or initialize with custom settings
agent_manager = OpenRouterAgentManager(
    api_key="your_api_key_here",
    model_tiers={
        'tier1': 'mistralai/mistral-7b-instruct',
        'tier2': 'anthropic/claude-instant-1.2',
        'tier3': 'anthropic/claude-3-haiku-20240307'
    }
)
```

## Configuration

### API Key Management

The OpenRouter API key is stored in a `.env` file in the backend directory. This file is not tracked in version control for security reasons. A `.env.example` file is provided as a template.

#### .env File

```
# OpenRouter API Key
# Get your API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_api_key_here
```

#### Loading the API Key

The API key is loaded using the `python-dotenv` library and accessed through the `config.py` module:

```python
# In config.py
from dotenv import load_dotenv
import os

load_dotenv()

def get_openrouter_api_key():
    """Get the OpenRouter API key from environment variables."""
    return os.getenv('OPENROUTER_API_KEY')
```

## Model Tier System

The OpenRouter integration uses a tiered approach to AI models, allowing for fallback to more powerful models when needed.

### Default Model Tiers

```python
model_tiers = {
    'tier1': 'mistralai/mistral-7b-instruct',
    'tier2': 'anthropic/claude-instant-1.2',
    'tier3': 'anthropic/claude-3-haiku-20240307'
}
```

### Model Cost Information

```python
model_costs = {
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
```

## Agent Prompts

Agent prompts are stored in text files in the `App/backend/prompts/` directory. Each agent has its own prompt file, which is loaded by the `OpenRouterAgentManager` class.

### Prompt File Naming Convention

- `dma_tier1_prompt.txt`: Dungeon Master Agent prompt for tier 1 models
- `cma_tier1_prompt.txt`: Character Management Agent prompt for tier 1 models
- etc.

### Loading Prompts

Prompts are loaded in the `SimpleADDTest` class:

```python
def _load_prompt(self, agent_type):
    """Load prompt for a specific agent"""
    prompt_path = os.path.join(PROMPT_DIR, f"{agent_type.lower()}_tier1_prompt.txt")
    try:
        with open(prompt_path, "r") as f:
            prompt_content = f.read()
            logger.info(f"Loaded prompt for {agent_type} from {prompt_path}")
            return prompt_content
    except FileNotFoundError:
        logger.warning(f"Warning: Prompt file {prompt_path} not found.")
        return f"You are the {agent_type} for AD&D 1st Edition."
```

## API Calls

### Making API Calls

The `_call_openrouter` method in the `OpenRouterAgentManager` class handles API calls to OpenRouter:

```python
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
        "HTTP-Referer": "https://rpger.app",
        "X-Title": "RPGer"
    }

    # Ensure model_name is a string
    if isinstance(model, dict) and 'model' in model:
        model_name = model['model']
    else:
        model_name = model

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

    # Make the API call
    response = requests.post(
        f"{self.base_url}/chat/completions",
        headers=headers,
        json=data
    )

    # Process the response
    if response.status_code == 200:
        return response.json()
    else:
        # Handle error
        return {"error": f"API error: {response.status_code}"}
```

## Debug Messages

The OpenRouter integration includes detailed debug messages to help diagnose connection issues:

```
DMA: No API key provided, attempting to load from environment variables
DMA: Successfully loaded OpenRouter API key from environment variables
DMA: Querying agent DMA with starting tier tier1
DMA: Using model: mistralai/mistral-7b-instruct
DMA: Attempting to connect to OpenRouter with model: mistralai/mistral-7b-instruct
DMA: API Key (first 4 chars): sk-o...
DMA: Successfully connected to OpenRouter API
DMA: Got response from OpenRouter: The dungeon is dark and damp...
```

## Error Handling

The OpenRouter integration includes robust error handling to deal with various failure scenarios:

1. **Missing API Key**: If the API key is missing, the system logs an error and returns a helpful message.
2. **Connection Errors**: If the connection to OpenRouter fails, the system logs the error and returns a helpful message.
3. **API Errors**: If the OpenRouter API returns an error, the system logs the error details and returns a helpful message.
4. **Invalid Models**: If an invalid model is specified, the system falls back to a reliable model.

## Usage Tracking

The `OpenRouterAgentManager` class tracks usage statistics for each model tier:

```python
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

        # Estimate cost
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
```

## Troubleshooting

### Common Issues

1. **"No models provided" Error**
   - **Cause**: The model parameter is not being passed correctly to the OpenRouter API
   - **Solution**: Ensure the model parameter is a string, not a dictionary or other object

2. **"API key not found" Error**
   - **Cause**: The OpenRouter API key is not set in the `.env` file
   - **Solution**: Add your OpenRouter API key to the `.env` file

3. **Connection Errors**
   - **Cause**: Network issues or OpenRouter API downtime
   - **Solution**: Check your internet connection and the OpenRouter status page

## Conclusion

The OpenRouter integration provides a robust and flexible way to use various AI models in the RPGer application. The tiered approach allows for fallback to more powerful models when needed, and the detailed debug messages help diagnose connection issues.
