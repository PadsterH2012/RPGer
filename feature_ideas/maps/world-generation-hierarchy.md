# World Generation Hierarchy

## Core Principle: Terrain as Foundation

In our procedural world generation system, terrain serves as the foundational layer upon which all other world elements are built. This creates a logical, realistic world where geographic features influence settlement patterns, travel routes, and even weather systems.

## Hierarchical Dependency Structure

```
Terrain (Elevation, Land/Water)
  │
  ├─► Geographic Features
  │     │
  │     ├─► Mountains, Hills
  │     ├─► Rivers, Lakes
  │     ├─► Coastlines, Islands
  │     ├─► Forests, Plains
  │     └─► Natural Resources (Mines, etc.)
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
        ├─► Settlements (Cities, Towns, Villages)
        │     │
        │     └─► Based on:
        │           ├─► Access to Water
        │           ├─► Defensible Positions
        │           ├─► Fertile Land
        │           ├─► Natural Resources
        │           └─► Trade Opportunities
        │
        └─► Infrastructure
              │
              ├─► Roads (Following Terrain Contours)
              ├─► Bridges (River Crossings)
              ├─► Ports (Coastal Access)
              ├─► Mountain Passes
              └─► Trade Routes (Optimal Paths)
```

## Implementation Details

### 1. Terrain Generation

The terrain layer establishes the fundamental geography of the world:

- **Elevation Map**: Determines mountains, hills, plains, and depressions
- **Land/Water Boundaries**: Defines coastlines, islands, and water bodies
- **Terrain Types**: Classifies regions as mountains, hills, plains, forests, etc.

```python
# Terrain generation is the first step
terrain_layer = TerrainLayer(seed, parameters)
terrain_layer.generate()
```

### 2. Geographic Features

Geographic features are derived directly from the terrain:

- **Rivers**: Flow from high to low elevation, following natural gradients
- **Lakes**: Form in depressions surrounded by higher terrain
- **Forests**: Grow in areas with suitable elevation and moisture
- **Natural Resources**: Placed based on terrain types (e.g., mines in mountains)

#### High-Resolution River Generation

For detailed river systems, a high-resolution grid approach can be used:

```python
# High-resolution terrain for river generation (one-time process)
high_res_terrain = HighResolutionTerrainLayer(seed, resolution=(4096, 4096))
high_res_terrain.generate()

# Hydrological simulation for realistic river formation
river_system = HydrologicalSystem(high_res_terrain)
river_system.simulate_rainfall(iterations=1000)
river_system.simulate_water_flow()
river_system.simulate_erosion(iterations=500)

# Extract river network from simulation results
rivers_layer = RiversLayer(seed, parameters)
rivers_layer.extract_from_hydrological_system(river_system)
rivers_layer.classify_river_types()  # Categorize as streams, rivers, major rivers
```

The high-resolution approach allows for:
- Realistic river meandering and branching patterns
- Natural formation of tributaries and watersheds
- Proper handling of elevation-based water flow
- Erosion effects that shape the terrain over time

### 3. Weather Patterns

Weather systems are heavily influenced by terrain:

- **Temperature**: Decreases with elevation (mountains are colder)
- **Precipitation**: More common on windward sides of mountains (rain shadows)
- **Wind Patterns**: Channeled by mountain ranges and valleys
- **Humidity**: Higher near water bodies, lower in inland areas

```python
# Weather systems use terrain data to generate realistic patterns
weather_system = WeatherSystem(seed, map_width, map_height)
weather_system.generate_regional_weather(terrain_layer)
```

#### Seasonal Effects

Seasons modify weather patterns but don't change the underlying terrain:

- **Temperature Variations**: Warmer in summer, colder in winter
- **Precipitation Types**: Rain in summer, snow in winter
- **Daylight Hours**: Longer days in summer, shorter in winter
- **Sunrise/Sunset Times**: Vary by season and latitude

```python
# Calculate sunrise/sunset based on season and latitude
def calculate_daylight_hours(day_of_year, latitude):
    """Calculate daylight hours based on day of year and latitude"""
    # Day of year (1-365)
    # Latitude (degrees, 0=equator, +90=north pole, -90=south pole)

    # Calculate solar declination
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))

    # Calculate day length in hours
    if latitude * declination > 90:
        return 24  # Polar day
    elif latitude * declination < -90:
        return 0   # Polar night
    else:
        day_length = 24 - (24/math.pi) * math.acos(
            (math.sin(math.radians(-0.83)) +
             math.sin(math.radians(latitude)) * math.sin(math.radians(declination))) /
            (math.cos(math.radians(latitude)) * math.cos(math.radians(declination)))
        )
        return day_length
```

### 4. Human Settlements

Settlements are placed based on terrain advantages:

- **Cities**: Located at strategic positions (river confluences, natural harbors, etc.)
- **Towns**: Placed at resource nodes, crossroads, or fertile areas
- **Villages**: Scattered in habitable areas with access to water and farmland

```python
# Settlement placement considers terrain, water access, and resources
settlements_layer = SettlementsLayer(seed, parameters)
settlements_layer.generate(terrain_layer, rivers_layer)
```

