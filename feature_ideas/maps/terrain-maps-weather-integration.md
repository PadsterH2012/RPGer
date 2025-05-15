# Integrated Terrain, Maps, and Weather System

## Overview

This document outlines a comprehensive approach to world-building that integrates terrain generation, map representation, and dynamic weather systems. These three elements are deeply interconnected in our RPG system:

1. **Terrain as Foundation**: The physical geography forms the base layer upon which all other world elements are built
2. **Map Representation**: Multiple data formats and layers represent the world for both visual display and agent interaction
3. **Weather Systems**: Dynamic weather patterns influenced by terrain and geography create immersive, realistic environments

## Core Principle: Hierarchical Dependency

The world generation follows a strict hierarchical structure where terrain is the foundation:

```
Terrain (Elevation, Land/Water)
  │
  ├─► Geographic Features
  │     │
  │     ├─► Mountains, Hills
  │     ├─► Rivers, Lakes
  │     ├─► Coastlines, Islands
  │     ├─► Forests, Plains
  │     └─► Natural Resources
  │
  ├─► Weather Patterns
  │     │
  │     ├─► Regional Climate
  │     ├─► Precipitation
  │     ├─► Temperature
  │     ├─► Wind Patterns
  │     └─► Seasonal Variations
  │
  └─► Human Elements
        │
        ├─► Settlements
        └─► Infrastructure
```

## Terrain and World Generation

### Generation Process

1. **Elevation Map**: Determines mountains, hills, plains, and depressions
2. **Land/Water Boundaries**: Defines coastlines, islands, and water bodies
3. **Geographic Features**: Rivers flow from high to low elevation, lakes form in depressions
4. **Biomes and Vegetation**: Determined by elevation, moisture, and temperature

### Implementation Example

```python
# Terrain generation is the first step
terrain_layer = TerrainLayer(seed, parameters)
terrain_layer.generate()

# Rivers follow elevation gradients from the terrain
rivers_layer = RiversLayer(seed, parameters)
rivers_layer.generate(terrain_layer)  # Requires terrain data
```

## Map Data Formats and Representation

### Multi-Format Approach

The system supports multiple data formats to represent the same world information:

1. **GeoJSON-Style Format**: Vector-based representation with features, properties, and coordinates
2. **Grid-Based Representation**: 2D arrays where each cell contains terrain information
   - Supports high-resolution grids (up to 4096×4096) for detailed terrain and river systems
   - Multiple approaches for river representation (cell type, multi-layer, flow direction)
   - One-time generation process prioritizes quality over performance
3. **Layered Data Structure**: Multiple overlapping grids for different information types

### Layered Map Structure

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

### Map Information Categories

1. **Terrain and Physical Features**
   - Elevation data (altitude, slope, barriers)
   - Water features (rivers, lakes, coastlines)
   - Vegetation (forests, grasslands)
   - Ground composition (rocky, sandy, fertile)

2. **Climate and Environmental Factors**
   - Biomes (desert, tundra, rainforest)
   - Weather patterns (wind, precipitation)
   - Natural hazards (volcanic areas, fault lines)

3. **Civilization Elements**
   - Settlements (cities, towns, villages)
   - Political boundaries (kingdoms, territories)
   - Infrastructure (roads, bridges, ports)
   - Points of interest (dungeons, temples)

## Dynamic Weather System

### Core Concept

The weather system pre-generates patterns for each region in the campaign world, storing this information in the database. As gameplay progresses, the AI references the current game date to determine weather conditions, incorporating them into descriptions, encounters, and storylines.

### Weather-Terrain Interaction

Weather patterns are heavily influenced by terrain:

1. **Temperature**: Decreases with elevation (mountains are colder)
2. **Precipitation**: More common on windward sides of mountains (rain shadows)
3. **Wind Patterns**: Channeled by mountain ranges and valleys
4. **Humidity**: Higher near water bodies, lower in inland areas

### Regional Weather Interpolation

For locations between major regions, weather is calculated dynamically:

1. **Proximity-Based Calculation**
   - Weather for intermediate locations is interpolated from nearest regions
   - Closer regions have stronger influence on local conditions
   - Creates smooth transitions across the world map

2. **Terrain Adjustments**
   - Modify interpolated weather based on local terrain
   - Elevation changes affect temperature (lapse rate)
   - Mountains create rain shadows on leeward sides
   - Forests moderate temperature extremes and reduce wind
   - Coastal areas have more moderate temperatures and increased fog probability

