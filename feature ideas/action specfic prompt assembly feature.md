# Action-Specific Prompt Assembly Feature for Multi-Agent RPG System

## Overview
The Action-Specific Prompt Assembly feature dynamically constructs lean, targeted prompts by extracting and assembling relevant components from both successful and unsuccessful API interactions. This system optimizes performance, relevance, and continuous improvement by generating minimalist prompts that contain only the elements necessary for the specific action being performed by each specialized agent in our RPG system.

## Problem Statement
Current approaches to agent prompting in our multi-agent RPG system often include:

- Excessive boilerplate instructions
- Redundant context information
- Overly generalized parameter sets
- Inefficient use of token space
- Repetitive response patterns
- Inconsistent handling of similar actions
- Difficulty maintaining prompt quality across multiple specialized agents

These issues lead to higher API costs, slower response times, reduced effectiveness when handling specialized tasks, and inconsistent player experiences.

## Solution: Component-Based Prompt Assembly with Error Feedback Loop
Our solution implements a dynamic prompt assembly system that:

- Analyzes both successful and unsuccessful API interactions
- Extracts effective prompt components by action type and agent role
- Records error patterns and problematic responses
- Stores these components and error patterns in a vector database for efficient retrieval
- Assembles minimal, targeted prompts on demand based on detected player intent
- Continuously refines prompts based on performance feedback

## Key Features

### 1. Intelligent Component Extraction

- **Action Classification**: Automatically categorizes past API calls by intent, action type, and agent role (DMA, CMA, CRA, etc.)
- **Success Analysis**: Identifies components from high-performing interactions across all agents
- **Error Pattern Recognition**: Catalogs problematic responses and their associated prompt components
- **Parameter Optimization**: Extracts only parameters that influenced successful outcomes
- **Instruction Distillation**: Refines instruction sets to remove redundancy
- **Agent-Specific Optimization**: Tailors components to each agent's specific role and requirements

### 2. Vector-Based Component Storage with Error Repository

- **Semantic Embedding**: Converts prompt components and error patterns into vector representations
- **Efficient Indexing**: Optimizes retrieval speed using vector similarity
- **Metadata Enrichment**: Maintains performance metrics, context requirements, and error frequencies
- **Versioning**: Tracks component evolution and effectiveness over time
- **Error Classification**: Categorizes failure modes (repetitive phrasing, assuming success, etc.)
- **Cross-Agent Pattern Recognition**: Identifies common issues across different agent types

### 3. Dynamic Prompt Assembly with Error Avoidance

- **Intent Recognition**: Detects required action from player input and routes to appropriate agent
- **Relevance Ranking**: Selects most appropriate components based on query similarity
- **Error Pattern Avoidance**: Actively excludes components associated with similar past failures
- **Minimal Construction**: Includes only essential elements required for the specific action
- **Response Adaptation**: Adjusts verbosity and detail based on action complexity
- **Agent-Specific Templates**: Uses specialized base templates for each agent type (DMA, CMA, etc.)

### 4. Continuous Optimization through Feedback Loop

- **Performance Tracking**: Monitors success rates of assembled prompts across all agents
- **Error Analysis**: Identifies recurring patterns in failed or suboptimal responses
- **Automatic Refinement**: Updates component effectiveness scores based on outcomes
- **A/B Testing**: Compares variations of prompt components for optimization
- **Usage Analytics**: Provides insights on token efficiency and response quality
- **Player Satisfaction Metrics**: Tracks indirect indicators of response quality
- **Cross-Agent Learning**: Applies successful patterns from one agent to others where applicable

## Technical Architecture

```
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│ Successful API  │    │ Component         │    │ Player Action   │
│ Interactions    │──▶│ Extraction Engine │◀───│ Intent Analysis │
└─────────────────┘    └───────────────────┘    └─────────────────┘
       │                        │
       │                        ▼
┌─────────────────┐    ┌───────────────────┐
│ Failed API      │    │ Vector Database   │
│ Interactions    │───▶│ Components +      │
└─────────────────┘    │ Error Patterns    │
                       └───────────────────┘
                               │
                               ▼
┌─────────────────┐    ┌───────────────────┐    ┌─────────────────┐
│ Performance     │◀───│ Agent-Specific    │───▶│ API Call with   │
│ Monitoring      │    │ Prompt Assembly   │    │ Lean Prompt     │
└─────────────────┘    └───────────────────┘    └─────────────────┘
       │                                                │
       │                                                ▼
       │                                        ┌─────────────────┐
       │                                        │ Agent Response  │
       │                                        │ Evaluation      │
       │                                        └─────────────────┘
       │                                                │
       └────────────────────────────────────────────────┘
```

