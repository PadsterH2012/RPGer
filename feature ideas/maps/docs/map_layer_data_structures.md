# Map Layer Data Structures

This document details the data structures used by each map layer, including the format of data returned by the `get_data_at(x, y)` method for each layer type.

## Core Data Structures

### MapSystem

The `MapSystem` class maintains the following key data structures:

```python
self.base_seed      # Base random seed for the entire map
self.width          # Map width in pixels
self.height         # Map height in pixels
self.layers         # Dictionary of layers by layer_id
self.layer_order    # List of layer_ids in dependency order
```

### BaseLayer

All layer types inherit from `BaseLayer`, which provides:

```python
self.seed           # Random seed for this specific layer
self.parameters     # Dictionary of configuration parameters
self.width          # Layer width in pixels
self.height         # Layer height in pixels
self.generated      # Boolean flag indicating if layer has been generated
self.layer_type     # String identifier for the layer type
```

## Layer-Specific Data Structures

### TerrainLayer

**Internal Data:**
```python
self.elevation      # 2D numpy array of elevation values (0.0-1.0)
self.moisture       # 2D numpy array of moisture values (0.0-1.0)
self.land_mask      # 2D boolean numpy array (True = land, False = water)
self.terrain_types  # 2D numpy array of terrain type codes
```

**Data Returned by `get_data_at(x, y)`:**
```python
{
    "elevation": float,        # Elevation value (0.0-1.0)
    "moisture": float,         # Moisture value (0.0-1.0)
    "is_land": bool,           # Whether this point is land
    "is_water": bool,          # Whether this point is water
    "terrain_type": string,    # Terrain type name (e.g., "mountains", "plains")
    "terrain_code": int        # Numeric code for terrain type
}
```

### RiversLayer

**Internal Data:**
```python
self.rivers         # List of river paths (each a list of (x,y) coordinates)
self.river_grid     # 2D numpy array of river size values (0 = no river)
```

**Data Returned by `get_data_at(x, y)`:**
```python
{
    "has_river": bool,         # Whether this point has a river
    "river_size": int,         # Size/width of the river (1+)
    "elevation": float         # Elevation at this point (filled during rendering)
}
```

### PoliticalLayer

**Internal Data:**
```python
self.territories    # List of territory objects
self.territory_grid # 2D numpy array of territory IDs (-1 = no territory)
self.capitals       # List of (x, y, territory_id) tuples for capital locations
```

**Data Returned by `get_data_at(x, y)`:**
```python
{
    "territory_id": int,       # ID of the territory (-1 if none)
    "name": string,            # Name of the territory
    "capital_distance": float, # Distance to the territory's capital
    "is_capital": bool,        # Whether this point is a capital
    "border_distance": float   # Distance to nearest border (if calculated)
}
```

### SettlementsLayer

**Internal Data:**
```python
self.settlements    # List of settlement objects
self.roads          # List of road objects (each with "points" and "type")
self.paths          # List of path objects (smaller than roads)
```

**Data Returned by `get_data_at(x, y)`:**
```python
{
    "has_settlement": bool,    # Whether this point has a settlement
    "settlement_type": string, # Type of settlement ("city", "town", "village")
    "settlement_name": string, # Name of the settlement
    "population": int,         # Estimated population
    "has_road": bool,          # Whether this point has a road
    "road_type": string        # Type of road ("major", "minor", "path")
}
```

### WeatherLayer

**Internal Data:**
```python
self.regional_weather  # Dictionary of weather data by region and day
self.current_day       # Current day index
```

**Data Returned by `get_weather_at(x, y, day_offset=0)`:**
```python
{
    "temperature": float,      # Temperature in degrees F
    "cloud_cover": float,      # Cloud cover (0.0-1.0)
    "precipitation": float,    # Precipitation amount (0.0-1.0)
    "precipitation_type": str, # Type ("none", "rain", "snow", etc.)
    "wind_speed": float,       # Wind speed (0.0-1.0)
    "wind_direction": float,   # Wind direction in degrees
    "description": string      # Text description of weather
}
```

### ExplorationLayer

**Internal Data:**
```python
self.exploration_grid       # 2D numpy array of exploration states (0-3)
self.player_position_history # List of (x,y) coordinates the player has visited
self.known_locations        # Dictionary of named locations the player knows
```

**Exploration States:**
```python
UNEXPLORED = 0  # Player has no knowledge of this area
KNOWN = 1       # Player has heard about this area but hasn't visited
MAPPED = 2      # Player has obtained a map of this area
EXPLORED = 3    # Player has personally visited this area
```

**Data Returned by `get_data_at(x, y)`:**
```python
{
    "exploration_state": int,  # Numeric state code (0-3)
    "is_unexplored": bool,     # Whether area is completely unknown
    "is_known": bool,          # Whether player has at least basic knowledge
    "is_mapped": bool,         # Whether player has a map of this area
    "is_explored": bool        # Whether player has personally visited
}
```

## Data Flow Between Layers

Layers are generated in a specific order to handle dependencies:

1. **TerrainLayer** is generated first, providing the foundation
2. **RiversLayer** uses TerrainLayer data to trace rivers along elevation gradients
3. **PoliticalLayer** uses both Terrain and Rivers to create realistic territories
4. **SettlementsLayer** uses all previous layers to place settlements logically

During rendering, data flows between layers to create the final visualization:

```
TerrainLayer → Base map colors
    ↓
RiversLayer → Rivers drawn on terrain
    ↓
PoliticalLayer → Political boundaries drawn respecting terrain and rivers
    ↓
SettlementsLayer → Settlements and roads added
    ↓
Final Map Visualization
```

For the player's view, the exploration layer filters what is visible:

```
Full Map Visualization
    ↓
ExplorationLayer → Filters map based on player knowledge
    ↓
Player's Map View (with "fog of war")
```

## Example: Data at a Single Point

For a single point (x=100, y=150), the combined data from all layers might look like:

```python
{
    # Terrain data
    "elevation": 0.75,
    "moisture": 0.4,
    "is_land": True,
    "terrain_type": "hills",

    # River data
    "has_river": True,
    "river_size": 2,

    # Political data
    "territory_id": 3,
    "territory_name": "Kingdom of Eldoria",
    "is_capital": False,

    # Settlement data
    "has_settlement": True,
    "settlement_type": "village",
    "settlement_name": "Riverdale",
    "population": 350,
    "has_road": True,

    # Weather data (separate function)
    "temperature": 68.5,
    "precipitation_type": "rain",
    "wind_speed": 0.3,

    # Exploration data
    "exploration_state": 3,
    "is_explored": True
}
```

This combined data enables rich, contextual descriptions of locations for RPG gameplay, while the exploration layer controls what information is actually revealed to the player.
