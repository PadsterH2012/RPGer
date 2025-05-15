# Multi-Resolution Terrain Database for AI Reasoning

## Overview

This document outlines a database structure for storing detailed terrain data at multiple resolution levels. This approach allows the AI to access appropriate detail levels for reasoning about the game world, generating consistent descriptions, and making intelligent decisions about location placement.

The key concept is a hierarchical data structure that stores terrain information at different scales:
- **Continent Level**: Low-resolution data covering the entire world
- **Region Level**: Medium-resolution data for specific areas
- **Local Level**: High-resolution data for important locations

This data is primarily for AI consumption and reasoning, not for player visualization.

## Core Principles

1. **Hierarchical Consistency**: Each detail level is consistent with its parent level
2. **Deterministic Generation**: Features are generated consistently based on location
3. **Efficient Storage**: Only store necessary detail where needed
4. **Query Optimization**: Structure supports efficient spatial queries
5. **Descriptive Richness**: Contains sufficient detail for vivid, consistent descriptions

## Database Structure

### Continent-Level Data (1km resolution)

```python
continent_data = {
    "id": "main_continent",
    "dimensions": [4096, 4096],  # 4096km x 4096km
    "cell_size": 1000,  # 1 cell = 1km
    "elevation_data": compressed_binary_data,  # Height in meters
    "terrain_types": compressed_binary_data,  # Basic terrain classification
    "biomes": compressed_binary_data,  # Major biome types
    "major_features": [
        {
            "id": "northern_mountains",
            "type": "mountain_range",
            "bounds": [[1200, 800], [1800, 1200]],
            "properties": {"avg_elevation": 2500, "highest_peak": 3200}
        },
        {
            "id": "great_river",
            "type": "river",
            "path": [[2000, 1000], [2050, 1200], [2150, 1400], ...],
            "properties": {"width_avg": 200, "depth_avg": 15}
        }
        # More major features
    ]
}
```

### Region-Level Data (100m resolution)

```python
region_data = {
    "id": "northern_region",
    "parent_id": "main_continent",
    "bounds": [[1000, 1000], [1256, 1256]],  # 256km x 256km region
    "dimensions": [2560, 2560],  # 2560x2560 cells at 100m resolution
    "cell_size": 100,  # 1 cell = 100m
    "elevation_data": compressed_binary_data,  # More detailed elevation
    "terrain_details": compressed_binary_data,  # Detailed terrain types
    "vegetation": compressed_binary_data,  # Vegetation types and density
    "water_features": compressed_binary_data,  # Rivers, lakes, etc.
    "features": [
        {
            "id": "oakwood_forest",
            "type": "forest",
            "bounds": [[1050, 1100], [1100, 1150]],
            "properties": {
                "dominant_trees": ["oak", "maple"],
                "density": "dense",
                "age": "ancient"
            }
        },
        {
            "id": "riverdale",
            "type": "settlement",
            "position": [1150, 1120],
            "properties": {
                "name": "Riverdale",
                "population": 250,
                "type": "village"
            }
        }
        # More regional features
    ]
}
```

### Local-Level Data (1m resolution)

```python
local_data = {
    "id": "riverdale_area",
    "parent_id": "northern_region",
    "bounds": [[1145, 1115], [1155, 1125]],  # 10km x 10km area
    "dimensions": [10000, 10000],  # 10000x10000 cells at 1m resolution
    "cell_size": 1,  # 1 cell = 1m
    "elevation_data": compressed_binary_data,  # Highly detailed elevation
    "ground_composition": compressed_binary_data,  # Soil, rock types
    "vegetation_details": compressed_binary_data,  # Individual trees, plants
    "features": [
        {
            "id": "old_mill",
            "type": "building",
            "position": [11502, 11183],
            "properties": {
                "name": "Old Mill",
                "size": [15, 10],  # 15m x 10m
                "material": "stone",
                "condition": "weathered",
                "description": "An old stone mill with a creaking water wheel"
            }
        },
        {
            "id": "village_square",
            "type": "landmark",
            "position": [11500, 11200],
            "properties": {
                "size": 30,  # 30m diameter
                "features": ["well", "market stalls", "old oak tree"],
                "description": "A bustling village square centered around an ancient oak"
            }
        }
        # More local features
    ]
}
```

## AI Reasoning Functions

### Location Description Generation

