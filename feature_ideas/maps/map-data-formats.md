# Map Data Formats and Agent Usage

This document outlines various approaches for structuring map data in formats that AI agents can effectively use for RPG gameplay and world interaction.

## Data Representation Formats

### 1. GeoJSON-Style Format
```json
{
  "map_dimensions": {"width": 1024, "height": 1024},
  "scale": "1 unit = 1 mile",
  "seed": 45470,
  "coastlines": [
    {"id": "east_coast", "points": [[800, 100], [820, 150], [810, 200], ...]}
  ],
  "boundaries": [
    {"id": "kingdom_border", "type": "political", "points": [[...]], "properties": {"name": "Eldoria"}}
  ],
  "regions": [
    {"id": "dark_forest", "type": "forest", "polygon": [[...]], "properties": {"danger_level": 3}}
  ],
  "locations": [
    {"id": "capital_city", "coordinates": [500, 300], "type": "city", "properties": {"name": "Highcastle", "population": 50000}}
  ]
}
```

### 2. Grid-Based Representation
```python
# 2D array where each cell contains terrain information
map_grid = [
    [0, 0, 0, 1, 1, 2, 2], # 0=water, 1=plains, 2=mountains
    [0, 0, 1, 1, 1, 1, 2],
    [0, 1, 1, 3, 3, 1, 2], # 3=forest
    ...
]

# Additional layers for other information
political_grid = [...]
resources_grid = [...]
```

#### High-Resolution Grid Implementation
For detailed world generation, high-resolution grids (1024×1024 to 4096×4096) can be used as a one-time generation process:

```python
# High-resolution heightmap (elevation in meters)
elevation_grid = [
    # 4096x4096 grid of elevation values
    [120, 118, 115, ...],
    [119, 117, 114, ...],
    ...
]

# Water volume grid (cubic meters per cell)
water_volume = [
    # 4096x4096 grid of water volume values
    [0, 0, 0.2, ...],
    [0, 0.1, 0.5, ...],
    ...
]

# River type classification
# 0=none, 1=seasonal creek, 2=stream, 3=river, 4=major river
river_type = [
    # 4096x4096 grid of river classifications
    [0, 0, 0, ...],
    [0, 0, 1, ...],
    [0, 1, 2, ...],
    ...
]

# Flow direction (for water movement simulation)
# Direction values 0-7 representing 8 possible directions
flow_direction = [
    # 4096x4096 grid of flow directions
    [0, 0, 3, ...],
    [0, 3, 3, ...],
    ...
]

# River depth (meters)
river_depth = [
    # 4096x4096 grid of depth values
    [0, 0, 0.1, ...],
    [0, 0, 0.3, ...],
    ...
]
```

#### River Representation Approaches

1. **Cell Type Approach**
```python
# 0=water, 1=plains, 2=mountains, 3=forest, 4=river
map_grid = [
    [0, 0, 0, 1, 1, 2, 2],
    [0, 0, 1, 4, 4, 1, 2],  # River cells (4)
    [0, 1, 1, 4, 3, 1, 2],  # River continues
    [0, 1, 4, 4, 3, 1, 2],  # River bends
    ...
]
```

2. **Multi-Layer Approach**
```python
# Base terrain layer
terrain_grid = [
    [0, 0, 0, 1, 1, 2, 2],  # 0=water, 1=plains, 2=mountains, 3=forest
    [0, 0, 1, 1, 1, 1, 2],
    [0, 1, 1, 3, 3, 1, 2],
    ...
]

# River layer (1=river, 0=no river)
river_grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0],  # River cells
    [0, 0, 0, 1, 0, 0, 0],  # River continues
    [0, 0, 1, 1, 0, 0, 0],  # River bends
    ...
]
```

3. **Flow Direction Approach**
```python
# Flow directions: 0=none, 1=north, 2=northeast, 3=east, etc.
flow_grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 6, 6, 0, 0],  # Flow southwest and southwest
    [0, 0, 0, 5, 0, 0, 0],  # Flow south
    [0, 0, 4, 4, 0, 0, 0],  # Flow southeast and southeast
    ...
]
```

4. **Heightmap + Water Volume Approach**
```python
# Heightmap (elevation values)
height_grid = [
    [2, 2, 2, 5, 8, 15, 20],
    [1, 1, 3, 4, 7, 12, 18],
    [0, 0, 2, 3, 5, 10, 15],
    ...
]

# Water volume grid (amount of water in each cell)
water_grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 2, 0, 0],  # Water accumulation
    [0, 0, 0, 3, 0, 0, 0],  # More water
    [5, 5, 1, 2, 0, 0, 0],  # Water flowing to lake
    ...
]
```

### 3. Vector Data
```python
coastlines = [
    [(x1, y1), (x2, y2), ...],  # Each list is a continuous coastline
    [(x1, y1), (x2, y2), ...],
]

regions = [
    {
        "name": "Misty Mountains",
        "type": "mountain_range",
        "polygon": [(x1, y1), (x2, y2), ...],
    },
    ...
]
```

