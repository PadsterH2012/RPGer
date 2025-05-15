"""
Additional Map Layers for Seed-Based Layered Map System

This file contains additional layer implementations for the seed-based map system.
These layers build upon the base architecture defined in seed_based_layered_map_system.py.
"""

import numpy as np
from queue import PriorityQueue

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


class RiversLayer(BaseLayer):
    """Layer for rivers that depend on terrain"""
    def __init__(self, seed, parameters=None):
        super().__init__(seed, parameters)
        self.layer_type = "rivers"
        self.rivers = []  # List of river paths
        self.river_grid = None  # Grid representation of rivers

    def generate(self, terrain_layer=None):
        """Generate rivers based on terrain elevation"""
        if terrain_layer is None:
            raise ValueError("Rivers layer requires a terrain layer")

        np.random.seed(self.seed)

        # Parameters
        num_rivers = self.parameters.get("num_rivers", 20)
        min_length = self.parameters.get("min_length", 20)
        meander_factor = self.parameters.get("meander_factor", 0.4)
        flow_strength = self.parameters.get("flow_strength", 0.8)

        # Initialize river grid (0 = no river, 1+ = river with flow volume)
        self.river_grid = np.zeros((self.height, self.width), dtype=np.uint8)

        # Generate rivers starting from random mountain points
        self.rivers = []
        for _ in range(num_rivers):
            # Find a suitable starting point (higher elevation)
            for _ in range(100):  # Try up to 100 times to find a good start
                x = np.random.randint(0, self.width)
                y = np.random.randint(0, self.height)

                # Check if it's a mountain or hill
                terrain_data = terrain_layer.get_data_at(x, y)
                if terrain_data and terrain_data["terrain_type"] in ["mountains", "hills"]:
                    # Start a river here
                    river_path = self._trace_river_path(x, y, terrain_layer, meander_factor, flow_strength)
                    if len(river_path) >= min_length:
                        self.rivers.append(river_path)

                        # Mark river on the grid with increasing size as it flows downhill
                        river_size = 1
                        for i, (rx, ry) in enumerate(river_path):
                            if 0 <= rx < self.width and 0 <= ry < self.height:
                                # Rivers get wider as they flow downhill (every 10 steps)
                                if i > 0 and i % 10 == 0:
                                    river_size += 1
                                self.river_grid[ry][rx] = max(self.river_grid[ry][rx], river_size)
                    break

        self.generated = True
        return self

    def _trace_river_path(self, start_x, start_y, terrain_layer, meander_factor=0.4, flow_strength=0.8):
        """Trace a river path from starting point to sea following elevation gradient with natural meandering"""
        path = [(start_x, start_y)]
        current_x, current_y = start_x, start_y

        # Store the starting elevation for calculating river size later
        start_elevation = terrain_layer.get_data_at(start_x, start_y)["elevation"]

        # Continue until we reach water or edge of map
        max_steps = 1000  # Prevent infinite loops
        for _ in range(max_steps):
            # Get all neighboring cells and their elevations
            neighbors = []

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = current_x + dx, current_y + dy

                    # Check bounds
                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue

                    # Check if already in path (avoid loops)
                    if (nx, ny) in path:
                        continue

                    # Get elevation
                    terrain_data = terrain_layer.get_data_at(nx, ny)
                    if terrain_data:
                        elev = terrain_data["elevation"]

                        # If we reached water, end the river
                        if not terrain_data["is_land"]:
                            path.append((nx, ny))
                            return path

                        # Calculate a score for this cell
                        # Lower elevation is better (multiplied by flow strength)
                        # Add randomness for meandering
                        randomness = np.random.uniform(-meander_factor, meander_factor)

                        # Diagonal movement should be slightly less preferred to avoid zigzag patterns
                        diagonal_penalty = 0.1 if dx != 0 and dy != 0 else 0

                        # Score combines elevation gradient and randomness
                        score = (elev * flow_strength) + randomness + diagonal_penalty

                        neighbors.append((nx, ny, elev, score))

            # If no valid neighbors, end the river
            if not neighbors:
                break

            # Sort by score (lowest first)
            neighbors.sort(key=lambda n: n[3])

            # Select the best cell, but occasionally pick the second or third best for natural variation
            selection_idx = 0
            if len(neighbors) > 1 and np.random.random() < 0.3:
                selection_idx = min(1, len(neighbors) - 1)
            if len(neighbors) > 2 and np.random.random() < 0.1:
                selection_idx = min(2, len(neighbors) - 1)

            next_x, next_y, next_elev, _ = neighbors[selection_idx]

            # If we're not going downhill anymore, end the river
            # (but allow small uphill sections occasionally for realism)
            current_elev = terrain_layer.get_data_at(current_x, current_y)["elevation"]
            if next_elev > current_elev + 0.05 and np.random.random() > 0.1:
                break

            # Move to the next point
            current_x, current_y = next_x, next_y
            path.append((current_x, current_y))

        return path

    def get_data_at(self, x, y):
        """Get river data at specific coordinates"""
        if not self.generated:
            self.generate()

        if 0 <= x < self.width and 0 <= y < self.height:
            river_value = int(self.river_grid[y][x])
            return {
                "has_river": river_value > 0,
                "river_size": river_value,  # Higher values = larger rivers (confluences)
                "elevation": 0  # This will be filled in by the rendering code
            }
        return None


