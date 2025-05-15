# Player Exploration Map System

## Overview

The Player Exploration Map implements a "fog of war" system that only reveals areas of the world that players have personally explored or learned about through in-game means. This creates a sense of discovery and exploration as players gradually uncover the world map through their adventures.

## Core Concepts

### 1. Exploration States

Each map tile can exist in one of several states for the player:

- **Unexplored**: The player has no knowledge of this area (blank/fog)
- **Known**: The player has heard about this area but hasn't visited (basic outline)
- **Explored**: The player has personally visited this area (fully visible)
- **Mapped**: The player has obtained a map of this area (visible but less detailed than explored)

### 2. Knowledge Sources

Players can gain knowledge of the map through various means:

- **Direct Exploration**: Areas the player character physically visits
- **Maps**: In-game items that reveal specific regions
- **NPC Information**: Knowledge gained through conversation
- **Faction Knowledge**: Information shared by allied factions
- **Magical Scrying**: Supernatural means of viewing distant locations

## Implementation

### ExplorationMapLayer Class

```python
class ExplorationMapLayer(BaseLayer):
    """Layer tracking player knowledge of the world"""
    
    # Exploration state constants
    UNEXPLORED = 0
    KNOWN = 1
    MAPPED = 2
    EXPLORED = 3
    
    def __init__(self, seed=None, width=512, height=512):
        super().__init__(seed, width, height)
        self.layer_type = "exploration"
        self.exploration_grid = None
        self.player_position_history = []
        self.known_locations = {}  # Dict of named locations the player knows
        
    def initialize(self):
        """Initialize a blank exploration map"""
        self.exploration_grid = np.zeros((self.height, self.width), dtype=np.uint8)
        self.generated = True
        return self
        
    def mark_explored(self, x, y, radius=10):
        """Mark an area as explored by the player"""
        # Record player position
        self.player_position_history.append((x, y))
        
        # Mark area within radius as explored
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                    
                # Calculate distance from center
                distance = ((dx**2 + dy**2)**0.5)
                
                if distance <= radius:
                    # Mark as explored
                    self.exploration_grid[ny][nx] = self.EXPLORED
                    
                    # Gradually reduce visibility at edges
                    edge_distance = radius - distance
                    if edge_distance < 3 and self.exploration_grid[ny][nx] < self.KNOWN:
                        self.exploration_grid[ny][nx] = self.KNOWN
        
        return self
        
    def mark_known(self, x, y, radius=20, name=None):
        """Mark an area as known but not explored"""
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                    
                # Calculate distance from center
                distance = ((dx**2 + dy**2)**0.5)
                
                if distance <= radius:
                    # Only update if not already explored
                    if self.exploration_grid[ny][nx] < self.KNOWN:
                        self.exploration_grid[ny][nx] = self.KNOWN
        
        # Record named location if provided
        if name:
            self.known_locations[(x, y)] = {
                "name": name,
                "state": "known"
            }
        
        return self
        
    def add_map_knowledge(self, region_bounds, detail_level=2):
        """Add knowledge from acquiring a map of a region"""
        x_min, y_min, x_max, y_max = region_bounds
        
        # Ensure bounds are within map
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(self.width - 1, x_max)
        y_max = min(self.height - 1, y_max)
        
        # Mark region as mapped
        for y in range(y_min, y_max + 1):
            for x in range(x_min, x_max + 1):
                # Don't downgrade from explored to mapped
                if self.exploration_grid[y][x] < self.MAPPED:
                    self.exploration_grid[y][x] = self.MAPPED
        
        return self
        
    def mark_route_known(self, start, end, width=3):
        """Mark a route between two points as known"""
        x1, y1 = start
        x2, y2 = end
        
        # Use Bresenham's line algorithm to find points along the route
        points = self._get_line_points(x1, y1, x2, y2)
        
        # Mark points along the route
        for x, y in points:
            # Mark the route with some width
            for dx in range(-width, width+1):
                for dy in range(-width, width+1):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                        
                    # Calculate distance from route
                    distance = ((dx**2 + dy**2)**0.5)
                    
                    if distance <= width:
                        # Only update if not already explored
                        if self.exploration_grid[ny][nx] < self.KNOWN:
                            self.exploration_grid[ny][nx] = self.KNOWN
        
        return self
        
    def _get_line_points(self, x1, y1, x2, y2):
        """Get points along a line using Bresenham's algorithm"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
                
        return points
        
    def get_data_at(self, x, y):
        """Get exploration data at specific coordinates"""
        if not self.generated:
            self.initialize()
            
        if 0 <= x < self.width and 0 <= y < self.height:
            state = int(self.exploration_grid[y][x])
            return {
                "exploration_state": state,
                "is_unexplored": state == self.UNEXPLORED,
                "is_known": state >= self.KNOWN,
                "is_mapped": state >= self.MAPPED,
                "is_explored": state == self.EXPLORED
            }
        return None
```