### 4. Layered Data Structure
```python
map_data = {
    "base_terrain": terrain_grid,
    "elevation": elevation_grid,
    "political": political_grid,
    "resources": resources_grid,
    "points_of_interest": poi_list,
    "climate": climate_grid,
    "vector_features": {
        "coastlines": coastlines,
        "rivers": rivers,
        "roads": roads,
    }
}
```

## Map Information Categories

### Terrain and Physical Features

1. **Elevation Data**
   - Precise altitude at any coordinate
   - Slope steepness and direction
   - Natural barriers (cliffs, ravines)
   - Mountain passes and traversable routes

2. **Water Features**
   - Rivers, streams, and flow direction
   - Lakes and ponds with depth information
   - Waterfalls and rapids (difficulty to cross)
   - Underwater terrain for aquatic adventures

3. **Vegetation**
   - Forest coverage and type (deciduous, coniferous)
   - Undergrowth density affecting movement speed
   - Ancient/magical trees as landmarks
   - Clearings and natural gathering places

4. **Ground Composition**
   - Rocky, sandy, fertile, or marshy terrain
   - Natural resources (ore deposits, gem veins)
   - Stability for construction or camping
   - Archaeological significance (ancient ruins beneath)

### Climate and Environmental Factors

1. **Biomes**
   - Desert, tundra, rainforest, savanna, etc.
   - Transition zones between biomes
   - Microclimate areas with unique properties

2. **Weather Patterns**
   - Prevailing wind directions
   - Precipitation frequency and intensity by region
   - Storm paths and seasonal weather events
   - Temperature ranges by elevation and region

3. **Natural Hazards**
   - Volcanic activity zones
   - Earthquake fault lines
   - Avalanche-prone slopes
   - Flash flood channels

### Civilization Elements

1. **Settlements**
   - Cities, towns, villages with population density
   - Outposts, forts, and watchtowers
   - Abandoned settlements and ruins
   - Trade routes and caravan paths

2. **Political Boundaries**
   - Kingdom and empire borders
   - Disputed territories
   - Neutral zones and demilitarized areas
   - Tribal lands and nomadic migration routes

3. **Infrastructure**
   - Roads and bridges with quality ratings
   - Ports and harbors with capacity information
   - Canals and aqueducts
   - Magical transportation networks (teleportation circles)

4. **Points of Interest**
   - Dungeons, caves, and adventure sites
   - Magical anomalies or ley lines
   - Shrines, temples, and places of power
   - Historical battlefields and monuments

### Strategic Information

1. **Resources**
   - Hunting grounds and fishing spots
   - Herb and potion ingredient locations
   - Mining areas and quarries
   - Magical material sources

2. **Travel Logistics**
   - Distance calculations between points
   - Estimated travel times by different methods
   - Seasonal route changes (winter passes, spring floods)
   - Rest stop locations and water sources

## Agent Usage Patterns

### 1. Location-Based Storytelling
```python
def describe_location(x, y, map_data):
    """Generate description based on coordinates"""
    terrain_type = map_data.get_terrain_at(x, y)
    elevation = map_data.get_elevation_at(x, y)
    nearby_features = map_data.get_nearby_features(x, y, radius=5)
    region = map_data.get_region_at(x, y)
    weather = map_data.get_current_weather(x, y, current_day, season)

    description = f"You are in {region}, standing on {terrain_type} terrain at {elevation}ft elevation. "
    if nearby_features:
        description += f"You can see {', '.join(nearby_features)} in the distance."
    description += f" The weather is {weather}."
    return description
```

### 2. Navigation and Pathfinding
```python
def find_path(start_x, start_y, dest_x, dest_y, map_data, travel_mode="walking"):
    """Find a path between two points, considering terrain difficulty"""
    # A* pathfinding algorithm using terrain costs
    # Different travel modes (walking, horseback, boat) affect path selection
    # Return a list of coordinates forming a path and estimated travel time
```

### 3. Resource and Feature Discovery
```python
def find_nearest_resource(x, y, resource_type, map_data):
    """Find the nearest specified resource"""
    # Search for nearest resource of requested type
    # Return coordinates and distance
```

### 4. Dynamic Event Generation
```python
def generate_encounter(x, y, map_data, party_level):
    """Generate an appropriate encounter based on location"""
    terrain = map_data.get_terrain_at(x, y)
    region = map_data.get_region_at(x, y)
    nearby_poi = map_data.get_nearby_poi(x, y, radius=10)

    # Select encounter appropriate to terrain, region, and nearby features
    # Consider party level for difficulty
```

## Implementation Considerations

1. **Spatial Indexing**
   - Use quadtrees or similar data structures for efficient spatial queries
   - Enable "find nearest X" type queries for agents
   - Support region-based queries ("what's in this area?")

2. **Procedural Generation Rules**
   - Create algorithms that generate coherent relationships between features
   - Ensure rivers flow downhill, settlements appear near water, etc.
   - Generate logical resource distribution based on terrain

3. **Interpolation Methods**
   - Implement methods to calculate values between data points
   - Smooth transitions between different terrain types
   - Realistic blending of climate and weather patterns