#### Settlement Placement Logic

```python
def evaluate_settlement_location(x, y, terrain_layer, rivers_layer):
    """Score a location for settlement suitability"""
    score = 0

    # Get terrain data
    terrain_data = terrain_layer.get_data_at(x, y)

    # Basic habitability
    if terrain_data["is_water"]:
        return 0  # Can't build on water
    if terrain_data["terrain_type"] == "mountains":
        score -= 50  # Very difficult to build in mountains
    elif terrain_data["terrain_type"] == "hills":
        score -= 10  # Somewhat difficult in hills
    elif terrain_data["terrain_type"] == "plains":
        score += 20  # Good for farming

    # Water access (critical for settlements)
    has_water_access = False
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            nx, ny = x + dx, y + dy
            river_data = rivers_layer.get_data_at(nx, ny)
            if river_data and river_data["has_river"]:
                has_water_access = True
                score += 30  # Major bonus for river access
                score += river_data["river_size"] * 5  # Larger rivers are better
                break

    if not has_water_access:
        score -= 40  # Major penalty for no water access

    # Coastal access (good for trade)
    is_coastal = False
    for dx in range(-10, 11):
        for dy in range(-10, 11):
            nx, ny = x + dx, y + dy
            terrain_data = terrain_layer.get_data_at(nx, ny)
            if terrain_data and terrain_data["is_water"] and not terrain_data["is_river"]:
                is_coastal = True
                score += 25  # Bonus for coastal access
                break

    return score
```

### 5. Infrastructure

Infrastructure connects settlements and resources, following terrain constraints:

- **Roads**: Follow valleys, avoid steep slopes, connect settlements
- **Bridges**: Placed at narrow river crossings
- **Mountain Passes**: Located at lowest points between mountain ranges
- **Trade Routes**: Optimize for distance and terrain difficulty

```python
# Road generation connects settlements while respecting terrain
def generate_roads(settlements_layer, terrain_layer):
    roads = []

    # Connect major settlements first
    major_settlements = [s for s in settlements_layer.settlements
                         if s["type"] in ["city", "town"]]

    # Sort by population (connect largest first)
    major_settlements.sort(key=lambda s: s["population"], reverse=True)

    # Connect each settlement to nearest neighbors
    for i, settlement in enumerate(major_settlements):
        # Find nearest unconnected settlements
        nearest = find_nearest_settlements(settlement, major_settlements[:i])

        for target in nearest:
            # Find path that follows terrain
            path = find_terrain_path(
                settlement["position"],
                target["position"],
                terrain_layer
            )

            if path:
                roads.append({
                    "path": path,
                    "type": "major_road",
                    "connects": [settlement["name"], target["name"]]
                })

    return roads
```

## Practical Applications

### 1. Realistic World Building

This hierarchical approach ensures that all elements of the world make geographic sense:
- Rivers flow downhill from mountains to seas
- Settlements are located where people would logically build them
- Roads follow natural terrain contours and connect important locations

### 2. Gameplay Implications

The terrain-based hierarchy creates natural gameplay opportunities:
- **Strategic Locations**: Mountain passes become strategic chokepoints
- **Resource Distribution**: Certain resources only appear in specific terrain types
- **Travel Challenges**: Terrain difficulty affects travel speed and route planning
- **Weather Effects**: Different regions have distinct weather patterns affecting gameplay

### 3. Narrative Opportunities

The logical world structure supports storytelling:
- **Border Conflicts**: Natural features often form political boundaries
- **Trade Dynamics**: Geography influences trade routes and economic centers
- **Cultural Development**: Isolated regions develop distinct cultures
- **Historical Events**: Geography shapes historical developments (battles at river crossings, etc.)

## Implementation Strategy

To implement this hierarchical system effectively:

1. **Generate in Order**: Always generate layers in dependency order (terrain → rivers → settlements → roads)
2. **Pass References**: Each generation step should have access to previously generated layers
3. **Cache Derived Data**: Compute and store derived properties (e.g., "near_water") to avoid repeated calculations
4. **Use Consistent Coordinates**: Maintain the same coordinate system across all layers
5. **Parameterize Relationships**: Allow adjustment of how strongly terrain influences other elements

### High-Resolution Grid Approach

For the most realistic world generation, a multi-resolution approach can be used:

1. **Initial High-Resolution Generation**:
   - Generate terrain and rivers at high resolution (4096×4096)
   - Perform detailed hydrological simulation as a one-time process
   - Store results in database for AI reasoning

2. **Gameplay-Oriented Representation**:
   - Downsample or extract key features for gameplay purposes
   - Maintain separate representations for AI reasoning vs. player interaction
   - Allow AI to reference the detailed data when generating descriptions or making decisions

3. **Database Integration**:
   - Store high-resolution grid data in compressed format
   - Index key features for efficient querying
   - Implement spatial queries for location-based reasoning

## Conclusion

By using terrain as the foundation and building other world elements in a logical hierarchy, we create a coherent, believable world where geographic features, weather patterns, settlements, and infrastructure all make sense together. This approach not only produces more realistic worlds but also creates richer gameplay experiences where the environment itself tells a story.
