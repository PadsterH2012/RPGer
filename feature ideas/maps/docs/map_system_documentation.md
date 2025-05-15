# Map Generation System Documentation

## Overview

The map generation system creates procedurally generated maps with multiple layers of information for use in RPG games. The system uses a seed-based approach to ensure reproducibility while allowing for controlled randomization.

## Core Components

### 1. Seed-Based Layered Map System

The system is built around a core `MapSystem` class that manages multiple layers, each responsible for a specific aspect of the map (terrain, rivers, settlements, etc.). Each layer can be generated with a modified seed derived from the base seed, allowing for controlled variation.

### 2. Layer Types

The system includes several specialized layers:
- **Terrain Layer**: Handles elevation, land/water boundaries, and terrain types
- **Rivers Layer**: Creates rivers that follow elevation gradients
- **Political Layer**: Generates territories and political boundaries
- **Settlements Layer**: Places cities, towns, and villages with connecting roads
- **Weather Layer**: Simulates regional weather patterns

### 3. Journey System

A journey planning system allows for plotting paths between locations, with natural route finding that follows roads when available and creates realistic travel segments.

### 4. Player Exploration Map

A "fog of war" system that only reveals areas of the world that players have personally explored or learned about through in-game means. This creates a sense of discovery as players gradually uncover the world map through their adventures.

## Scripts

### 1. `seed_based_layered_map_system.py`

**Purpose**: Defines the core map system architecture and base layer classes.

**Key Components**:
- `MapSystem`: Main class for managing multiple map layers
- `BaseLayer`: Abstract base class for all layer types
- `TerrainLayer`: Implementation of terrain generation

### 2. `additional_map_layers.py`

**Purpose**: Implements specialized map layers that build upon the terrain layer.

**Key Components**:
- `RiversLayer`: Generates rivers following elevation gradients
- `PoliticalLayer`: Creates territories and political boundaries
- `SettlementsLayer`: Places settlements and connecting roads

### 3. `map_weather_journey_test.py`

**Purpose**: Demonstrates the full map system with weather and journey planning.

**Key Components**:
- `WeatherSystem`: Simulates regional weather patterns
- `JourneyPlanner`: Plans routes between locations
- Map visualization and rendering functions

### 4. `test_imports.py`

**Purpose**: Simple test script to verify that all map system components can be imported correctly.

### 5. `exploration_map_layer.py`

**Purpose**: Implements the player exploration map system with "fog of war" functionality.

**Key Components**:
- `ExplorationMapLayer`: Tracks which areas players have explored, know about, or have mapped
- Visualization functions for rendering the player's current knowledge of the world

## Detailed Function Documentation

### `seed_based_layered_map_system.py`

#### `MapSystem` Class

```python
class MapSystem:
    def __init__(self, base_seed=None, width=512, height=512):
        """
        Initialize a new map system with the given base seed.

        Parameters:
        - base_seed: Integer seed for map generation (random if None)
        - width: Width of the map in pixels
        - height: Height of the map in pixels
        """
```

```python
def add_layer(self, layer_id, layer_type, seed_modifier=0, parameters=None):
    """
    Add a new layer to the map system.

    Parameters:
    - layer_id: Unique identifier for the layer
    - layer_type: Type of layer to create (terrain, rivers, etc.)
    - seed_modifier: Value to add to base_seed for this layer
    - parameters: Dictionary of parameters for layer initialization

    Returns:
    - The newly created layer
    """
```

```python
def generate_all_layers(self):
    """
    Generate all layers in the correct dependency order.

    Returns:
    - Self for method chaining
    """
```

```python
def get_layer(self, layer_id):
    """
    Get a layer by its ID.

    Parameters:
    - layer_id: The ID of the layer to retrieve

    Returns:
    - The requested layer or None if not found
    """
```

#### `BaseLayer` Class

```python
class BaseLayer:
    def __init__(self, seed, parameters=None):
        """
        Initialize a base layer.

        Parameters:
        - seed: Random seed for this layer
        - parameters: Dictionary of parameters for layer configuration
        """
```

```python
def generate(self):
    """
    Generate the layer data - implement in subclasses.

    Returns:
    - Self for method chaining
    """
```

```python
def get_data_at(self, x, y):
    """
    Get data at specific coordinates.

    Parameters:
    - x, y: Coordinates to query

    Returns:
    - Dictionary of data at the specified location
    """
```

#### `TerrainLayer` Class

```python
class TerrainLayer(BaseLayer):
    def generate(self):
        """
        Generate terrain using Perlin noise for elevation and moisture.

        Returns:
        - Self for method chaining
        """
```

```python
def _classify_terrain_types(self):
    """
    Classify terrain into types based on elevation and moisture.

    Terrain types include:
    - Deep water, shallow water, beach
    - Plains, hills, mountains, snow peaks
    - Forest, desert, etc. based on moisture
    """
```