### Implementation Example

```javascript
function getLocationWeather(x, y, gameDate) {
  // Find nearest regions with weather data
  const nearestRegions = findNearestWeatherRegions(x, y, 3);

  // Get current weather for each region
  const regionalWeather = nearestRegions.map(region => ({
    weather: getRegionWeather(region.id, gameDate),
    distance: region.distance,
    weight: 1 / (region.distance * region.distance) // Inverse square distance
  }));

  // Normalize weights
  const totalWeight = regionalWeather.reduce((sum, rw) => sum + rw.weight, 0);
  regionalWeather.forEach(rw => rw.normalizedWeight = rw.weight / totalWeight);

  // Calculate interpolated values
  const interpolated = calculateWeightedWeather(regionalWeather);

  // Apply terrain modifiers
  const terrain = getTerrainAt(x, y);
  const elevation = getElevationAt(x, y);
  return applyTerrainModifiers(interpolated, terrain, elevation);
}
```

## Database Schema Integration

The database schema supports the integrated terrain-map-weather system:

### Geographic Feature Schema
```json
{
  "_id": "ObjectId",
  "name": "Feature name",
  "type": "Feature type",
  "description": "Feature description",
  "location": "Where it's located",
  "climate": "Weather patterns",
  "flora": "Plant life",
  "fauna": "Animal life",
  "resources": "Available resources",
  "settlements": "Associated settlements",
  "points_of_interest": "Notable locations",
  "hazards": "Dangers",
  "extended_properties": {
    "magical_properties": "Magical effects"
  }
}
```

### Weather Pattern Schema
```json
{
  "_id": "ObjectId",
  "region_id": "Associated region",
  "year": "Game world year",
  "starting_day": "First day in sequence",
  "pattern_seed": "Randomization seed",
  "region_data": {
    "coordinates": "Map coordinates",
    "elevation": "Height above sea level",
    "terrain_type": "Primary terrain",
    "water_bodies": "Nearby water features",
    "region_size": "Area covered"
  },
  "daily_weather": [
    {
      "day_number": "Day in sequence",
      "season": "Current season",
      "temperature": {
        "morning": "Morning temperature",
        "midday": "Midday temperature",
        "evening": "Evening temperature",
        "night": "Night temperature"
      },
      "precipitation": {
        "type": "Rain, snow, etc.",
        "intensity": "Light, moderate, heavy",
        "duration_hours": "How long it lasts"
      },
      "wind": {
        "direction": "Wind direction",
        "speed": "Wind speed",
        "gusts": "Gust strength"
      },
      "cloud_cover": "Cloud coverage percentage",
      "special_conditions": "Fog, mist, etc.",
      "description_tags": "Keywords for descriptions",
      "narrative_hooks": {
        "description": "Weather narrative",
        "gameplay_effects": "Effects on gameplay",
        "mood": "Atmospheric mood"
      }
    }
  ],
  "weather_transitions": [
    {
      "from_condition": "Starting weather",
      "to_condition": "Ending weather",
      "transition_description": "How weather changes",
      "duration_days": "How long transition takes"
    }
  ]
}
```

### Weather Interpolation Schema
```json
{
  "_id": "ObjectId",
  "name": "Name of interpolation system",
  "description": "How the system works",
  "interpolation_parameters": {
    "max_interpolation_distance": "Maximum distance for interpolation",
    "elevation_lapse_rate": "Temperature change per elevation unit",
    "distance_weight_factor": "How distance affects weighting",
    "terrain_influence_factor": "How terrain affects interpolation"
  },
  "terrain_modifiers": {
    "mountain": {
      "temperature_modifier": "Temperature adjustment",
      "precipitation_modifier": "Precipitation adjustment",
      "wind_modifier": "Wind adjustment"
    },
    "forest": "Forest-specific modifiers",
    "coast": "Coastal area modifiers",
    "valley": "Valley-specific modifiers",
    "desert": "Desert-specific modifiers",
    "plains": "Plains-specific modifiers"
  }
}
```

## Agent Usage and Integration

