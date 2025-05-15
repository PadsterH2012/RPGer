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

## Integration with Existing maps.py

The current maps.py file generates a basic terrain map using Perlin noise. To enhance it for agent use:

1. Add export functions for different data formats
2. Implement feature detection (coastlines, mountains, etc.)
3. Create a MapData class with query methods
4. Add layers for additional information types
5. Implement serialization/deserialization

## Next Steps

1. Extend maps.py to export structured data formats
2. Create a MapData class for agent interaction
3. Implement basic query functions (get_terrain_at, find_path, etc.)
4. Add feature detection algorithms
5. Develop additional information layers