```python
def generate_location_description(player_position, time_of_day, season, weather):
    """Generate a consistent description based on player's location and conditions"""
    # Get basic terrain data at player position
    x, y = player_position
    terrain_cell = get_terrain_at(x, y)
    
    # Find nearby features (within visibility range)
    visibility = calculate_visibility(weather, time_of_day)
    nearby_features = find_features_within_range(x, y, visibility)
    
    # Sort features by distance and significance
    nearby_features.sort(key=lambda f: (distance(f["position"], player_position), -f["significance"]))
    
    # Build description
    description = []
    
    # Start with immediate surroundings
    description.append(f"You are standing on {terrain_cell['terrain_type']} terrain.")
    
    # Add elevation context
    if terrain_cell["slope"] > 0.2:
        slope_direction = get_slope_direction(x, y)
        description.append(f"The ground slopes {slope_direction}.")
    
    # Add vegetation
    if terrain_cell["vegetation_density"] > 0.7:
        description.append(f"You're surrounded by {terrain_cell['vegetation_type']}.")
    elif terrain_cell["vegetation_density"] > 0.3:
        description.append(f"Scattered {terrain_cell['vegetation_type']} can be seen around you.")
    
    # Add weather and time
    description.append(generate_weather_description(weather, time_of_day, season))
    
    # Add visible features in order of prominence
    if nearby_features:
        description.append("You can see:")
        for feature in nearby_features[:5]:  # Limit to most prominent 5
            feature_desc = generate_feature_description(
                feature, 
                distance(feature["position"], player_position),
                direction(player_position, feature["position"]),
                time_of_day,
                weather
            )
            description.append(f"- {feature_desc}")
    
    # Add sounds and smells based on surroundings
    ambient = generate_ambient_sensations(
        terrain_cell, nearby_features, time_of_day, weather, season
    )
    if ambient:
        description.append(ambient)
    
    return "\n".join(description)
```

### Settlement Placement

```python
def find_suitable_settlement_locations(terrain_db, settlement_type="village", count=5):
    """Find suitable locations for settlements based on terrain data"""
    suitable_locations = []
    
    # Different criteria based on settlement type
    if settlement_type == "village":
        # Villages need water, arable land, and resources
        criteria = {
            "water_distance": 5,      # Must be within 5 cells of water
            "min_elevation": 5,       # Above potential flood level
            "max_elevation": 100,     # Not too high in mountains
            "suitable_terrains": [1, 3],  # Plains or light forest
            "required_resources": ["wood", "food", "water"]
        }
    elif settlement_type == "fortress":
        # Fortresses need defensive position and strategic value
        criteria = {
            "water_distance": 8,      # Water access but can be further
            "min_elevation": 20,      # Higher ground for defense
            "local_prominence": 10,   # Higher than surroundings
            "suitable_terrains": [1, 2],  # Plains or hills
            "strategic_features": ["river_crossing", "mountain_pass", "valley"]
        }
    
    # Search the grid for locations meeting criteria
    for x in range(0, terrain_db.width, 10):  # Sample every 10 cells for efficiency
        for y in range(0, terrain_db.height, 10):
            if meets_criteria(x, y, terrain_db, criteria):
                score = calculate_location_score(x, y, terrain_db, criteria)
                suitable_locations.append({
                    'position': (x, y),
                    'score': score,
                    'terrain': terrain_db.terrain[x][y],
                    'elevation': terrain_db.elevation[x][y],
                    'features': identify_nearby_features(x, y, terrain_db)
                })
    
    # Return top N locations by suitability score
    return sorted(suitable_locations, key=lambda loc: loc['score'], reverse=True)[:count]
```

## Example Output

When a player is at position [1545, 1455] in the early morning during spring with clear weather:

```
You are standing on grassy terrain.
The ground slopes gently toward the east.
Scattered oak trees can be seen around you.
The morning sun illuminates the landscape. A light breeze comes from the west.

You can see:
- The small village of Riverdale to the northeast, with its old stone bridge visible
- The crystal waters of the Silvermelt River to the north, flowing gently
- The well-traveled dirt road leading southeast
- The edge of the Whispering Woods to the east, where birds can be heard singing
- The distant peaks of the Frostpeak Mountains to the northwest, with snow-capped peaks

The air smells of fresh grass and wildflowers. Birdsong fills the air, and you can hear the faint sounds of village life from Riverdale.
```

If the player returns to the exact same spot under the same conditions, they'll get the identical description. If they visit in winter during a snowstorm at night, they'd get a completely different but equally consistent description.

## Implementation Considerations

1. **Storage Efficiency**:
   - Use compression for grid data
   - Store sparse data where appropriate
   - Use procedural generation with seeds for deterministic detail

2. **Query Performance**:
   - Implement spatial indexing (quadtree, R-tree)
   - Cache frequently accessed regions
   - Pre-compute derived properties

3. **Consistency Mechanisms**:
   - Use deterministic algorithms based on location
   - Maintain hierarchical relationships between resolution levels
   - Store permanent changes as deltas from the base data

4. **Database Technology**:
   - MongoDB for document-based storage
   - PostgreSQL with PostGIS for spatial queries
   - Redis for caching frequently accessed data

## Next Steps

1. Implement basic terrain database schema
2. Develop terrain generation algorithms for multiple resolution levels
3. Create query functions for AI reasoning
4. Implement description generation system
5. Test consistency across different conditions
6. Optimize storage and query performance