### Location-Based Storytelling
```python
def describe_location(x, y, map_data, weather_system, game_date):
    """Generate description based on coordinates and current weather"""
    terrain_type = map_data.get_terrain_at(x, y)
    elevation = map_data.get_elevation_at(x, y)
    nearby_features = map_data.get_nearby_features(x, y, radius=5)
    region = map_data.get_region_at(x, y)

    # Get current weather for this location
    weather = weather_system.get_location_weather(x, y, game_date)

    # Build description incorporating terrain and weather
    description = f"You are in {region}, standing on {terrain_type} terrain at {elevation}ft elevation. "

    # Add weather details
    if weather.precipitation.type != "none":
        description += f"It is currently {weather.precipitation.intensity} {weather.precipitation.type}. "

    if weather.cloud_cover > 80:
        description += "The sky is heavily overcast. "
    elif weather.cloud_cover > 50:
        description += "There are scattered clouds above. "
    elif weather.cloud_cover > 20:
        description += "The sky is mostly clear with a few clouds. "
    else:
        description += "The sky is clear. "

    # Add wind description
    if weather.wind.speed == "strong":
        description += f"A strong wind blows from the {weather.wind.direction}. "
    elif weather.wind.speed == "moderate":
        description += f"A steady breeze comes from the {weather.wind.direction}. "

    # Add nearby features
    if nearby_features:
        description += f"You can see {', '.join(nearby_features)} in the distance."

    return description
```

### AI Reasoning with High-Resolution Grid Data
```python
def find_suitable_settlement_locations(grid_data, settlement_type="village", count=5):
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
    for x in range(0, grid_data.width, 10):  # Sample every 10 cells for efficiency
        for y in range(0, grid_data.height, 10):
            if meets_criteria(x, y, grid_data, criteria):
                score = calculate_location_score(x, y, grid_data, criteria)
                suitable_locations.append({
                    'position': (x, y),
                    'score': score,
                    'terrain': grid_data.terrain[x][y],
                    'elevation': grid_data.elevation[x][y],
                    'features': identify_nearby_features(x, y, grid_data)
                })

    # Return top N locations by suitability score
    return sorted(suitable_locations, key=lambda loc: loc['score'], reverse=True)[:count]
```

### Database Integration for AI Reasoning
```python
# Example database structure for AI reasoning with grid data
terrain_data_collection = {
    "world_id": "unique_world_identifier",
    "generation_parameters": {
        "seed": 45470,
        "resolution": [4096, 4096],
        "generation_date": "2023-05-15"
    },
    "grid_data": {
        "elevation": "compressed_binary_data",  # High-resolution elevation grid
        "water_flow": "compressed_binary_data", # Water flow direction and volume
        "river_type": "compressed_binary_data", # River classification
        "terrain_type": "compressed_binary_data", # Base terrain types
        "soil_quality": "compressed_binary_data" # Soil fertility data
    },
    "derived_features": {
        "coastlines": [...],  # Vector data for coastlines
        "rivers": [...],      # Major river paths
        "mountain_ranges": [...], # Mountain range definitions
        "biomes": [...]       # Biome region definitions
    }
}

# AI-placed locations collection
locations_collection = [
    {
        "location_id": "unique_location_id",
        "world_id": "unique_world_identifier",
        "type": "village",
        "name": "Riverdale",
        "position": [1024, 2048],  # Coordinates in the grid
        "population": 250,
        "features": ["river_crossing", "mill", "fishing_spot"],
        "resources": ["fish", "timber", "crops"],
        "description": "A small farming village built along the banks of the Swift River...",
        "placement_rationale": {
            "water_proximity": "adjacent to Swift River",
            "elevation": "15m above river level (safe from flooding)",
            "terrain_quality": "fertile soil in river valley",
            "strategic_value": "controls river crossing on trade route"
        }
    },
    # More locations...
]
```

## Implementation Strategy

To implement this integrated system effectively:

1. **Generate in Order**: Always generate layers in dependency order (terrain → rivers → settlements → roads → weather)
2. **Pass References**: Each generation step should have access to previously generated layers
3. **Cache Derived Data**: Compute and store derived properties to avoid repeated calculations
4. **Use Consistent Coordinates**: Maintain the same coordinate system across all layers
5. **Parameterize Relationships**: Allow adjustment of how strongly terrain influences other elements

## Conclusion

By integrating terrain, maps, and weather systems, we create a coherent, believable world where geographic features and weather patterns interact realistically. This approach produces more immersive gameplay experiences where:

1. Weather changes naturally over time rather than remaining static
2. Weather affects travel speed, visibility, and combat
3. Different regions have distinct climate patterns based on their terrain
4. Players experience the passage of seasons and changing conditions
5. The environment feels alive and responsive to both geography and time

This integrated approach ensures that all world elements make geographic sense while providing rich opportunities for gameplay and storytelling.
