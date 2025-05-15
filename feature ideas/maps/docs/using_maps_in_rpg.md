# Using the Map System in RPG Applications

This guide explains how to integrate the map generation system into RPG applications, with a focus on creating immersive gameplay experiences.

## Getting Started

### Basic Map Creation

To create a basic map with terrain, rivers, and political boundaries:

```python
from seed_based_layered_map_system import MapSystem

# Create a map system with a specific seed for reproducibility
map_system = MapSystem(base_seed=12345, width=512, height=512)

# Add terrain layer
map_system.add_layer(
    "terrain", 
    "terrain", 
    seed_modifier=0,
    parameters={
        "scale": 100.0,
        "sea_level": -0.1,
        "mountain_level": 0.7
    }
)

# Add rivers layer
map_system.add_layer(
    "rivers", 
    "rivers", 
    seed_modifier=500,
    parameters={
        "num_rivers": 15,
        "meander_factor": 0.4
    }
)

# Add political boundaries
map_system.add_layer(
    "kingdoms", 
    "political", 
    seed_modifier=1000,
    parameters={
        "num_territories": 8
    }
)

# Generate all layers
map_system.generate_all_layers()

# Visualize the map
from map_weather_journey_test import visualize_map
map_img = visualize_map(map_system, output_path="my_campaign_map.png")
```

### Adding Weather and Journey Planning

To enhance the map with weather systems and journey planning:

```python
from map_weather_journey_test import WeatherSystem, JourneyPlanner

# Create a weather system
weather_system = WeatherSystem(seed=12345, map_width=512, map_height=512)
weather_system.generate_regional_weather(days=100)  # Generate 100 days of weather

# Create a journey planner
journey_planner = JourneyPlanner(map_system, weather_system)

# Plan a journey between two points
start_point = (100, 150)  # Starting coordinates
end_point = (400, 350)    # Destination coordinates
journey_log = journey_planner.plan_journey(start_point, end_point)

# Visualize the journey on the map
from map_weather_journey_test import visualize_journey
journey_map = visualize_journey(map_system, journey_log, output_path="journey_map.png")

# Print the journey log
for entry in journey_log:
    print(f"Day {entry['day']}, {entry['time_of_day']}: {entry['description']}")
```

## RPG Integration

### 1. Campaign World Creation

Use the map system to create a persistent world for your campaign:

1. **Generate the base map** with a fixed seed for consistency
2. **Save the map data** to a database or file for future sessions
3. **Create named locations** that correspond to map coordinates
4. **Develop regional lore** based on terrain, political boundaries, and settlements

### 2. Travel and Exploration

Implement travel mechanics using the journey planning system:

1. **Calculate travel times** based on terrain, roads, and weather
2. **Generate travel encounters** based on the regions being traversed
3. **Create descriptive narration** using the journey log descriptions
4. **Track party resources** (food, water, etc.) during travel

Example travel narration:

```python
def narrate_journey_segment(segment):
    """Create a narrative description of a journey segment for the players"""
    time = segment["time_of_day"]
    weather = segment["weather"]
    terrain = segment["terrain_type"]
    
    # Create a rich description
    narration = f"As {time} approaches, your party travels through {terrain}. "
    narration += f"The weather is {weather['description']}. "
    
    # Add terrain-specific details
    if terrain == "mountains":
        narration += "The path winds steeply upward, testing your endurance. "
    elif terrain == "forest":
        narration += "Dappled sunlight filters through the dense canopy above. "
    
    # Add encounter hooks
    if segment["has_settlement"]:
        narration += f"In the distance, you can see {segment['settlement_name']}. "
    
    return narration
```

### 3. Weather Effects

Implement gameplay effects based on weather conditions:

1. **Movement penalties** in severe weather
2. **Combat modifiers** (e.g., disadvantage on ranged attacks in high winds)
3. **Survival challenges** during extreme conditions
4. **Time-sensitive quests** affected by weather forecasts

Example weather effects system:

```python
def apply_weather_effects(character, weather_data):
    """Apply gameplay effects based on weather conditions"""
    effects = []
    
    # Temperature effects
    if weather_data["temperature"] < 32:  # Freezing
        effects.append({
            "type": "movement",
            "modifier": -0.25,
            "description": "Difficult movement in freezing conditions"
        })
    
    # Precipitation effects
    if weather_data["precipitation_type"] == "heavy_rain":
        effects.append({
            "type": "perception",
            "modifier": -2,
            "description": "Limited visibility in heavy rain"
        })
        effects.append({
            "type": "ranged_attacks",
            "modifier": -2,
            "description": "Difficult to aim in heavy rain"
        })
    
    # Wind effects
    if weather_data["wind_speed"] > 0.7:  # Strong wind
        effects.append({
            "type": "ranged_attacks",
            "modifier": -3,
            "description": "Strong winds affecting ranged attacks"
        })
    
    return effects
```

### 4. Dynamic World Events

Create a living world with events influenced by the map:

1. **Political conflicts** between neighboring territories
2. **Natural disasters** like floods along rivers or avalanches in mountains
3. **Seasonal changes** affecting terrain accessibility and resources
4. **Trade routes** following roads between settlements

Example dynamic event system:

```python
def generate_regional_events(map_system, current_day):
    """Generate events based on map data and current day"""
    events = []
    
    # Check for political tensions
    political_layer = map_system.get_layer("kingdoms")
    for territory_id in range(political_layer.num_territories):
        neighbors = political_layer.get_neighboring_territories(territory_id)
        for neighbor_id in neighbors:
            # Calculate tension based on shared border length and resources
            tension = calculate_tension(political_layer, territory_id, neighbor_id)
            if tension > 0.8:
                events.append({
                    "type": "political",
                    "subtype": "border_skirmish",
                    "location": political_layer.get_border_point(territory_id, neighbor_id),
                    "description": f"Border skirmish between {political_layer.get_territory_name(territory_id)} and {political_layer.get_territory_name(neighbor_id)}"
                })
    
    # Check for flooding along rivers
    rivers_layer = map_system.get_layer("rivers")
    weather_system = WeatherSystem(map_system.base_seed)
    for river in rivers_layer.rivers:
        # Check recent rainfall in the river's watershed
        rainfall = weather_system.get_regional_rainfall(river[0], days=3)
        if rainfall > 0.8:
            events.append({
                "type": "natural",
                "subtype": "flooding",
                "location": river[len(river)//2],  # Middle of the river
                "description": f"Heavy rainfall has caused flooding along the river"
            })
    
    return events
```

## Advanced Features

### 1. Procedural Quest Generation

Generate quests based on map features:

```python
def generate_location_based_quests(map_system, player_position):
    """Generate quests based on nearby map features"""
    quests = []
    x, y = player_position
    search_radius = 50
    
    # Check for nearby settlements
    settlements_layer = map_system.get_layer("settlements")
    for settlement in settlements_layer.settlements:
        sx, sy = settlement["position"]
        distance = ((x - sx)**2 + (y - sy)**2)**0.5
        if distance < search_radius:
            # Generate a settlement-based quest
            quest_type = random.choice(["delivery", "rescue", "investigation"])
            quests.append({
                "type": quest_type,
                "location": (sx, sy),
                "settlement": settlement["name"],
                "description": f"{quest_type.title()} quest in {settlement['name']}"
            })
    
    # Check for nearby terrain features
    terrain_layer = map_system.get_layer("terrain")
    for dx in range(-search_radius, search_radius+1):
        for dy in range(-search_radius, search_radius+1):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < map_system.width and 0 <= ny < map_system.height):
                continue
                
            terrain_data = terrain_layer.get_data_at(nx, ny)
            if terrain_data["terrain_type"] == "mountains":
                quests.append({
                    "type": "exploration",
                    "location": (nx, ny),
                    "description": "Rumors of an ancient dwarf mine in the mountains"
                })
            elif terrain_data["terrain_type"] == "forest" and random.random() < 0.1:
                quests.append({
                    "type": "hunting",
                    "location": (nx, ny),
                    "description": "Reports of a dangerous beast in the forest"
                })
    
    return quests
```

### 2. Faction Influence Maps

Create influence maps showing the reach of different factions:

```python
def generate_faction_influence(map_system, factions):
    """Generate influence maps for different factions"""
    width, height = map_system.width, map_system.height
    influence_maps = {}
    
    for faction in factions:
        # Create an influence map for this faction
        influence = np.zeros((height, width))
        
        # Add influence from faction strongholds
        for stronghold in faction["strongholds"]:
            x, y = stronghold["position"]
            strength = stronghold["strength"]
            radius = stronghold["influence_radius"]
            
            # Add influence in a radius around the stronghold
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                        
                    # Calculate distance-based influence
                    distance = ((dx**2 + dy**2)**0.5)
                    if distance <= radius:
                        influence_value = strength * (1 - distance/radius)
                        influence[ny][nx] += influence_value
        
        influence_maps[faction["name"]] = influence
    
    return influence_maps
```

### 3. Time-Based Map Changes

Implement changes to the map over time:

```python
def update_map_for_season(map_system, season):
    """Update map data based on the current season"""
    terrain_layer = map_system.get_layer("terrain")
    rivers_layer = map_system.get_layer("rivers")
    
    if season == "winter":
        # Freeze water in northern regions
        for y in range(map_system.height):
            for x in range(map_system.width):
                # Northern half of map
                if y < map_system.height / 2:
                    terrain_data = terrain_layer.get_data_at(x, y)
                    if terrain_data and terrain_data["is_water"]:
                        # Mark as frozen
                        terrain_layer.set_data_at(x, y, {"is_frozen": True})
        
        # Reduce river sizes
        for river in rivers_layer.rivers:
            for i, (rx, ry) in enumerate(river):
                river_data = rivers_layer.get_data_at(rx, ry)
                if river_data:
                    # Reduce river size in winter
                    new_size = max(1, river_data["river_size"] * 0.7)
                    rivers_layer.set_data_at(rx, ry, {"river_size": new_size})
    
    elif season == "spring":
        # Thaw frozen water
        for y in range(map_system.height):
            for x in range(map_system.width):
                terrain_data = terrain_layer.get_data_at(x, y)
                if terrain_data and terrain_data.get("is_frozen", False):
                    # Remove frozen flag
                    terrain_layer.set_data_at(x, y, {"is_frozen": False})
        
        # Increase river sizes due to snowmelt
        for river in rivers_layer.rivers:
            for i, (rx, ry) in enumerate(river):
                river_data = rivers_layer.get_data_at(rx, ry)
                if river_data:
                    # Increase river size in spring
                    new_size = river_data["river_size"] * 1.5
                    rivers_layer.set_data_at(rx, ry, {"river_size": new_size})
```

## Conclusion

The map system provides a rich foundation for creating immersive RPG worlds with realistic geography, weather, and travel. By integrating these elements into your game mechanics, you can create a more dynamic and engaging experience for your players.