### Rendering the Player Map

```python
def visualize_player_map(map_system, exploration_layer, output_path=None):
    """Create a visualization of the map from the player's perspective"""
    width = map_system.width
    height = map_system.height
    
    # Create a blank image (dark gray for unexplored)
    player_map = Image.new('RGB', (width, height), (40, 40, 40))
    draw = ImageDraw.Draw(player_map)
    
    # Get the base terrain for reference
    terrain_layer = map_system.get_layer("terrain")
    
    # Process each pixel
    for y in range(height):
        for x in range(width):
            # Get exploration state
            exp_data = exploration_layer.get_data_at(x, y)
            if not exp_data:
                continue
                
            # Skip unexplored areas (leave as blank/fog)
            if exp_data["is_unexplored"]:
                continue
                
            # Get terrain data for this point
            terrain_data = terrain_layer.get_data_at(x, y)
            if not terrain_data:
                continue
                
            # Render based on exploration state
            if exp_data["is_explored"]:
                # Fully explored - show full detail
                if terrain_data["is_water"]:
                    player_map.putpixel((x, y), (65, 105, 225))  # Blue for water
                elif terrain_data["terrain_type"] == "mountains":
                    player_map.putpixel((x, y), (139, 137, 137))  # Gray for mountains
                elif terrain_data["terrain_type"] == "hills":
                    player_map.putpixel((x, y), (160, 82, 45))  # Brown for hills
                else:
                    player_map.putpixel((x, y), (34, 139, 34))  # Green for land
                    
            elif exp_data["is_mapped"]:
                # Mapped but not explored - show less detail
                if terrain_data["is_water"]:
                    player_map.putpixel((x, y), (100, 149, 237))  # Lighter blue
                elif terrain_data["terrain_type"] in ["mountains", "hills"]:
                    player_map.putpixel((x, y), (169, 169, 169))  # Light gray for elevation
                else:
                    player_map.putpixel((x, y), (144, 238, 144))  # Light green
                    
            elif exp_data["is_known"]:
                # Only known - show basic outlines
                if terrain_data["is_water"]:
                    player_map.putpixel((x, y), (176, 196, 222))  # Very light blue
                else:
                    player_map.putpixel((x, y), (211, 211, 211))  # Very light gray
    
    # Add known locations and routes
    for pos, location in exploration_layer.known_locations.items():
        x, y = pos
        # Draw a small circle for the location
        draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 0, 0))
        
        # Add the name
        font = ImageFont.truetype("arial.ttf", 12)
        draw.text((x+5, y-5), location["name"], fill=(255, 255, 255), font=font)
    
    # Add player position history as a path
    points = exploration_layer.player_position_history
    if len(points) > 1:
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            draw.line((x1, y1, x2, y2), fill=(255, 0, 0), width=2)
    
    # Save or show the map
    if output_path:
        player_map.save(output_path)
    
    return player_map
```

## Integration with Game Mechanics

### 1. Automatic Exploration

As players move through the world, automatically update their exploration map:

```python
def update_player_exploration(player, map_system):
    """Update exploration map based on player movement"""
    # Get current position
    x, y = player.position
    
    # Get exploration layer
    exploration_layer = map_system.get_layer("exploration")
    
    # Mark current area as explored
    visibility_radius = 10  # Base visibility
    
    # Adjust for conditions
    if player.has_skill("keen_eye"):
        visibility_radius += 2
    
    # Weather effects
    weather = map_system.get_weather_at(x, y)
    if weather["fog"] > 0.5:
        visibility_radius -= 3
    if weather["precipitation"] > 0.7:
        visibility_radius -= 2
    
    # Time of day effects
    if player.time_of_day == "night":
        visibility_radius -= 5
    
    # Ensure minimum visibility
    visibility_radius = max(3, visibility_radius)
    
    # Mark area as explored
    exploration_layer.mark_explored(x, y, radius=visibility_radius)
```

### 2. Acquiring Maps

Allow players to find or purchase maps that reveal regions:

```python
def acquire_map(player, map_name, map_system):
    """Player acquires a map item that reveals a region"""
    # Define map regions
    map_regions = {
        "Northern Highlands": (100, 50, 300, 150),
        "Coastal Regions": (350, 200, 500, 400),
        "Southern Plains": (100, 350, 300, 450),
        # Add more regions as needed
    }
    
    if map_name in map_regions:
        # Get region bounds
        region_bounds = map_regions[map_name]
        
        # Get exploration layer
        exploration_layer = map_system.get_layer("exploration")
        
        # Add map knowledge
        exploration_layer.add_map_knowledge(region_bounds)
        
        # Add to player inventory
        player.add_to_inventory({
            "type": "map",
            "name": f"Map of {map_name}",
            "description": f"A detailed map showing the geography of {map_name}."
        })
        
        return f"You have acquired a map of {map_name}. Your world map has been updated."
    else:
        return f"Map of {map_name} not found."
```

### 3. Learning from NPCs

Allow players to learn about locations from NPCs:

```python
def learn_location_from_npc(player, location_name, coordinates, map_system):
    """Player learns about a location from an NPC"""
    x, y = coordinates
    
    # Get exploration layer
    exploration_layer = map_system.get_layer("exploration")
    
    # Mark location as known
    exploration_layer.mark_known(x, y, radius=15, name=location_name)
    
    # Also mark a route if the NPC provides directions
    current_x, current_y = player.position
    exploration_layer.mark_route_known((current_x, current_y), (x, y), width=2)
    
    return f"You've learned about {location_name}. It has been marked on your map."
```

## Example Usage

```python
# Create a map system
map_system = MapSystem(base_seed=12345)

# Add standard layers
map_system.add_layer("terrain", "terrain")
map_system.add_layer("rivers", "rivers")
map_system.add_layer("kingdoms", "political")
map_system.add_layer("settlements", "settlements")

# Add exploration layer
map_system.add_layer("exploration", "exploration")
exploration_layer = map_system.get_layer("exploration")

# Initialize player at starting position
player_x, player_y = 250, 250
exploration_layer.mark_explored(player_x, player_y, radius=15)

# Player travels to a new location
player_x, player_y = 270, 280
exploration_layer.mark_explored(player_x, player_y, radius=15)

# Player learns about a distant city from an NPC
exploration_layer.mark_known(350, 200, radius=20, name="Eldoria")
exploration_layer.mark_route_known((player_x, player_y), (350, 200), width=2)

# Player finds a map of the coastal regions
exploration_layer.add_map_knowledge((300, 150, 500, 350))

# Generate player's view of the map
player_map = visualize_player_map(map_system, exploration_layer, "player_map.png")
```

## Future Enhancements

1. **Memory Decay**: Gradually reduce detail of areas not visited for a long time
2. **Landmark Recognition**: Automatically identify and name distinctive terrain features
3. **Map Sharing**: Allow multiple players to combine their exploration knowledge
4. **Map Annotations**: Let players add their own notes and markers to the map
5. **Treasure Maps**: Special maps that reveal hidden locations with partial/cryptic information