4. **Serialization and Storage**
   - Efficient storage formats for large maps
   - Partial loading for performance optimization
   - Versioning for map evolution over campaign time

5. **High-Resolution Grid Processing**
   - One-time generation at world creation allows for intensive computation
   - Hydrological simulation for realistic river formation
   - Erosion simulation to shape terrain over time
   - Multi-scale approach: generate at high resolution, then downsample for gameplay if needed

6. **AI Reasoning with Grid Data**
   - Store detailed grid data in database for AI reasoning
   - AI can query terrain features for logical location placement
   - Maintain player-facing representation separately from AI reasoning layer
   - Enable AI to reference geographical features in descriptions and storytelling

## Integration with Existing maps.py

The current maps.py file generates a basic terrain map using Perlin noise. To enhance it for agent use:

1. Add export functions for different data formats
2. Implement feature detection (coastlines, mountains, etc.)
3. Create a MapData class with query methods
4. Add layers for additional information types
5. Implement serialization/deserialization

## AI Location Placement on Grid Data

The high-resolution grid data provides a foundation for intelligent AI placement of locations and features:

```python
# Example: AI querying for suitable village locations
def find_suitable_village_locations(grid_data, count=5):
    """Find suitable locations for villages based on terrain data"""
    suitable_locations = []

    for x in range(grid_data.width):
        for y in range(grid_data.height):
            # Check if near water but not in flood zone
            near_water = is_near_water(x, y, grid_data, max_distance=5)
            above_flood_level = grid_data.elevation[x][y] > get_flood_level(x, y, grid_data)

            # Check for suitable terrain
            suitable_terrain = grid_data.terrain[x][y] in [1, 3]  # Plains or light forest

            # Check for resources
            has_resources = has_nearby_resources(x, y, grid_data, resource_types=['wood', 'food', 'water'])

            if near_water and above_flood_level and suitable_terrain and has_resources:
                suitability_score = calculate_location_score(x, y, grid_data)
                suitable_locations.append({
                    'position': (x, y),
                    'score': suitability_score,
                    'terrain': grid_data.terrain[x][y],
                    'elevation': grid_data.elevation[x][y],
                    'water_source': identify_water_source(x, y, grid_data)
                })

    # Return top N locations by suitability score
    return sorted(suitable_locations, key=lambda loc: loc['score'], reverse=True)[:count]

# Example: AI placing a fortress at strategic location
def place_strategic_fortress(grid_data):
    """Find optimal location for a defensive fortress"""
    strategic_points = []

    for x in range(grid_data.width):
        for y in range(grid_data.height):
            # Check if higher than surroundings (defensive advantage)
            local_prominence = is_locally_prominent(x, y, grid_data, radius=10)

            # Check if near water source
            has_water_access = is_near_water(x, y, grid_data, max_distance=8)

            # Check if overlooks important feature (river crossing, valley, etc.)
            overlooks_feature = overlooks_strategic_feature(x, y, grid_data)

            # Check if terrain is suitable for construction
            buildable = grid_data.terrain[x][y] in [1, 2]  # Plains or hills

            if local_prominence and has_water_access and overlooks_feature and buildable:
                strategic_value = calculate_strategic_value(x, y, grid_data)
                strategic_points.append({
                    'position': (x, y),
                    'strategic_value': strategic_value,
                    'overlooks': get_overlooked_features(x, y, grid_data),
                    'elevation': grid_data.elevation[x][y],
                    'defensibility': calculate_defensibility(x, y, grid_data)
                })

    # Return the most strategic location
    if strategic_points:
        return max(strategic_points, key=lambda p: p['strategic_value'])
    return None
```

### Database Storage for AI Reasoning

```python
# Example database structure for AI reasoning with grid data
terrain_data = {
    "elevation_grid": [...],  # High-resolution elevation data
    "water_flow": [...],      # Water volume/direction
    "river_type": [...],      # Classification of water features
    "soil_type": [...],       # Soil fertility, type
    # Other environmental factors
}

# AI-placed locations (stored as coordinates + metadata)
locations = [
    {
        "type": "village",
        "name": "Riverdale",
        "position": [1024, 2048],  # Coordinates in the grid
        "population": 250,
        "features": ["river_crossing", "mill", "fishing_spot"],
        "resources": ["fish", "timber", "crops"],
        "description": "A small farming village built along the banks of the Swift River..."
    },
    {
        "type": "fortress",
        "name": "Highwatch Keep",
        "position": [1156, 2189],
        "garrison": 120,
        "features": ["river_overlook", "stone_walls", "watchtower"],
        "description": "A stone fortress perched on the cliffs overlooking the river valley..."
    },
    # More locations...
]
```

## Next Steps

1. Extend maps.py to export structured data formats
2. Create a MapData class for agent interaction
3. Implement basic query functions (get_terrain_at, find_path, etc.)
4. Add feature detection algorithms
5. Develop additional information layers
6. Implement hydrological simulation for realistic river generation
7. Create AI query functions for intelligent location placement