### `additional_map_layers.py`

#### `RiversLayer` Class

```python
class RiversLayer(BaseLayer):
    def generate(self, terrain_layer=None):
        """
        Generate rivers based on terrain elevation.

        Parameters:
        - terrain_layer: Reference to the terrain layer

        Returns:
        - Self for method chaining
        """
```

```python
def _trace_river_path(self, start_x, start_y, terrain_layer, meander_factor=0.4, flow_strength=0.8):
    """
    Trace a river path from starting point to sea following elevation gradient with natural meandering.

    Parameters:
    - start_x, start_y: Starting coordinates for the river
    - terrain_layer: Reference to the terrain layer
    - meander_factor: How much randomness to add to river paths (0-1)
    - flow_strength: How strongly rivers follow elevation gradients (0-1)

    Returns:
    - List of (x, y) coordinates forming the river path
    """
```

#### `PoliticalLayer` Class

```python
class PoliticalLayer(BaseLayer):
    def generate(self, terrain_layer=None, rivers_layer=None):
        """
        Generate political territories based on terrain and rivers.

        Parameters:
        - terrain_layer: Reference to the terrain layer
        - rivers_layer: Reference to the rivers layer

        Returns:
        - Self for method chaining
        """
```

```python
def _place_capitals(self, num_capitals, terrain_layer, rivers_layer=None):
    """
    Place capital cities for territories.

    Parameters:
    - num_capitals: Number of capitals to place
    - terrain_layer: Reference to the terrain layer
    - rivers_layer: Reference to the rivers layer

    Returns:
    - List of (x, y, territory_id) tuples for capital locations
    """
```

```python
def _grow_territories(self, capitals, terrain_layer, rivers_layer=None):
    """
    Grow territories from capital cities using a priority queue approach.

    Parameters:
    - capitals: List of (x, y, territory_id) tuples for capital locations
    - terrain_layer: Reference to the terrain layer
    - rivers_layer: Reference to the rivers layer
    """
```

### `map_weather_journey_test.py`

#### `WeatherSystem` Class

```python
class WeatherSystem:
    def __init__(self, seed=None, map_width=512, map_height=512, region_size=64):
        """
        Initialize a weather system for a map.

        Parameters:
        - seed: Random seed for weather generation
        - map_width, map_height: Dimensions of the map
        - region_size: Size of weather regions in pixels
        """
```

```python
def generate_regional_weather(self, days=100):
    """
    Generate weather patterns for all regions for a number of days.

    Parameters:
    - days: Number of days to generate weather for

    Returns:
    - Dictionary of regional weather data
    """
```

```python
def get_weather_at(self, x, y, day_offset=0):
    """
    Get weather at specific coordinates and day.

    Parameters:
    - x, y: Coordinates to query
    - day_offset: Day offset from the current day (0 = today)

    Returns:
    - Dictionary of weather data
    """
```

#### `JourneyPlanner` Class

```python
class JourneyPlanner:
    def __init__(self, map_system, weather_system=None):
        """
        Initialize a journey planner.

        Parameters:
        - map_system: Reference to the map system
        - weather_system: Optional reference to the weather system
        """
```

```python
def plan_journey(self, start_point, end_point, start_day=0):
    """
    Plan a journey between two points.

    Parameters:
    - start_point: (x, y) coordinates of the starting point
    - end_point: (x, y) coordinates of the destination
    - start_day: Day to start the journey (for weather)

    Returns:
    - List of journey segments with positions, times, and descriptions
    """
```

```python
def _naturalize_path(self, path):
    """
    Make the path more natural by following roads and terrain.

    Parameters:
    - path: List of (x, y) coordinates

    Returns:
    - Modified path with more natural routing
    """
```

```python
def _find_road_path(self, start_x, start_y, end_x, end_y):
    """
    Find a path along roads between two points.

    Parameters:
    - start_x, start_y: Starting coordinates
    - end_x, end_y: Ending coordinates

    Returns:
    - List of (x, y) coordinates along roads, or None if no road path exists
    """
```

#### Map Visualization Functions

```python
def visualize_map(map_system, output_path=None, show_grid=False, show_labels=True):
    """
    Create a visualization of the map with all layers.

    Parameters:
    - map_system: The map system to visualize
    - output_path: Path to save the image (shows on screen if None)
    - show_grid: Whether to show the coordinate grid
    - show_labels: Whether to show territory and settlement labels

    Returns:
    - PIL Image object of the rendered map
    """
```

```python
def visualize_journey(map_system, journey_log, output_path=None):
    """
    Create a visualization of a journey on the map.

    Parameters:
    - map_system: The map system
    - journey_log: List of journey segments from JourneyPlanner
    - output_path: Path to save the image

    Returns:
    - PIL Image object of the rendered map with journey
    """
```