class PoliticalLayer(BaseLayer):
    """Layer for political boundaries and territories"""
    def __init__(self, seed, parameters=None):
        super().__init__(seed, parameters)
        self.layer_type = "political"
        self.territories = []  # List of territory objects
        self.territory_grid = None  # Grid of territory IDs
        self.capitals = []  # List of capital locations

    def generate(self, terrain_layer=None, rivers_layer=None):
        """Generate political territories based on terrain and rivers"""
        if terrain_layer is None:
            raise ValueError("Political layer requires a terrain layer")

        np.random.seed(self.seed)

        # Parameters
        num_territories = self.parameters.get("num_territories", 8)

        # Initialize territory grid (-1 = no territory)
        self.territory_grid = np.full((self.height, self.width), -1, dtype=np.int16)

        # Generate capital locations (on land, preferably near water)
        self.capitals = self._place_capitals(num_territories, terrain_layer, rivers_layer)

        # Grow territories from capitals using a flood fill algorithm
        self._grow_territories(self.capitals, terrain_layer, rivers_layer)

        self.generated = True
        return self

    def _place_capitals(self, num_capitals, terrain_layer, rivers_layer):
        """Place capital cities in suitable locations"""
        capitals = []

        for i in range(num_capitals):
            # Try to find a good location (plains near rivers)
            for _ in range(100):  # Try up to 100 times
                x = np.random.randint(0, self.width)
                y = np.random.randint(0, self.height)

                terrain_data = terrain_layer.get_data_at(x, y)

                # Check if it's suitable land
                if terrain_data and terrain_data["terrain_type"] in ["plains", "hills"]:
                    # Prefer locations near rivers
                    near_river = False
                    if rivers_layer:
                        for dx in range(-3, 4):
                            for dy in range(-3, 4):
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < self.width and 0 <= ny < self.height:
                                    river_data = rivers_layer.get_data_at(nx, ny)
                                    if river_data and river_data["has_river"]:
                                        near_river = True
                                        break
                            if near_river:
                                break

                    # Check if far enough from other capitals
                    too_close = False
                    for cx, cy, _ in capitals:
                        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < self.width / (num_capitals * 0.5):
                            too_close = True
                            break

                    if not too_close:
                        # This is a good spot for a capital
                        capitals.append((x, y, i))  # x, y, territory_id
                        break

        return capitals

    def _grow_territories(self, capitals, terrain_layer, rivers_layer):
        """Grow territories from capital cities using a priority queue approach"""
        # Initialize with capitals
        for x, y, territory_id in capitals:
            self.territory_grid[y][x] = territory_id

        # Use a priority queue for expansion
        expansion_queue = PriorityQueue()

        # Add initial cells around capitals
        for x, y, territory_id in capitals:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        # Check if it's land
                        terrain_data = terrain_layer.get_data_at(nx, ny)
                        if terrain_data and terrain_data["is_land"]:
                            # Calculate expansion cost
                            cost = self._calculate_expansion_cost(nx, ny, territory_id, terrain_layer, rivers_layer)
                            # Add to queue (cost, x, y, territory_id)
                            expansion_queue.put((cost, nx, ny, territory_id))

        # Expand territories
        while not expansion_queue.empty():
            cost, x, y, territory_id = expansion_queue.get()

            # Check if this cell is already claimed
            if self.territory_grid[y][x] != -1:
                continue

            # Claim this cell
            self.territory_grid[y][x] = territory_id

            # Add neighbors to queue
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.territory_grid[ny][nx] == -1:
                        # Check if it's land
                        terrain_data = terrain_layer.get_data_at(nx, ny)
                        if terrain_data and terrain_data["is_land"]:
                            # Calculate expansion cost
                            cost = self._calculate_expansion_cost(nx, ny, territory_id, terrain_layer, rivers_layer)
                            # Add to queue
                            expansion_queue.put((cost, nx, ny, territory_id))

    def _calculate_expansion_cost(self, x, y, territory_id, terrain_layer, rivers_layer):
        """Calculate the cost of expanding a territory to a cell"""
        # Base cost
        cost = 1.0

        # Terrain factors
        terrain_data = terrain_layer.get_data_at(x, y)
        if terrain_data:
            # Different terrain types have different costs
            terrain_type = terrain_data["terrain_type"]
            if terrain_type == "mountains":
                cost *= 5.0  # Very hard to expand into mountains
            elif terrain_type == "hills":
                cost *= 2.0  # Harder to expand into hills
            elif terrain_type == "plains":
                cost *= 0.8  # Easy to expand into plains

        # River factors
        if rivers_layer:
            river_data = rivers_layer.get_data_at(x, y)
            if river_data and river_data["has_river"]:
                cost *= 3.0  # Rivers form natural borders

        # Distance from capital
        capital_x, capital_y, _ = self.capitals[territory_id]
        distance = np.sqrt((x - capital_x)**2 + (y - capital_y)**2)
        cost *= 1.0 + (distance / (self.width * 0.1))  # Harder to expand far from capital

        return cost

    def get_data_at(self, x, y):
        """Get political data at specific coordinates"""
        if not self.generated:
            self.generate()

        if 0 <= x < self.width and 0 <= y < self.height:
            territory_id = int(self.territory_grid[y][x])

            # Generate territory names if needed
            territory_names = self.parameters.get("territory_names", [])
            if territory_id >= 0:
                territory_name = territory_names[territory_id] if territory_id < len(territory_names) else f"Territory {territory_id}"

                # Check if this is a capital
                is_capital = False
                for cx, cy, tid in self.capitals:
                    if tid == territory_id and x == cx and y == cy:
                        is_capital = True
                        break

                return {
                    "territory_id": territory_id,
                    "territory_name": territory_name,
                    "is_capital": is_capital
                }
            else:
                return {
                    "territory_id": -1,
                    "territory_name": "Unclaimed",
                    "is_capital": False
                }
        return None