### Agent-Specific Processing Flow

1. **Player Input Processing**:
   - Player action is received and analyzed for intent
   - System determines which specialized agent should handle the action (DMA, CMA, CRA, etc.)
   - Action is classified by type and complexity

2. **Prompt Component Selection**:
   - System retrieves agent-specific base template (e.g., DMA template for action acknowledgment)
   - Relevant components are selected based on action type and past performance
   - Error patterns associated with similar actions are identified and avoided

3. **Agent-Optimized Assembly**:
   - Components are assembled into a lean, targeted prompt
   - Agent-specific formatting and requirements are applied
   - Final prompt is optimized for token efficiency

4. **Response Evaluation**:
   - Agent response is analyzed for quality metrics
   - Success or failure is determined based on predefined criteria
   - Response patterns are extracted and stored
   - Feedback is routed to the appropriate component repositories
## Implementation Plan

### Phase 1: Agent Analysis and Component Extraction System

- Analyze existing agent prompts (DMA, CMA, CRA, etc.) to identify common patterns
- Develop JSON parsing and response analysis framework
- Implement action classification algorithms with agent-specific categorization
- Create component extraction pipeline with error pattern identification
- Build storage schema for component and error pattern database

### Phase 2: Vector Database Integration with Error Repository

- Select optimal vector database technology for both components and error patterns
- Implement embedding and vectorization process for multi-agent system
- Develop efficient querying and retrieval systems with error avoidance
- Create indexing and metadata management for cross-agent pattern recognition
- Build error classification and storage system

### Phase 3: Agent-Specific Assembly Engine Development

- Build player action analysis and intent detection system
- Develop agent routing logic based on action type
- Create agent-specific component selection algorithms
- Implement error pattern avoidance mechanisms
- Build prompt assembly logic with agent-specific templates
- Implement serialization to API-compatible format

### Phase 4: Feedback Loop and Continuous Optimization

- Develop response quality evaluation system
- Implement multi-faceted feedback loops for component refinement
- Create error pattern extraction and classification system
- Build agent-specific performance dashboards
- Implement A/B testing framework for continuous improvement
- Develop cross-agent learning mechanisms

## Expected Benefits

- **Token Efficiency**: 30-50% decrease in token usage per API call across all agents
- **Response Quality**: 25-40% improvement in response appropriateness and variety
- **Error Reduction**: 40-60% decrease in common response errors (repetition, assuming success)
- **Performance Improvement**: 20-40% reduction in response latency
- **Accuracy Enhancement**: 15-25% improvement in action completion success
- **Cross-Agent Consistency**: 30-45% improvement in consistent handling of similar actions
- **Scalability**: Support for growing action library and agent types without performance degradation
- **Player Experience**: More natural, varied, and appropriate agent responses

## Success Metrics

- **Token Efficiency**: Average token count per successful action by agent type
- **Response Variety**: Percentage of unique response patterns for similar actions
- **Error Rate**: Frequency of identified error patterns in agent responses
- **Response Time**: Latency from player action to completed agent response
- **Success Rate**: Percentage of correctly executed actions by agent type
- **Coverage**: Percentage of player intents successfully mapped to specific actions
- **Cross-Agent Consistency**: Consistency score for similar actions across different agents
- **Player Satisfaction**: Indirect metrics of player engagement and satisfaction

## Next Steps

- Conduct technical feasibility assessment with current DMA prompt as test case
- Select vector database and embedding technologies for component storage
- Develop proof-of-concept with DMA and one additional agent (e.g., CMA)
- Perform initial benchmarking against current system using our test suite
- Create initial error pattern repository based on identified DMA response issues
- Design feedback collection mechanism for ongoing prompt improvement
