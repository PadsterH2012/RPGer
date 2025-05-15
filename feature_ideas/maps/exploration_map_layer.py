"""
Exploration Map Layer

This module implements a "fog of war" system that only reveals areas of the world
that players have personally explored or learned about through in-game means.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

# Create a circular import workaround
# Define BaseLayer here if it can't be imported
try:
    from seed_based_layered_map_system import BaseLayer
except ImportError:
    # Define a minimal BaseLayer for this file to work
    class BaseLayer:
        """Base class for all map layers"""
        def __init__(self, seed, parameters=None):
            self.seed = seed
            self.parameters = parameters or {}
            self.data = None
            self.width = parameters.get("width", 1024) if parameters else 1024
            self.height = parameters.get("height", 1024) if parameters else 1024
            self.generated = False
            self.layer_type = "base"  # Override in subclasses


class ExplorationMapLayer(BaseLayer):
    """Layer tracking player knowledge of the world"""
    
    # Exploration state constants
    UNEXPLORED = 0
    KNOWN = 1
    MAPPED = 2
    EXPLORED = 3
    
    def __init__(self, seed, parameters=None):
        super().__init__(seed, parameters)
        self.layer_type = "exploration"
        self.exploration_grid = None
        self.player_position_history = []
        self.known_locations = {}  # Dict of named locations the player knows
        
    def generate(self):
        """Initialize a blank exploration map"""
        self.exploration_grid = np.zeros((self.height, self.width), dtype=np.uint8)
        self.generated = True
        return self
        
    def mark_explored(self, x, y, radius=10):
        """Mark an area as explored by the player"""
        if not self.generated:
            self.generate()
            
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
        if not self.generated:
            self.generate()
            
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
        if not self.generated:
            self.generate()
            
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
        if not self.generated:
            self.generate()
            
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
            self.generate()
            
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
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except IOError:
            # Fallback to default font
            font = ImageFont.load_default()
            
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


# Example usage when run directly
if __name__ == "__main__":
    try:
        from seed_based_layered_map_system import MapSystem
        
        # Create a map system
        map_system = MapSystem(base_seed=12345, width=512, height=512)
        
        # Add terrain layer
        map_system.add_layer("terrain", "terrain")
        map_system.generate_all_layers()
        
        # Add exploration layer
        exploration_layer = ExplorationMapLayer(12345, {"width": 512, "height": 512})
        
        # Mark some areas as explored
        exploration_layer.mark_explored(250, 250, radius=30)
        exploration_layer.mark_explored(300, 270, radius=25)
        
        # Mark some areas as known
        exploration_layer.mark_known(400, 200, radius=40, name="Eldoria")
        exploration_layer.mark_route_known((300, 270), (400, 200), width=3)
        
        # Add a mapped region
        exploration_layer.add_map_knowledge((100, 100, 200, 200))
        
        # Visualize the player's map
        player_map = visualize_player_map(map_system, exploration_layer, "player_map.png")
        print("Player map saved to player_map.png")
        
    except ImportError as e:
        print(f"Error importing map modules: {e}")
        print("Make sure seed_based_layered_map_system.py is in the same directory.")
