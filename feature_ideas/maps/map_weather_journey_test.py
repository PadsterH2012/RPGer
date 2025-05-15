"""
Map Weather Journey Test

This script demonstrates a complete test of the seed-based map system with dynamic weather,
simulating a 10-turn journey across the map with descriptive narration.

The test includes:
1. Creating a map with terrain, rivers, and settlements
2. Generating a dynamic weather system for the map
3. Visualizing the map with added details
4. Simulating a journey with descriptive narration at each step
"""

import numpy as np
import matplotlib.pyplot as plt
import noise
import json
import time
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Global variables
current_map_seed = None
# Travel pace in miles per 6-hour period
TRAVEL_PACE = {
    "road": 18,  # 3 miles/hour × 6 hours
    "clear": 18,  # Plains, beaches
    "difficult": 12,  # Forests, hills
    "very_difficult": 6  # Mountains, swamps
}

# Import from our map system modules
# Assuming these files are in the same directory
try:
    from seed_based_layered_map_system import MapSystem, TerrainLayer, BaseLayer
    from additional_map_layers import RiversLayer, PoliticalLayer
except ImportError as e:
    print(f"Error importing map modules: {e}")
    print("Make sure seed_based_layered_map_system.py and additional_map_layers.py are in the same directory.")
    raise

# Create output directory if it doesn't exist
Path("output").mkdir(exist_ok=True)

class SettlementsLayer:
    """Layer for settlements (cities, towns, villages) and roads"""
    def __init__(self, seed, parameters=None):
        self.seed = seed
        self.parameters = parameters or {}
        self.width = parameters.get("width", 1024)
        self.height = parameters.get("height", 1024)
        self.layer_type = "settlements"
        self.settlements = []  # List of settlement objects
        self.roads = []  # List of road segments
        self.paths = []  # List of path segments (smaller than roads)
        self.generated = False

    def generate(self, terrain_layer=None, rivers_layer=None, political_layer=None):
        """Generate settlements based on terrain, rivers, and political boundaries"""
        if terrain_layer is None:
            raise ValueError("Settlements layer requires a terrain layer")

        np.random.seed(self.seed)

        # Parameters
        num_cities = self.parameters.get("num_cities", 5)
        num_towns = self.parameters.get("num_towns", 10)
        num_villages = self.parameters.get("num_villages", 20)

        # Generate cities (larger settlements, often capitals)
        self.settlements = []

        # If we have a political layer, use capitals as cities
        if political_layer and hasattr(political_layer, 'capitals'):
            for x, y, territory_id in political_layer.capitals:
                # Get territory name if available
                territory_name = "Unknown"
                if hasattr(political_layer, 'parameters') and 'territory_names' in political_layer.parameters:
                    if territory_id < len(political_layer.parameters['territory_names']):
                        territory_name = political_layer.parameters['territory_names'][territory_id]

                city_name = self._generate_settlement_name("city")
                self.settlements.append({
                    'type': 'city',
                    'name': f"{city_name}, Capital of {territory_name}",
                    'x': x,
                    'y': y,
                    'population': np.random.randint(8000, 50000),
                    'is_capital': True,
                    'territory_id': territory_id
                })

            # Adjust number of additional cities
            num_cities = max(0, num_cities - len(political_layer.capitals))

        # Generate remaining cities
        for _ in range(num_cities):
            self._place_settlement("city", terrain_layer, rivers_layer, political_layer)

        # Generate towns
        for _ in range(num_towns):
            self._place_settlement("town", terrain_layer, rivers_layer, political_layer)

        # Generate villages
        for _ in range(num_villages):
            self._place_settlement("village", terrain_layer, rivers_layer, political_layer)

        # Generate roads and paths connecting settlements
        self._generate_road_network(terrain_layer, rivers_layer)

        self.generated = True
        return self

    def _generate_road_network(self, terrain_layer, rivers_layer):
        """Generate a network of roads and paths connecting settlements"""
        # Clear existing roads and paths
        self.roads = []
        self.paths = []

        # Sort settlements by importance
        cities = [s for s in self.settlements if s['type'] == 'city']
        towns = [s for s in self.settlements if s['type'] == 'town']
        villages = [s for s in self.settlements if s['type'] == 'village']

        # Connect all cities to each other with major roads
        for i, city1 in enumerate(cities):
            for city2 in cities[i+1:]:
                # Check if they're in the same territory (if territory info exists)
                same_territory = False
                if 'territory_id' in city1 and 'territory_id' in city2:
                    same_territory = city1['territory_id'] == city2['territory_id'] and city1['territory_id'] != -1

                # Cities in the same territory are more likely to have direct roads
                if same_territory or np.random.random() < 0.8:  # Increased probability
                    road = self._generate_road(
                        city1['x'], city1['y'],
                        city2['x'], city2['y'],
                        terrain_layer, rivers_layer,
                        road_type="major"
                    )
                    if road:
                        self.roads.append(road)

        # Connect towns to nearest city with medium roads
        for town in towns:
            # Find nearest city
            nearest_city = None
            min_distance = float('inf')

            for city in cities:
                dist = np.sqrt((town['x'] - city['x'])**2 + (town['y'] - city['y'])**2)
                if dist < min_distance:
                    min_distance = dist
                    nearest_city = city

            # Connect town to nearest city
            if nearest_city and (min_distance < 250 or np.random.random() < 0.9):  # Increased range and probability
                road = self._generate_road(
                    town['x'], town['y'],
                    nearest_city['x'], nearest_city['y'],
                    terrain_layer, rivers_layer,
                    road_type="medium"
                )
                if road:
                    self.roads.append(road)

            # Connect towns to other nearby towns
            for other_town in towns:
                if town == other_town:
                    continue

                dist = np.sqrt((town['x'] - other_town['x'])**2 + (town['y'] - other_town['y'])**2)
                if dist < 150 and np.random.random() < 0.6:  # Increased range and probability
                    road = self._generate_road(
                        town['x'], town['y'],
                        other_town['x'], other_town['y'],
                        terrain_layer, rivers_layer,
                        road_type="medium"
                    )
                    if road:
                        self.roads.append(road)

        # Connect villages to nearest town or city with minor roads/paths
        for village in villages:
            # Find nearest settlement (town or city)
            nearest = None
            min_distance = float('inf')

            for settlement in cities + towns:
                dist = np.sqrt((village['x'] - settlement['x'])**2 + (village['y'] - settlement['y'])**2)
                if dist < min_distance:
                    min_distance = dist
                    nearest = settlement

            # Connect village to nearest settlement
            if nearest and (min_distance < 150 or np.random.random() < 0.95):  # Increased range and probability
                # Determine if it's a minor road or just a path
                road_type = "minor" if nearest['type'] == 'city' or np.random.random() < 0.4 else "path"

                road = self._generate_road(
                    village['x'], village['y'],
                    nearest['x'], nearest['y'],
                    terrain_layer, rivers_layer,
                    road_type=road_type
                )

                if road:
                    if road_type == "path":
                        self.paths.append(road)
                    else:
                        self.roads.append(road)

            # Connect villages to other nearby villages with paths
            connected_to_any = False
            for other_village in villages:
                if village == other_village:
                    continue

                dist = np.sqrt((village['x'] - other_village['x'])**2 + (village['y'] - other_village['y'])**2)
                if dist < 80 and np.random.random() < 0.6:  # Increased range and probability
                    path = self._generate_road(
                        village['x'], village['y'],
                        other_village['x'], other_village['y'],
                        terrain_layer, rivers_layer,
                        road_type="path"
                    )
                    if path:
                        self.paths.append(path)
                        connected_to_any = True

            # If village is not connected to anything yet, force a connection to the nearest village
            if not connected_to_any:
                nearest_village = None
                min_distance = float('inf')

                for other_village in villages:
                    if village == other_village:
                        continue

                    dist = np.sqrt((village['x'] - other_village['x'])**2 + (village['y'] - other_village['y'])**2)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_village = other_village

                if nearest_village:
                    path = self._generate_road(
                        village['x'], village['y'],
                        nearest_village['x'], nearest_village['y'],
                        terrain_layer, rivers_layer,
                        road_type="path"
                    )
                    if path:
                        self.paths.append(path)

        # Ensure all settlements have at least one connection
        self._ensure_all_settlements_connected(terrain_layer, rivers_layer)

    def _ensure_all_settlements_connected(self, terrain_layer, rivers_layer):
        """Make sure all settlements have at least one connection to the road network"""
        # Check each settlement
        for settlement in self.settlements:
            # Skip if already connected
            if self._is_settlement_connected(settlement):
                continue

            # Find nearest connected settlement
            nearest = None
            min_distance = float('inf')

            for other in self.settlements:
                if settlement == other or not self._is_settlement_connected(other):
                    continue

                dist = np.sqrt((settlement['x'] - other['x'])**2 + (settlement['y'] - other['y'])**2)
                if dist < min_distance:
                    min_distance = dist
                    nearest = other

            # Connect to nearest connected settlement
            if nearest:
                # Determine road type based on settlement types
                if settlement['type'] == 'city' or nearest['type'] == 'city':
                    road_type = "medium"
                elif settlement['type'] == 'town' or nearest['type'] == 'town':
                    road_type = "minor"
                else:
                    road_type = "path"

                road = self._generate_road(
                    settlement['x'], settlement['y'],
                    nearest['x'], nearest['y'],
                    terrain_layer, rivers_layer,
                    road_type=road_type
                )

                if road:
                    if road_type == "path":
                        self.paths.append(road)
                    else:
                        self.roads.append(road)

    def _is_settlement_connected(self, settlement):
        """Check if a settlement is connected to any road or path"""
        x, y = settlement['x'], settlement['y']
        search_radius = 5

        # Check roads
        for road in self.roads:
            for rx, ry in road["points"]:
                if abs(x - rx) <= search_radius and abs(y - ry) <= search_radius:
                    return True

        # Check paths
        for path in self.paths:
            for px, py in path["points"]:
                if abs(x - px) <= search_radius and abs(y - py) <= search_radius:
                    return True

        return False

    def _generate_road(self, start_x, start_y, end_x, end_y, terrain_layer, rivers_layer, road_type="major"):
        """Generate a road between two points, following terrain contours"""
        # A* pathfinding with terrain-based costs
        import heapq

        # Define movement costs based on terrain and road type
        def get_movement_cost(x, y, prev_x, prev_y):
            # Default high cost for impassable terrain
            cost = 1000

            # Get terrain data
            terrain_data = terrain_layer.get_data_at(x, y)
            if not terrain_data:
                return cost

            # Base costs by terrain type
            if not terrain_data["is_land"]:
                return cost  # Can't build roads on water

            terrain_type = terrain_data["terrain_type"]
            if terrain_type == "beach":
                cost = 2.0
            elif terrain_type == "plains":
                cost = 1.0  # Easiest terrain for roads
            elif terrain_type == "hills":
                cost = 3.0  # Harder to build on hills
            elif terrain_type == "mountains":
                cost = 8.0  # Very hard to build on mountains
            elif terrain_type == "snow_peaks":
                cost = 15.0  # Extremely difficult

            # Check for rivers - crossing rivers is expensive
            if rivers_layer:
                river_data = rivers_layer.get_data_at(x, y)
                if river_data and river_data["has_river"]:
                    # Check if we're crossing the river (not just following it)
                    prev_river_data = rivers_layer.get_data_at(prev_x, prev_y)
                    if prev_river_data and prev_river_data["has_river"]:
                        # We're following the river, not crossing it
                        pass
                    else:
                        # We're crossing the river - expensive!
                        river_size = river_data["river_size"]
                        cost += river_size * 5

            # Prefer to follow existing roads
            for road in self.roads:
                if road["type"] != road_type:  # Only follow same or better road types
                    continue

                for rx, ry in road["points"]:
                    if abs(x - rx) <= 1 and abs(y - ry) <= 1:
                        cost *= 0.5  # Much cheaper to follow existing roads
                        break

            # Prefer gentler slopes - check elevation change
            if prev_x is not None and prev_y is not None:
                prev_terrain = terrain_layer.get_data_at(prev_x, prev_y)
                if prev_terrain:
                    elev_diff = abs(terrain_data["elevation"] - prev_terrain["elevation"])
                    cost *= (1.0 + elev_diff * 5.0)  # Steeper slopes are more expensive

            # Adjust cost based on road type
            if road_type == "major":
                cost *= 1.0  # Major roads can afford more expensive construction
            elif road_type == "medium":
                cost *= 1.2  # Medium roads try to avoid difficult terrain
            elif road_type == "minor":
                cost *= 1.5  # Minor roads strongly prefer easy terrain
            else:  # path
                cost *= 2.0  # Paths really want to follow easy routes

            return cost

        # A* implementation
        open_set = [(0, start_x, start_y, None)]  # (f_score, x, y, prev_direction)
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)}

        # Track previous positions for each node to calculate direction changes
        prev_pos = {}

        # Limit search to prevent very long roads
        max_iterations = 1000
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            _, current_x, current_y, prev_dir = heapq.heappop(open_set)

            # Check if we reached the destination
            if current_x == end_x and current_y == end_y:
                # Reconstruct path
                path = [(current_x, current_y)]
                while (current_x, current_y) in came_from:
                    current_x, current_y = came_from[(current_x, current_y)]
                    path.append((current_x, current_y))
                path.reverse()

                # Create road object
                return {
                    "type": road_type,
                    "points": path,
                    "start": (start_x, start_y),
                    "end": (end_x, end_y)
                }

            # Check neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                neighbor_x, neighbor_y = current_x + dx, current_y + dy

                # Check bounds
                if not (0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height):
                    continue

                # Determine direction of this move
                if dx == 0:
                    direction = "vertical"
                elif dy == 0:
                    direction = "horizontal"
                else:
                    direction = "diagonal"

                # Calculate movement cost
                movement_cost = get_movement_cost(neighbor_x, neighbor_y, current_x, current_y)
                if movement_cost >= 1000:  # Impassable
                    continue

                # Diagonal movement costs more
                if dx != 0 and dy != 0:
                    movement_cost *= 1.414  # sqrt(2)

                # Penalize direction changes (roads prefer to be straight)
                if prev_dir is not None and prev_dir != direction:
                    movement_cost *= 1.2  # Turning penalty

                # Calculate scores
                tentative_g = g_score[(current_x, current_y)] + movement_cost

                if (neighbor_x, neighbor_y) not in g_score or tentative_g < g_score[(neighbor_x, neighbor_y)]:
                    # This path is better
                    came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                    g_score[(neighbor_x, neighbor_y)] = tentative_g
                    f_score[(neighbor_x, neighbor_y)] = tentative_g + np.sqrt((end_x - neighbor_x)**2 + (end_y - neighbor_y)**2)

                    # Store the direction for the next step
                    prev_pos[(neighbor_x, neighbor_y)] = (current_x, current_y)

                    heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], neighbor_x, neighbor_y, direction))

        # No path found or too many iterations
        return None

    def _place_settlement(self, settlement_type, terrain_layer, rivers_layer, political_layer):
        """Place a settlement in a suitable location"""
        # Different settlement types have different preferences
        near_water_preference = 0.8  # Chance of wanting to be near water
        terrain_preferences = {
            "city": ["plains", "hills"],
            "town": ["plains", "hills", "beach"],
            "village": ["plains", "hills", "beach", "mountains"]
        }

        # Population ranges
        population_ranges = {
            "city": (5000, 30000),
            "town": (1000, 5000),
            "village": (50, 1000)
        }

        # Try to find a suitable location
        for _ in range(100):  # Try up to 100 times
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)

            # Check terrain suitability
            terrain_data = terrain_layer.get_data_at(x, y)
            if not terrain_data or not terrain_data["is_land"]:
                continue

            if terrain_data["terrain_type"] not in terrain_preferences[settlement_type]:
                continue

            # Check for water proximity if desired
            near_water = False
            if rivers_layer and np.random.random() < near_water_preference:
                # Check surrounding area for water
                search_radius = 5 if settlement_type == "city" else 3
                for dx in range(-search_radius, search_radius + 1):
                    for dy in range(-search_radius, search_radius + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            river_data = rivers_layer.get_data_at(nx, ny)
                            if river_data and river_data["has_river"]:
                                near_water = True
                                break
                    if near_water:
                        break

                if not near_water and settlement_type == "city":
                    continue  # Cities strongly prefer water access

            # Check if too close to another settlement
            too_close = False
            min_distance = 20 if settlement_type == "city" else 10 if settlement_type == "town" else 5
            for settlement in self.settlements:
                dist = np.sqrt((x - settlement['x'])**2 + (y - settlement['y'])**2)
                if dist < min_distance:
                    too_close = True
                    break

            if too_close:
                continue

            # Determine territory if political layer exists
            territory_id = -1
            if political_layer:
                political_data = political_layer.get_data_at(x, y)
                if political_data:
                    territory_id = political_data["territory_id"]

            # This is a good location - create the settlement
            name = self._generate_settlement_name(settlement_type)
            population = np.random.randint(*population_ranges[settlement_type])

            self.settlements.append({
                'type': settlement_type,
                'name': name,
                'x': x,
                'y': y,
                'population': population,
                'is_capital': False,
                'territory_id': territory_id,
                'near_water': near_water
            })

            return True

        return False  # Failed to place settlement

    def _generate_settlement_name(self, settlement_type):
        """Generate a random fantasy settlement name"""
        prefixes = ["Green", "High", "Fair", "Wood", "Stone", "River", "Lake", "North", "South", "East", "West",
                   "Old", "New", "Silver", "Golden", "Red", "Blue", "Black", "White", "Frost", "Sun", "Moon"]

        suffixes_by_type = {
            "city": ["hold", "keep", "tower", "fort", "guard", "watch", "spire", "crown", "throne", "haven", "refuge"],
            "town": ["ford", "bridge", "crossing", "mill", "stead", "market", "trade", "field", "garden", "grove"],
            "village": ["ton", "ville", "wick", "wood", "field", "hill", "dale", "valley", "glen", "hollow", "meadow"]
        }

        if np.random.random() < 0.5:
            # Two-part name
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes_by_type[settlement_type])
            return f"{prefix}{suffix}"
        else:
            # Simple name with suffix
            roots = ["Elm", "Oak", "Ash", "Thorn", "Mill", "Bur", "Mal", "Tyr", "Fen", "Bel", "Mor", "Wyn",
                    "Bran", "Carn", "Dun", "Bal", "Pen", "Ros", "Tre", "Pol", "Caer", "Aber", "Inver", "Lan"]
            suffix = random.choice(suffixes_by_type[settlement_type])
            return f"{random.choice(roots)}{suffix}"

    def get_data_at(self, x, y):
        """Get settlement data at specific coordinates"""
        if not self.generated:
            self.generate()

        # Check if there's a settlement at these coordinates
        for settlement in self.settlements:
            if settlement['x'] == x and settlement['y'] == y:
                return settlement

        return None  # No settlement at this location


class WeatherSystem:
    """Dynamic weather system for the map"""
    def __init__(self, seed, map_system, parameters=None):
        self.seed = seed
        self.map_system = map_system
        self.parameters = parameters or {}
        self.width = map_system.layers["terrain"].width
        self.height = map_system.layers["terrain"].height
        self.regional_weather = {}  # Weather patterns for each region
        self.current_date = parameters.get("start_date", datetime(1482, 3, 21))  # Default: spring equinox
        self.days_generated = parameters.get("days_generated", 100)

    def generate(self):
        """Generate weather patterns for all regions"""
        np.random.seed(self.seed)

        # Find all settlements to use as weather regions
        if "settlements" in self.map_system.layers:
            settlements_layer = self.map_system.layers["settlements"]
            for settlement in settlements_layer.settlements:
                if settlement['type'] in ['city', 'town']:  # Only use cities and towns as weather regions
                    region_id = f"{settlement['name']}_{settlement['x']}_{settlement['y']}"
                    self.regional_weather[region_id] = self._generate_regional_weather(
                        settlement['x'],
                        settlement['y'],
                        self.days_generated
                    )

        return self

    def _generate_regional_weather(self, x, y, num_days):
        """Generate weather pattern for a specific region"""
        # Get terrain data to determine base climate
        terrain_data = self.map_system.layers["terrain"].get_data_at(x, y)

        # Determine climate based on location and terrain
        # This is a simplified approach - could be much more complex
        base_temp = 60  # Base temperature in Fahrenheit

        # Adjust for y-coordinate (latitude) - northern areas are cooler
        latitude_factor = 1 - (y / self.height)
        base_temp -= latitude_factor * 40  # Up to 40 degrees cooler in the north

        # Adjust for elevation
        if terrain_data:
            if terrain_data["terrain_type"] in ["mountains", "snow_peaks"]:
                base_temp -= 20
            elif terrain_data["terrain_type"] == "hills":
                base_temp -= 5

        # Determine seasons based on current date
        # This is a simplified approach with 4 equal seasons
        daily_weather = []

        for day in range(num_days):
            current_day = self.current_date + timedelta(days=day)
            month = current_day.month

            # Determine season
            if 3 <= month <= 5:
                season = "spring"
                temp_modifier = np.random.normal(0, 8)  # Spring: moderate variability
                precip_chance = 0.4
            elif 6 <= month <= 8:
                season = "summer"
                temp_modifier = np.random.normal(15, 5)  # Summer: hotter, less variable
                precip_chance = 0.3
            elif 9 <= month <= 11:
                season = "autumn"
                temp_modifier = np.random.normal(0, 10)  # Autumn: moderate, more variable
                precip_chance = 0.5
            else:
                season = "winter"
                temp_modifier = np.random.normal(-20, 7)  # Winter: colder, variable
                precip_chance = 0.35

            # Calculate daily temperatures
            day_temp = base_temp + temp_modifier

            # Daily variation
            temps = {
                "morning": max(0, day_temp - 10 + np.random.normal(0, 3)),
                "midday": max(0, day_temp + 5 + np.random.normal(0, 2)),
                "evening": max(0, day_temp - 5 + np.random.normal(0, 2)),
                "night": max(0, day_temp - 15 + np.random.normal(0, 4))
            }

            # Determine precipitation
            has_precipitation = np.random.random() < precip_chance
            precipitation = {"type": "none", "intensity": "none", "duration_hours": 0}

            if has_precipitation:
                # Determine type based on temperature
                midday_temp = temps["midday"]
                if midday_temp < 32:  # Below freezing
                    precip_type = "snow"
                elif midday_temp < 40:  # Near freezing
                    precip_type = np.random.choice(["snow", "sleet", "freezing_rain"],
                                                 p=[0.5, 0.3, 0.2])
                else:
                    precip_type = "rain"

                # Determine intensity
                intensity = np.random.choice(["light", "moderate", "heavy"],
                                           p=[0.6, 0.3, 0.1])

                # Determine duration
                duration = np.random.randint(1, 12)  # 1-12 hours

                # Determine time of day
                time_of_day = np.random.choice(["morning", "midday", "evening", "night"])

                precipitation = {
                    "type": precip_type,
                    "intensity": intensity,
                    "duration_hours": duration,
                    "time_of_day": time_of_day
                }

            # Determine wind
            directions = ["north", "northeast", "east", "southeast", "south",
                         "southwest", "west", "northwest"]
            wind = {
                "direction": np.random.choice(directions),
                "speed": np.random.choice(["calm", "light", "moderate", "strong", "gale"],
                                        p=[0.1, 0.3, 0.4, 0.15, 0.05])
            }

            # Determine cloud cover (0-100%)
            if has_precipitation:
                cloud_cover = np.random.randint(60, 101)  # 60-100% for precipitation
            else:
                cloud_cover = np.random.randint(0, 81)  # 0-80% for no precipitation

            # Generate description tags
            tags = []
            if cloud_cover < 20:
                tags.append("clear")
            elif cloud_cover < 50:
                tags.append("partly cloudy")
            else:
                tags.append("overcast")

            if precipitation["type"] != "none":
                tags.append(precipitation["type"])
                tags.append(precipitation["intensity"])

            if wind["speed"] in ["strong", "gale"]:
                tags.append("windy")

            if temps["midday"] > 85:
                tags.append("hot")
            elif temps["midday"] > 70:
                tags.append("warm")
            elif temps["midday"] < 32:
                tags.append("freezing")
            elif temps["midday"] < 50:
                tags.append("cold")
            else:
                tags.append("mild")

            # Create daily weather entry
            daily_weather.append({
                "day_number": day + 1,
                "date": current_day.strftime("%Y-%m-%d"),
                "season": season,
                "temperature": temps,
                "precipitation": precipitation,
                "wind": wind,
                "cloud_cover": cloud_cover,
                "description_tags": tags
            })

        return daily_weather

    def get_weather_at(self, x, y, day_offset=0):
        """Get weather at specific coordinates and day"""
        if not self.regional_weather:
            self.generate()

        # Find the nearest weather regions
        nearest_regions = self._find_nearest_weather_regions(x, y)

        if not nearest_regions:
            return None

        # If only one region or very close to a region, use that region's weather
        if len(nearest_regions) == 1 or nearest_regions[0]["distance"] < 5:
            region_id = nearest_regions[0]["region_id"]
            day_idx = min(day_offset, len(self.regional_weather[region_id]) - 1)
            return self.regional_weather[region_id][day_idx]

        # Otherwise, interpolate between regions
        return self._interpolate_weather(nearest_regions, x, y, day_offset)

    def _find_nearest_weather_regions(self, x, y, max_regions=3):
        """Find the nearest weather regions to a point"""
        regions = []

        for region_id, weather_data in self.regional_weather.items():
            # Extract coordinates from region_id
            parts = region_id.split('_')
            region_x = int(parts[-2])
            region_y = int(parts[-1])

            # Calculate distance
            distance = np.sqrt((x - region_x)**2 + (y - region_y)**2)

            regions.append({
                "region_id": region_id,
                "distance": distance
            })

        # Sort by distance and return the closest ones
        regions.sort(key=lambda r: r["distance"])
        return regions[:max_regions]

    def _interpolate_weather(self, regions, x, y, day_offset):
        """Interpolate weather between multiple regions"""
        # Calculate weights based on inverse square distance
        total_weight = 0
        for region in regions:
            if region["distance"] == 0:
                region["weight"] = 1000  # Very high weight for exact matches
            else:
                region["weight"] = 1 / (region["distance"] ** 2)
            total_weight += region["weight"]

        # Normalize weights
        for region in regions:
            region["normalized_weight"] = region["weight"] / total_weight

        # Get weather for each region
        for region in regions:
            day_idx = min(day_offset, len(self.regional_weather[region["region_id"]]) - 1)
            region["weather"] = self.regional_weather[region["region_id"]][day_idx]

        # Interpolate numerical values
        result = {
            "day_number": regions[0]["weather"]["day_number"],
            "date": regions[0]["weather"]["date"],
            "season": regions[0]["weather"]["season"],
            "temperature": {
                "morning": self._weighted_average([r["weather"]["temperature"]["morning"] for r in regions],
                                               [r["normalized_weight"] for r in regions]),
                "midday": self._weighted_average([r["weather"]["temperature"]["midday"] for r in regions],
                                              [r["normalized_weight"] for r in regions]),
                "evening": self._weighted_average([r["weather"]["temperature"]["evening"] for r in regions],
                                               [r["normalized_weight"] for r in regions]),
                "night": self._weighted_average([r["weather"]["temperature"]["night"] for r in regions],
                                             [r["normalized_weight"] for r in regions])
            },
            "cloud_cover": self._weighted_average([r["weather"]["cloud_cover"] for r in regions],
                                               [r["normalized_weight"] for r in regions])
        }

        # For precipitation, use the highest weighted non-none value
        precip_regions = [r for r in regions if r["weather"]["precipitation"]["type"] != "none"]
        if precip_regions:
            # Sort by weight and use the highest weighted precipitation
            precip_regions.sort(key=lambda r: r["normalized_weight"], reverse=True)
            result["precipitation"] = precip_regions[0]["weather"]["precipitation"].copy()

            # If we're far from the precipitation region, reduce intensity
            if precip_regions[0]["distance"] > 20:
                if result["precipitation"]["intensity"] == "heavy":
                    result["precipitation"]["intensity"] = "moderate"
                elif result["precipitation"]["intensity"] == "moderate":
                    result["precipitation"]["intensity"] = "light"
        else:
            result["precipitation"] = {"type": "none", "intensity": "none", "duration_hours": 0}

        # For wind, use vector averaging for direction and weighted average for speed
        wind_speeds = {"calm": 0, "light": 1, "moderate": 2, "strong": 3, "gale": 4}
        wind_speed_names = ["calm", "light", "moderate", "strong", "gale"]

        # Convert directions to angles (in radians)
        direction_to_angle = {
            "north": 0, "northeast": np.pi/4, "east": np.pi/2, "southeast": 3*np.pi/4,
            "south": np.pi, "southwest": 5*np.pi/4, "west": 3*np.pi/2, "northwest": 7*np.pi/4
        }

        # Calculate weighted average of wind vectors
        x_component = 0
        y_component = 0
        speed_value = 0

        for region in regions:
            wind = region["weather"]["wind"]
            angle = direction_to_angle[wind["direction"]]
            speed = wind_speeds[wind["speed"]]

            # Add weighted vector components
            x_component += np.cos(angle) * speed * region["normalized_weight"]
            y_component += np.sin(angle) * speed * region["normalized_weight"]
            speed_value += speed * region["normalized_weight"]

        # Convert back to direction and speed
        if x_component == 0 and y_component == 0:
            direction = "north"  # Default if no wind
        else:
            angle = np.arctan2(y_component, x_component)
            if angle < 0:
                angle += 2 * np.pi

            # Convert angle back to direction
            direction_idx = int(round(angle / (np.pi/4))) % 8
            directions = ["north", "northeast", "east", "southeast",
                         "south", "southwest", "west", "northwest"]
            direction = directions[direction_idx]

        # Round speed to nearest category
        speed_idx = min(int(round(speed_value)), 4)
        speed = wind_speed_names[speed_idx]

        result["wind"] = {"direction": direction, "speed": speed}

        # Generate description tags
        tags = []
        if result["cloud_cover"] < 20:
            tags.append("clear")
        elif result["cloud_cover"] < 50:
            tags.append("partly cloudy")
        else:
            tags.append("overcast")

        if result["precipitation"]["type"] != "none":
            tags.append(result["precipitation"]["type"])
            tags.append(result["precipitation"]["intensity"])

        if result["wind"]["speed"] in ["strong", "gale"]:
            tags.append("windy")

        if result["temperature"]["midday"] > 85:
            tags.append("hot")
        elif result["temperature"]["midday"] > 70:
            tags.append("warm")
        elif result["temperature"]["midday"] < 32:
            tags.append("freezing")
        elif result["temperature"]["midday"] < 50:
            tags.append("cold")
        else:
            tags.append("mild")

        result["description_tags"] = tags

        return result

    def _weighted_average(self, values, weights):
        """Calculate weighted average of values"""
        return sum(v * w for v, w in zip(values, weights))


class JourneySimulator:
    """Simulates a journey across the map with descriptive narration"""
    def __init__(self, map_system, weather_system, start_point, end_point, num_days=3):
        self.map_system = map_system
        self.weather_system = weather_system
        self.start_point = start_point
        self.end_point = end_point
        self.num_days = num_days
        self.turns_per_day = 4  # morning, midday, evening, night
        self.total_turns = num_days * self.turns_per_day
        self.current_position = start_point
        self.current_day = 0
        self.current_time_of_day = 0  # 0=morning, 1=midday, 2=evening, 3=night
        self.journey_log = []
        self.resting = False
        self.times_of_day = ["morning", "midday", "evening", "night"]

    def simulate_journey(self):
        """Simulate the entire journey"""
        # Calculate path between start and end points
        path = self._calculate_path()

        if not path:
            return "No valid path could be found between the start and end points."

        # Make the path more natural by adding some randomness and following roads
        natural_path = self._naturalize_path(path)

        # Divide path into segments based on travel time and rest periods
        path_segments = self._plan_journey_with_rests(natural_path)

        # Simulate each turn
        turn_idx = 0
        day = 0
        time_of_day = 0  # 0=morning, 1=midday, 2=evening, 3=night

        for segment in path_segments:
            position = segment["position"]
            is_resting = segment["resting"]

            # Update current state
            self.current_position = position
            self.current_day = day
            self.current_time_of_day = time_of_day
            self.resting = is_resting

            # Generate description for this turn
            description = self._generate_turn_description(turn_idx + 1, position, is_resting)

            # Add to journey log
            self.journey_log.append({
                "turn": turn_idx + 1,
                "day": day + 1,
                "time_of_day": self.times_of_day[time_of_day],
                "position": position,
                "resting": is_resting,
                "miles_traveled": segment.get("miles_traveled", 0),
                "total_miles": segment.get("total_miles", 0),
                "description": description
            })

            # Update time and day
            turn_idx += 1
            time_of_day = (time_of_day + 1) % 4
            if time_of_day == 0:  # New day
                day += 1

            # Stop if we've reached the destination and it's the end of a day
            if position == self.end_point and time_of_day == 0:
                break

            # Stop if we've gone too long
            if turn_idx >= 40:  # Maximum 10 days
                break

        return self.journey_log

    def _naturalize_path(self, path):
        """Make the path more natural by following roads and terrain"""
        if not path or len(path) < 2:
            return path

        natural_path = [path[0]]  # Start with the first point

        # Process each segment of the path
        for i in range(len(path) - 1):
            start_x, start_y = path[i]
            end_x, end_y = path[i + 1]

            # Check if there's a road or path connecting these points
            road_path = self._find_road_path(start_x, start_y, end_x, end_y)

            if road_path:
                # Follow the road
                natural_path.extend(road_path[1:])  # Skip the first point as it's already in the path
            else:
                # No road, so add some natural variation
                segment_path = self._create_natural_segment(start_x, start_y, end_x, end_y)
                natural_path.extend(segment_path[1:])  # Skip the first point

        return natural_path

    def _find_road_path(self, start_x, start_y, end_x, end_y):
        """Find a path along roads between two points"""
        # Check if we have a settlements layer with roads
        if "settlements" not in self.map_system.layers:
            return None

        settlements_layer = self.map_system.layers["settlements"]
        if not hasattr(settlements_layer, 'roads') or not settlements_layer.roads:
            return None

        # Look for roads that might connect these points
        # This is a simplified approach - in a real system, you'd use a graph search

        # First, find roads that pass near the start and end points
        start_roads = []
        end_roads = []
        search_radius = 20

        for road in settlements_layer.roads + settlements_layer.paths:
            # Check if road passes near start point
            for point in road["points"]:
                if abs(point[0] - start_x) <= search_radius and abs(point[1] - start_y) <= search_radius:
                    start_roads.append((road, point))
                    break

            # Check if road passes near end point
            for point in road["points"]:
                if abs(point[0] - end_x) <= search_radius and abs(point[1] - end_y) <= search_radius:
                    end_roads.append((road, point))
                    break

        # If we found roads near both points, try to find a connection
        if start_roads and end_roads:
            # Check if any road connects both points
            for start_road, start_point in start_roads:
                for end_road, end_point in end_roads:
                    if start_road == end_road:
                        # Same road! Extract the segment
                        road_points = start_road["points"]
                        start_idx = road_points.index(start_point)
                        end_idx = road_points.index(end_point)

                        if start_idx == end_idx:
                            # Same point, just return it
                            return [start_point]
                        elif start_idx < end_idx:
                            # Forward segment
                            return road_points[start_idx:end_idx+1]
                        else:
                            # Reverse segment
                            return list(reversed(road_points[end_idx:start_idx+1]))

        # No direct road connection found
        return None

    def _create_natural_segment(self, start_x, start_y, end_x, end_y):
        """Create a more natural path segment between two points"""
        # Calculate direct distance
        distance = np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

        # If it's a short distance, just go direct
        if distance < 30:
            return [(start_x, start_y), (end_x, end_y)]

        # For longer distances, add some waypoints with variation
        num_waypoints = max(1, int(distance / 50))

        # Get terrain to follow natural features
        terrain_layer = self.map_system.layers["terrain"]

        waypoints = [(start_x, start_y)]

        for i in range(num_waypoints):
            # Calculate a point along the direct path
            progress = (i + 1) / (num_waypoints + 1)
            direct_x = start_x + (end_x - start_x) * progress
            direct_y = start_y + (end_y - start_y) * progress

            # Add some random variation
            # The variation is larger in the middle of the journey and smaller near the endpoints
            variation_factor = 4 * progress * (1 - progress)  # Peaks at 0.5
            max_deviation = distance * 0.2 * variation_factor

            # Try several potential waypoints and pick the best one
            best_point = (direct_x, direct_y)
            best_cost = float('inf')

            for _ in range(5):
                # Add random deviation
                dev_x = np.random.uniform(-max_deviation, max_deviation)
                dev_y = np.random.uniform(-max_deviation, max_deviation)

                test_x = int(direct_x + dev_x)
                test_y = int(direct_y + dev_y)

                # Check bounds
                if not (0 <= test_x < self.map_system.layers["terrain"].width and
                        0 <= test_y < self.map_system.layers["terrain"].height):
                    continue

                # Calculate cost based on terrain
                terrain_data = terrain_layer.get_data_at(test_x, test_y)
                if not terrain_data or not terrain_data["is_land"]:
                    # Avoid water
                    continue

                # Prefer easier terrain
                terrain_cost = 1.0
                if terrain_data["terrain_type"] == "plains":
                    terrain_cost = 0.8
                elif terrain_data["terrain_type"] == "hills":
                    terrain_cost = 1.2
                elif terrain_data["terrain_type"] == "mountains":
                    terrain_cost = 2.0

                # Calculate total cost
                cost = terrain_cost * (abs(dev_x) + abs(dev_y))

                if cost < best_cost:
                    best_cost = cost
                    best_point = (test_x, test_y)

            waypoints.append(best_point)

        waypoints.append((end_x, end_y))
        return waypoints

    def _plan_journey_with_rests(self, path):
        """Plan the journey with appropriate rest periods based on realistic travel pace"""
        if not path:
            return []

        # Create journey segments
        journey_segments = []

        # Start at the beginning
        current_idx = 0
        current_point = path[current_idx]

        # Track total distance traveled in miles
        total_miles_traveled = 0

        # For each time period
        for day in range(self.num_days):
            for time_of_day in range(4):  # morning, midday, evening, night
                is_night = (time_of_day == 3)

                if is_night:
                    # Rest at night - stay at the same location
                    journey_segments.append({
                        "position": current_point,
                        "resting": True,
                        "miles_traveled": 0  # No travel during rest
                    })
                else:
                    # Travel during the day based on terrain and roads
                    # Calculate how far we can travel in this 6-hour period
                    miles_this_segment = self._calculate_travel_distance(current_point, time_of_day)

                    # Convert miles to map units
                    # We'll use a scale where 1 pixel = 0.5 miles
                    map_units_this_segment = miles_this_segment * 2

                    # Find the furthest point we can reach
                    traveled_distance = 0
                    while current_idx < len(path) - 1 and traveled_distance < map_units_this_segment:
                        x1, y1 = current_point
                        x2, y2 = path[current_idx + 1]
                        segment_distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

                        if traveled_distance + segment_distance <= map_units_this_segment:
                            # We can reach the next point
                            current_idx += 1
                            current_point = path[current_idx]
                            traveled_distance += segment_distance
                        else:
                            # We can only go part way - interpolate
                            fraction = (map_units_this_segment - traveled_distance) / segment_distance
                            new_x = int(x1 + fraction * (x2 - x1))
                            new_y = int(y1 + fraction * (y2 - y1))
                            current_point = (new_x, new_y)
                            traveled_distance = map_units_this_segment

                    # Calculate actual miles traveled (may be less than miles_this_segment if we reached destination)
                    actual_miles = traveled_distance / 2
                    total_miles_traveled += actual_miles

                    # Add this travel segment
                    journey_segments.append({
                        "position": current_point,
                        "resting": False,
                        "miles_traveled": actual_miles,
                        "total_miles": total_miles_traveled
                    })

                # Check if we've reached the destination
                if current_point == path[-1]:
                    # We've arrived! Add a final rest segment if it's not night
                    if not is_night:
                        journey_segments.append({
                            "position": current_point,
                            "resting": True,
                            "miles_traveled": 0
                        })
                    break

            # Check if we've reached the destination
            if current_point == path[-1]:
                break

        return journey_segments

    def _calculate_travel_distance(self, position, time_of_day):
        """Calculate how many miles can be traveled from this position in a 6-hour period"""
        x, y = position

        # Get terrain and road information
        terrain_type = "clear"  # Default
        on_road = False
        road_type = None

        # Check terrain
        terrain_data = self.map_system.layers["terrain"].get_data_at(x, y)
        if terrain_data:
            if terrain_data["terrain_type"] in ["plains", "beach"]:
                terrain_type = "clear"
            elif terrain_data["terrain_type"] in ["hills", "forest"]:
                terrain_type = "difficult"
            elif terrain_data["terrain_type"] in ["mountains", "snow_peaks", "swamp"]:
                terrain_type = "very_difficult"

        # Check if on a road
        if "settlements" in self.map_system.layers:
            settlements_layer = self.map_system.layers["settlements"]

            # Check roads
            for road in settlements_layer.roads:
                for rx, ry in road["points"]:
                    if abs(x - rx) <= 2 and abs(y - ry) <= 2:
                        on_road = True
                        road_type = road["type"]
                        break
                if on_road:
                    break

        # Determine base travel pace
        if on_road:
            # On a road - use road pace
            base_pace = TRAVEL_PACE["road"]
            # Adjust for road quality
            if road_type == "major":
                base_pace *= 1.1  # 10% faster on major roads
            elif road_type == "minor":
                base_pace *= 0.9  # 10% slower on minor roads
        else:
            # Not on a road - use terrain pace
            base_pace = TRAVEL_PACE[terrain_type]

        # Adjust for time of day
        if time_of_day == 0:  # morning
            time_modifier = 1.0  # Normal travel
        elif time_of_day == 1:  # midday
            time_modifier = 1.1  # Slightly faster in good light
        else:  # evening
            time_modifier = 0.8  # Slower as light fades

        # Check weather effects
        weather_data = self.weather_system.get_weather_at(x, y, self.current_day)
        weather_modifier = 1.0

        # Precipitation slows travel
        if weather_data["precipitation"]["type"] != "none":
            intensity = weather_data["precipitation"]["intensity"]
            if intensity == "light":
                weather_modifier *= 0.9  # 10% slower in light rain/snow
            elif intensity == "moderate":
                weather_modifier *= 0.7  # 30% slower in moderate rain/snow
            else:  # heavy
                weather_modifier *= 0.5  # 50% slower in heavy rain/snow

        # Strong winds slow travel
        if weather_data["wind"]["speed"] in ["strong", "gale"]:
            weather_modifier *= 0.8  # 20% slower in strong winds

        # Calculate final travel distance
        travel_distance = base_pace * time_modifier * weather_modifier

        return travel_distance

    def _calculate_path(self):
        """Calculate a path between start and end points"""
        # This is a simplified A* pathfinding implementation
        import heapq

        # Define movement costs based on terrain
        def get_movement_cost(x, y):
            data = self.map_system.query_at_point(x, y)

            # Default high cost for impassable terrain
            cost = 1000

            if "terrain" in data and data["terrain"]:
                terrain_data = data["terrain"]

                if not terrain_data["is_land"]:
                    return cost  # Can't walk on water

                # Land movement costs
                if terrain_data["terrain_type"] == "beach":
                    cost = 1.2
                elif terrain_data["terrain_type"] == "plains":
                    cost = 1.0  # Easiest terrain
                elif terrain_data["terrain_type"] == "hills":
                    cost = 2.0
                elif terrain_data["terrain_type"] == "mountains":
                    cost = 5.0
                elif terrain_data["terrain_type"] == "snow_peaks":
                    cost = 8.0

            # Rivers affect movement
            if "rivers" in data and data["rivers"]:
                river_data = data["rivers"]
                if river_data["has_river"]:
                    cost += river_data["river_size"] * 2  # Harder to cross bigger rivers

            return cost

        # A* implementation
        start_x, start_y = self.start_point
        end_x, end_y = self.end_point

        open_set = [(0, start_x, start_y)]  # (f_score, x, y)
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): np.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)}

        while open_set:
            _, current_x, current_y = heapq.heappop(open_set)

            # Check if we reached the destination
            if current_x == end_x and current_y == end_y:
                # Reconstruct path
                path = [(current_x, current_y)]
                while (current_x, current_y) in came_from:
                    current_x, current_y = came_from[(current_x, current_y)]
                    path.append((current_x, current_y))
                path.reverse()
                return path

            # Check neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    neighbor_x, neighbor_y = current_x + dx, current_y + dy

                    # Check bounds
                    width = self.map_system.layers["terrain"].width
                    height = self.map_system.layers["terrain"].height
                    if not (0 <= neighbor_x < width and 0 <= neighbor_y < height):
                        continue

                    # Calculate movement cost
                    movement_cost = get_movement_cost(neighbor_x, neighbor_y)
                    if movement_cost >= 1000:  # Impassable
                        continue

                    # Diagonal movement costs more
                    if dx != 0 and dy != 0:
                        movement_cost *= 1.414  # sqrt(2)

                    # Calculate scores
                    tentative_g = g_score[(current_x, current_y)] + movement_cost

                    if (neighbor_x, neighbor_y) not in g_score or tentative_g < g_score[(neighbor_x, neighbor_y)]:
                        # This path is better
                        came_from[(neighbor_x, neighbor_y)] = (current_x, current_y)
                        g_score[(neighbor_x, neighbor_y)] = tentative_g
                        f_score[(neighbor_x, neighbor_y)] = tentative_g + np.sqrt((end_x - neighbor_x)**2 + (end_y - neighbor_y)**2)
                        heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], neighbor_x, neighbor_y))

        # No path found
        return None

    def _divide_path(self, path, num_segments):
        """Divide a path into a specified number of segments"""
        if len(path) <= num_segments:
            return path  # Path already has fewer points than requested segments

        # Calculate points to include
        step = (len(path) - 1) / num_segments
        indices = [int(round(i * step)) for i in range(num_segments)]

        # Make sure the end point is included
        if indices[-1] != len(path) - 1:
            indices[-1] = len(path) - 1

        # Return the selected points
        return [path[i] for i in indices]

    def _generate_turn_description(self, turn_number, position, is_resting=False):
        """Generate a rich description for a turn in the journey"""
        x, y = position

        # Get map data at this position
        map_data = self.map_system.query_at_point(x, y)

        # Get weather data
        weather_data = self.weather_system.get_weather_at(x, y, self.current_day)

        # Build description
        description = f"Day {self.current_day + 1}, {self.times_of_day[self.current_time_of_day].capitalize()}: "

        # Temperature for this time of day
        temperature = int(weather_data["temperature"][self.times_of_day[self.current_time_of_day]])

        # Start with time and weather
        description += f"The temperature is {temperature}°F. "

        # Add weather conditions
        if weather_data["cloud_cover"] < 20:
            description += "The sky is clear and blue. "
        elif weather_data["cloud_cover"] < 50:
            description += "There are scattered clouds in the sky. "
        else:
            description += "The sky is overcast with thick clouds. "

        # Add precipitation if any
        if weather_data["precipitation"]["type"] != "none":
            precip_type = weather_data["precipitation"]["type"]
            intensity = weather_data["precipitation"]["intensity"]

            if precip_type == "rain":
                if intensity == "light":
                    description += "A light drizzle is falling. "
                elif intensity == "moderate":
                    description += "It's raining steadily. "
                else:
                    description += "Heavy rain is pouring down. "
            elif precip_type == "snow":
                if intensity == "light":
                    description += "Light snowflakes are drifting down. "
                elif intensity == "moderate":
                    description += "It's snowing steadily. "
                else:
                    description += "Heavy snow is falling. "
            elif precip_type == "sleet":
                description += "Sleet is falling, a mix of rain and ice. "
            elif precip_type == "freezing_rain":
                description += "Freezing rain is coating everything in a layer of ice. "

        # Add wind
        wind_speed = weather_data["wind"]["speed"]
        wind_direction = weather_data["wind"]["direction"]

        if wind_speed != "calm":
            description += f"A {wind_speed} wind is blowing from the {wind_direction}. "

        # Handle resting vs. traveling
        if is_resting:
            description += "You are resting for the night. "
        else:
            description += "You are traveling. "

        # Describe terrain
        if "terrain" in map_data and map_data["terrain"]:
            terrain_type = map_data["terrain"]["terrain_type"]

            if terrain_type == "plains":
                if is_resting:
                    description += "You've made camp in the open grasslands. "
                else:
                    description += "Your path takes you across open grasslands. "

                # Add more details about plains
                plains_details = [
                    "Tall grasses sway in the breeze around you.",
                    "Wildflowers dot the landscape with splashes of color.",
                    "The relatively flat terrain allows you to see for miles in all directions.",
                    "A few scattered trees provide occasional shade.",
                    "Small animals scurry through the grass as you approach."
                ]
                description += np.random.choice(plains_details) + " "

            elif terrain_type == "hills":
                if is_resting:
                    description += "You've found a sheltered spot among the rolling hills to rest. "
                else:
                    description += "You're making your way through rolling hills. "

                # Add more details about hills
                hills_details = [
                    "The undulating landscape provides constantly changing views.",
                    "From each hilltop, you can see your path winding ahead.",
                    "Small copses of trees grow in the valleys between hills.",
                    "The terrain requires more effort to traverse, but offers better vantage points.",
                    "Rocky outcroppings occasionally break through the grassy slopes."
                ]
                description += np.random.choice(hills_details) + " "

            elif terrain_type == "mountains":
                if is_resting:
                    description += "You've found a protected alcove in the mountain terrain for the night. "
                else:
                    description += "You're traversing rugged mountain terrain. "

                # Add more details about mountains
                mountain_details = [
                    "The path narrows as it winds between towering rock faces.",
                    "Loose scree makes footing treacherous in places.",
                    "The air grows thinner as you climb higher.",
                    "Mountain goats watch curiously from higher ledges.",
                    "The views are breathtaking, with distant peaks visible on the horizon."
                ]
                description += np.random.choice(mountain_details) + " "

            elif terrain_type == "beach":
                if is_resting:
                    description += "You've made camp on the sandy beach for the night. "
                else:
                    description += "You're walking along a sandy beach. "

                # Add more details about beach
                beach_details = [
                    "Waves lap gently at the shore beside your path.",
                    "Seabirds circle overhead, occasionally diving for fish.",
                    "The sand shifts under your feet, making progress slightly slower.",
                    "Shells and interesting stones are scattered along the shoreline.",
                    "The salty breeze carries the distinctive smell of the ocean."
                ]
                description += np.random.choice(beach_details) + " "

            elif terrain_type == "snow_peaks":
                if is_resting:
                    description += "You've carved out a snow shelter in the high mountains. "
                else:
                    description += "You're carefully picking your way through snow-capped peaks. "

                # Add more details about snow peaks
                snow_details = [
                    "The air is bitingly cold at this altitude.",
                    "Your breath forms clouds in the frigid air.",
                    "The snow crunches underfoot with each careful step.",
                    "The pristine white landscape stretches out in all directions.",
                    "Occasional ice formations glitter in what sunlight penetrates the clouds."
                ]
                description += np.random.choice(snow_details) + " "

            elif "water" in terrain_type:
                if is_resting:
                    description += "You've anchored your boat for the night. "
                else:
                    description += "You're traveling by boat across water. "

                # Add more details about water
                water_details = [
                    "The water is relatively calm, making for smooth passage.",
                    "Small waves rock your vessel as you make your way forward.",
                    "Fish occasionally break the surface of the water around you.",
                    "The depth of the water beneath you is impossible to gauge.",
                    "Water slaps rhythmically against the sides of your craft."
                ]
                description += np.random.choice(water_details) + " "

        # Mention rivers if present
        if "rivers" in map_data and map_data["rivers"] and map_data["rivers"]["has_river"]:
            river_size = map_data["rivers"]["river_size"]
            if river_size > 3:
                if is_resting:
                    description += "You've made camp near a wide river. The sound of flowing water provides a soothing backdrop. "
                else:
                    description += "A wide river flows nearby. You'll need to find a bridge or ford to cross it. "
            else:
                if is_resting:
                    description += "A small stream trickles nearby, providing fresh water for your camp. "
                else:
                    description += "A small stream crosses your path. It's shallow enough to step across easily. "

        # Check for nearby roads
        on_road = False
        road_type = None

        if "settlements" in self.map_system.layers:
            settlements_layer = self.map_system.layers["settlements"]

            # Check if we're on a road
            for road in settlements_layer.roads:
                for rx, ry in road["points"]:
                    if abs(x - rx) <= 2 and abs(y - ry) <= 2:
                        on_road = True
                        road_type = road["type"]
                        break
                if on_road:
                    break

            # If not on a road, check if we're on a path
            if not on_road:
                for path in settlements_layer.paths:
                    for px, py in path["points"]:
                        if abs(x - px) <= 2 and abs(y - py) <= 2:
                            on_road = True
                            road_type = "path"
                            break
                    if on_road:
                        break

        # Describe the road if we're on one
        if on_road:
            if road_type == "major":
                if is_resting:
                    description += "You've set up camp just off a major road. Occasional travelers pass by. "
                else:
                    description += "You're following a well-maintained major road. The smooth surface makes travel easier. "
            elif road_type == "medium":
                if is_resting:
                    description += "You're resting beside a decent road. It's quieter here than on the main highways. "
                else:
                    description += "You're traveling along a medium-sized road. It's well-used but not as busy as a major highway. "
            elif road_type == "minor":
                if is_resting:
                    description += "You've made camp near a small country road. It's peaceful and quiet. "
                else:
                    description += "You're following a minor road. It's not in the best condition, but better than no road at all. "
            elif road_type == "path":
                if is_resting:
                    description += "You've set up camp beside a simple dirt path. Few travelers come this way. "
                else:
                    description += "You're following a narrow dirt path. It winds through the terrain, clearly made by frequent foot traffic. "

        # Mention settlements if present
        settlement = None
        for s in self.map_system.layers["settlements"].settlements:
            if abs(s["x"] - x) <= 5 and abs(s["y"] - y) <= 5:
                settlement = s
                break

        if settlement:
            if settlement["type"] == "city":
                if is_resting:
                    description += f"You're spending the night in the city of {settlement['name']}. "
                    description += "You've found lodging at a comfortable inn, with a warm meal and soft bed. "
                else:
                    description += f"You've reached the city of {settlement['name']}. "

                if settlement["is_capital"]:
                    description += "This is a capital city, with impressive buildings and bustling streets. "
                    description += "Guards patrol the walls, and merchants from distant lands hawk exotic wares. "
                else:
                    description += "The city is busy with people and commerce. "
                    description += "The streets are lined with shops, homes, and various establishments. "

            elif settlement["type"] == "town":
                if is_resting:
                    description += f"You're resting at an inn in the town of {settlement['name']}. "
                    description += "The local food is hearty, and the innkeeper shares gossip about the region. "
                else:
                    description += f"You've arrived at the town of {settlement['name']}. "

                description += "The town has several inns and shops where travelers can rest and resupply. "
                description += "Locals go about their business, occasionally glancing at travelers passing through. "

            else:  # village
                if is_resting:
                    description += f"You're spending the night in the small village of {settlement['name']}. "
                    description += "With no proper inn, a local family has offered you shelter in their barn. "
                else:
                    description += f"You've come to the small village of {settlement['name']}. "

                description += "The village is a simple collection of homes and farms. "
                description += "Chickens scatter as you pass, and curious children peek out from doorways. "

        # Look for nearby settlements if we're not in one
        if not settlement:
            nearby_settlements = []
            for s in self.map_system.layers["settlements"].settlements:
                dist = np.sqrt((s["x"] - x)**2 + (s["y"] - y)**2)
                if 5 < dist < 30:  # Close enough to see but not right there
                    nearby_settlements.append((s, dist))

            if nearby_settlements:
                # Sort by distance
                nearby_settlements.sort(key=lambda x: x[1])
                nearest = nearby_settlements[0][0]

                # Determine direction
                dx = nearest["x"] - x
                dy = nearest["y"] - y

                # Convert to compass direction
                angle = np.arctan2(dy, dx) * 180 / np.pi
                if angle < 0:
                    angle += 360

                directions = ["east", "northeast", "north", "northwest",
                             "west", "southwest", "south", "southeast"]
                direction_idx = int((angle + 22.5) / 45) % 8
                direction = directions[direction_idx]

                if nearest["type"] == "city":
                    description += f"In the distance to the {direction}, you can see the walls and towers of {nearest['name']}. "
                elif nearest["type"] == "town":
                    description += f"To the {direction}, you can make out the buildings of the town of {nearest['name']}. "
                else:
                    description += f"You can see smoke from cooking fires rising from the village of {nearest['name']} to the {direction}. "

        # Add some flavor based on time of day and weather
        if self.current_time_of_day == 0:  # morning
            if is_resting:
                description += "You're breaking camp as the sun rises. "
            elif "clear" in weather_data["description_tags"]:
                description += "The morning sun casts long shadows as you continue your journey. "
            elif "overcast" in weather_data["description_tags"]:
                description += "The gloomy morning light makes it difficult to see far ahead. "

        elif self.current_time_of_day == 1:  # midday
            if is_resting:
                description += "You've stopped for a brief midday meal before continuing. "
            elif temperature > 80:
                description += "The midday heat is making travel uncomfortable. You frequently stop in shaded areas for brief rests. "
            elif "clear" in weather_data["description_tags"]:
                description += "The sun is high in the sky, illuminating the landscape in all directions. "

        elif self.current_time_of_day == 2:  # evening
            if is_resting:
                description += "You're setting up camp as the light fades. "
            else:
                description += "The light is fading as evening approaches. You'll need to find a place to rest soon. "

            if "clear" in weather_data["description_tags"]:
                description += "The sunset paints the sky in brilliant colors. "

        else:  # night
            if is_resting:
                description += "You're settled in for the night, with a small campfire providing warmth and light. "

                if "clear" in weather_data["description_tags"]:
                    description += "The stars shine brightly overhead as you rest. "
                else:
                    description += "The night is dark with no stars visible through the clouds. "

            else:
                description += "You're traveling under the cover of darkness, which is slow and potentially dangerous. "

                if "clear" in weather_data["description_tags"]:
                    description += "At least the stars provide some light to see by. "
                else:
                    description += "The darkness is nearly complete, forcing you to move with extreme caution. "

        # Add a note about progress
        if position != self.end_point:
            if is_resting:
                description += "Tomorrow you'll continue your journey toward your destination. "
            else:
                description += "You press on toward your destination. "
        else:
            if is_resting:
                description += "You've reached your destination and can finally rest properly! "
            else:
                description += "You have reached your destination! "

        return description


def create_test_map_and_simulate_journey():
    """Create a test map and simulate a journey with weather"""
    # Create map system with a random seed for variety
    map_seed = random.randint(1, 100000)
    print(f"Generating map with seed: {map_seed}")

    # Store the seed for display in the legend
    global current_map_seed
    current_map_seed = map_seed

    map_system = MapSystem(base_seed=map_seed)

    # Map dimensions
    width, height = 512, 512

    # Add terrain layer with improved parameters for more natural-looking landscapes
    map_system.add_layer(
        "terrain",
        "terrain",
        seed_modifier=0,
        parameters={
            "width": width,
            "height": height,
            "scale": 200.0,  # Larger scale for more gradual terrain changes
            "octaves": 8,    # More octaves for more detail at different scales
            "persistence": 0.55,  # Higher persistence for more natural variation
            "lacunarity": 2.0,    # Adjusted lacunarity for better terrain flow
            "sea_level": -0.15,   # Adjusted sea level for better land/water ratio
            "mountain_level": 0.4, # Level at which mountains start
            "snow_level": 0.7,    # Level at which snow-capped peaks start
            "beach_width": 0.05,  # Width of beaches around water
            "smooth_iterations": 2 # Apply smoothing to terrain transitions
        }
    )

    # Add rivers layer with improved parameters for more natural-looking rivers
    map_system.add_layer(
        "rivers",
        "rivers",
        seed_modifier=500,
        parameters={
            "width": width,
            "height": height,
            "num_rivers": 20,           # More rivers for a richer landscape
            "min_length": 50,           # Minimum river length
            "max_length": 300,          # Maximum river length
            "meander_factor": 0.4,      # How much rivers meander (higher = more winding)
            "branch_probability": 0.15, # Probability of river branching
            "flow_strength": 0.8,       # How strongly rivers follow terrain gradient
            "min_river_width": 1,       # Minimum width of rivers
            "max_river_width": 5        # Maximum width of rivers (for major rivers)
        }
    )

    # Add political layer
    map_system.add_layer(
        "kingdoms",
        "political",
        seed_modifier=1000,
        parameters={
            "width": width,
            "height": height,
            "num_territories": 6,
            "territory_names": [
                "Eldoria", "Westmark", "Sunhaven",
                "Frostpeak", "Greendale", "Shadowvale"
            ]
        }
    )

    # Generate these layers
    map_system.generate_all_layers()

    # Add settlements layer
    settlements_layer = SettlementsLayer(
        map_seed + 1500,
        parameters={
            "width": width,
            "height": height,
            "num_cities": 6,
            "num_towns": 12,
            "num_villages": 24
        }
    )

    # Generate settlements using the other layers
    settlements_layer.generate(
        terrain_layer=map_system.layers["terrain"],
        rivers_layer=map_system.layers["rivers"],
        political_layer=map_system.layers["kingdoms"]
    )

    # Add to map system
    map_system.layers["settlements"] = settlements_layer

    # Create weather system
    weather_system = WeatherSystem(
        map_seed + 2000,
        map_system,
        parameters={
            "start_date": datetime(1482, 3, 21),  # Spring equinox
            "days_generated": 30
        }
    )

    # Generate weather
    weather_system.generate()

    # Find suitable start and end points for journey
    # Look for settlements that are reasonably far apart
    settlements = settlements_layer.settlements
    cities = [s for s in settlements if s["type"] == "city"]
    towns = [s for s in settlements if s["type"] == "town"]

    # Try to find two cities that are reasonably far apart but not too far
    start_point = None
    end_point = None

    # First try cities
    if len(cities) >= 2:
        # Find two cities that are reasonably far apart
        min_distance = 150  # Minimum distance to ensure an interesting journey
        max_distance = 400  # Maximum distance to ensure pathfinding works

        for i, city1 in enumerate(cities):
            for city2 in cities[i+1:]:
                distance = np.sqrt((city1["x"] - city2["x"])**2 + (city1["y"] - city2["y"])**2)
                if min_distance <= distance <= max_distance:
                    start_point = (city1["x"], city1["y"])
                    end_point = (city2["x"], city2["y"])
                    break
            if start_point and end_point:
                break

    # If we couldn't find suitable cities, try towns
    if not (start_point and end_point) and len(towns) >= 2:
        min_distance = 150
        max_distance = 400

        for i, town1 in enumerate(towns):
            for town2 in towns[i+1:]:
                distance = np.sqrt((town1["x"] - town2["x"])**2 + (town1["y"] - town2["y"])**2)
                if min_distance <= distance <= max_distance:
                    start_point = (town1["x"], town1["y"])
                    end_point = (town2["x"], town2["y"])
                    break
            if start_point and end_point:
                break

    # If we still don't have points, try a city and a town
    if not (start_point and end_point) and cities and towns:
        min_distance = 150
        max_distance = 400

        for city in cities:
            for town in towns:
                distance = np.sqrt((city["x"] - town["x"])**2 + (city["y"] - town["y"])**2)
                if min_distance <= distance <= max_distance:
                    start_point = (city["x"], city["y"])
                    end_point = (town["x"], town["y"])
                    break
            if start_point and end_point:
                break

    # If all else fails, use default points
    if not (start_point and end_point):
        # Use points that are likely to be on land
        start_point = (width // 4, height // 4)
        end_point = (width * 3 // 4, height * 3 // 4)

        print(f"Using default journey points: {start_point} to {end_point}")

    # Create journey simulator
    journey_simulator = JourneySimulator(
        map_system,
        weather_system,
        start_point,
        end_point,
        num_days=3  # 3 days = 12 turns (4 per day)
    )

    # Simulate journey
    journey_log = journey_simulator.simulate_journey()

    # Check if journey_log is a string (error message) or a list of entries
    if isinstance(journey_log, str):
        print(f"Journey simulation error: {journey_log}")
        # Return empty journey log to avoid visualization errors
        return []

    # Visualize the map with journey path
    visualize_map_with_journey(map_system, journey_log, start_point, end_point)

    return journey_log


def visualize_map_with_journey(map_system, journey_log, start_point, end_point):
    """Create a visualization of the map with the journey path using separate layers"""
    # Get dimensions of the map
    map_width = map_system.layers["terrain"].width
    map_height = map_system.layers["terrain"].height

    # Create a larger canvas to accommodate legend and compass without overlapping the map
    # Add 250 pixels to the right for legend
    canvas_width = map_width + 250
    # Keep the same height but ensure there's room at the bottom for scale
    canvas_height = map_height + 50

    # Create a single RGB image for simplicity and compatibility
    # We'll still organize our drawing logically but use a single image
    map_img = Image.new('RGB', (map_width, map_height), (255, 255, 255))
    draw = ImageDraw.Draw(map_img)

    # Create a base image from terrain
    terrain_layer = map_system.layers["terrain"]

    # Create RGB array for the terrain portion of the image
    rgb_data = np.zeros((map_height, map_width, 3), dtype=np.uint8)

    # Apply a slight blur effect to make the terrain look smoother
    # First, create a temporary array for the terrain colors
    terrain_colors = np.zeros((map_height, map_width, 3), dtype=np.float32)

    # Color the terrain
    for y in range(map_height):
        for x in range(map_width):
            terrain_data = terrain_layer.get_data_at(x, y)

            # Get terrain data
            elevation = terrain_data.get("elevation", 0)
            moisture = terrain_data.get("moisture", 0.5)
            is_land = terrain_data.get("is_land", True)
            terrain_type = terrain_data.get("terrain_type", "plains")

            # Add some noise to elevation and moisture for more natural variation
            noise_factor = 0.05
            elevation_noise = elevation + (np.random.random() - 0.5) * noise_factor
            moisture_noise = moisture + (np.random.random() - 0.5) * noise_factor

            # Improved terrain coloring with more natural transitions
            if not is_land:
                # Water with depth variation
                depth = 1.0 - max(0, min(1, (elevation + 0.2) / 0.2))
                blue = int(145 + 110 * depth)  # Deeper water is darker blue
                green = int(165 + 40 * depth)
                terrain_colors[y, x] = [65, min(green, 205), min(blue, 255)]
            elif terrain_type == "snow_peaks" or elevation > 0.75:
                # Snow-capped peaks - white with slight blue tint
                # Add slight variation for texture
                white_var = int(240 + (np.random.random() - 0.5) * 15)
                blue_var = int(250 + (np.random.random() - 0.5) * 10)
                terrain_colors[y, x] = [white_var, white_var, blue_var]
            elif terrain_type == "mountains" or elevation > 0.6:
                # Mountains - gray with slight variation based on moisture
                gray_base = 110 + 40 * moisture_noise
                # Add variation between pixels for texture
                r = int(gray_base + (np.random.random() - 0.5) * 15)
                g = int(gray_base + (np.random.random() - 0.5) * 10)
                b = int(gray_base + 10 + (np.random.random() - 0.5) * 10)
                terrain_colors[y, x] = [r, g, b]
            elif terrain_type == "hills" or elevation > 0.45:
                # Hills - blend between mountains and plains based on elevation
                blend = (elevation_noise - 0.45) / 0.15  # 0 at 0.45, 1 at 0.6
                # Drier hills are more brown, wetter hills more green
                if moisture_noise < 0.4:
                    # Dry hills - brown/tan
                    r = int(160 - 20 * blend + (np.random.random() - 0.5) * 15)
                    g = int(126 - 30 * blend + (np.random.random() - 0.5) * 10)
                    b = int(84 - 20 * blend + (np.random.random() - 0.5) * 10)
                    terrain_colors[y, x] = [r, g, b]
                else:
                    # Wet hills - green with brown
                    r = int(120 - 40 * moisture_noise + (np.random.random() - 0.5) * 15)
                    g = int(140 - 20 * blend + (np.random.random() - 0.5) * 10)
                    b = int(80 - 30 * blend + (np.random.random() - 0.5) * 10)
                    terrain_colors[y, x] = [r, g, b]
            elif terrain_type == "plains" or elevation > 0.25:
                # Plains/grasslands - green with variation based on moisture
                if moisture_noise > 0.6:
                    # Wet plains/forest - darker green
                    r = int(34 - 10 * (moisture_noise - 0.6) / 0.4 + (np.random.random() - 0.5) * 10)
                    g = int(139 - 30 * (moisture_noise - 0.6) / 0.4 + (np.random.random() - 0.5) * 15)
                    b = int(34 - 10 * (moisture_noise - 0.6) / 0.4 + (np.random.random() - 0.5) * 10)
                    terrain_colors[y, x] = [r, g, b]
                elif moisture_noise > 0.3:
                    # Normal plains - medium green
                    r = int(34 + 20 * (0.6 - moisture_noise) / 0.3 + (np.random.random() - 0.5) * 10)
                    g = int(139 - 20 * (0.6 - moisture_noise) / 0.3 + (np.random.random() - 0.5) * 15)
                    b = int(34 + 10 * (0.6 - moisture_noise) / 0.3 + (np.random.random() - 0.5) * 10)
                    terrain_colors[y, x] = [r, g, b]
                else:
                    # Dry plains/savanna - yellow-green
                    r = int(150 - 30 * moisture_noise / 0.3 + (np.random.random() - 0.5) * 15)
                    g = int(180 - 20 * moisture_noise / 0.3 + (np.random.random() - 0.5) * 15)
                    b = int(60 + 20 * moisture_noise / 0.3 + (np.random.random() - 0.5) * 10)
                    terrain_colors[y, x] = [r, g, b]
            elif terrain_type == "beach" or elevation > 0.05:
                # Beach/coast - sandy color with slight variation
                r = int(210 + 20 * moisture_noise + (np.random.random() - 0.5) * 15)
                g = int(180 + 10 * moisture_noise + (np.random.random() - 0.5) * 10)
                b = int(140 - 20 * moisture_noise + (np.random.random() - 0.5) * 10)
                terrain_colors[y, x] = [min(r, 255), min(g, 255), b]
            else:
                # Shallow water / swamp - murky blue-green
                r = int(100 + 30 * moisture_noise + (np.random.random() - 0.5) * 10)
                g = int(130 + 20 * moisture_noise + (np.random.random() - 0.5) * 15)
                b = int(130 + 40 * moisture_noise + (np.random.random() - 0.5) * 15)
                terrain_colors[y, x] = [r, g, b]

    # Apply a simple blur to smooth the terrain
    # This is a very basic blur - just averaging with neighbors
    for y in range(1, map_height-1):
        for x in range(1, map_width-1):
            # Average with 8 surrounding pixels
            neighbors = [
                terrain_colors[y-1, x-1], terrain_colors[y-1, x], terrain_colors[y-1, x+1],
                terrain_colors[y, x-1], terrain_colors[y, x+1],
                terrain_colors[y+1, x-1], terrain_colors[y+1, x], terrain_colors[y+1, x+1]
            ]

            # Add the center pixel with higher weight
            center = terrain_colors[y, x]

            # Calculate weighted average (center has weight 2, neighbors have weight 1)
            avg = (center * 2 + sum(neighbors)) / 10

            # Store in the final RGB data
            rgb_data[y, x] = avg.astype(np.uint8)

    # Convert the terrain array to an image
    base_terrain_img = Image.fromarray(rgb_data)
    map_img = base_terrain_img.copy()

    # Try to load fonts
    try:
        font = ImageFont.truetype("arial.ttf", 10)
        title_font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except IOError:
            font = ImageFont.load_default()
            title_font = font

    # Create the full canvas with white background
    img = Image.new('RGB', (canvas_width, canvas_height), color=(240, 240, 240))

    # Draw a border around the map area
    canvas_draw = ImageDraw.Draw(img)
    canvas_draw.rectangle([(0, 0), (map_width, map_height)], outline=(100, 100, 100), width=1)

    # Add a title for the legend section
    canvas_draw.text(
        (map_width + 75, 20),
        "Legend",
        fill=(0, 0, 0),
        font=title_font
    )

    # Draw rivers with improved appearance based on elevation
    if "rivers" in map_system.layers:
        rivers_layer = map_system.layers["rivers"]
        terrain_layer = map_system.layers["terrain"]

        # First pass - identify river pixels and their sizes, and get elevation data
        river_data_with_elevation = []
        for y in range(map_height):
            for x in range(map_width):
                river_data = rivers_layer.get_data_at(x, y)
                if river_data and river_data.get("has_river", False):
                    river_size = river_data.get("river_size", 1)
                    # Get elevation from terrain layer
                    terrain_data = terrain_layer.get_data_at(x, y)
                    elevation = terrain_data.get("elevation", 0) if terrain_data else 0
                    river_data_with_elevation.append((x, y, river_size, elevation))

        # Sort by elevation (highest first) to ensure rivers flow downhill
        river_data_with_elevation.sort(key=lambda p: p[3], reverse=True)

        # Draw rivers with a more natural appearance
        for x, y, river_size, elevation in river_data_with_elevation:
            # Base river color - blue with variation
            blue_intensity = min(255, 100 + river_size * 30)
            green_intensity = min(255, 80 + river_size * 20)

            # Draw the main river pixel
            map_img.putpixel((x, y), (65, green_intensity, blue_intensity))

            # For larger rivers, add some width based on elevation
            # Rivers should be wider at lower elevations
            effective_width = river_size + max(0, (1.0 - elevation/100) * 3)

            if effective_width > 1.5:
                # Check surrounding pixels and add river effect if they're not already rivers
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        # Check if this is already a river pixel
                        neighbor_data = rivers_layer.get_data_at(nx, ny)
                        if not (neighbor_data and neighbor_data.get("has_river", False)):
                            # Add a lighter blue "edge" to the river
                            edge_blue = min(255, blue_intensity - 20)
                            edge_green = min(255, green_intensity - 10)
                            # Add the edge pixel
                            map_img.putpixel((nx, ny), (65, edge_green, edge_blue))

            # Add some random variation for a more natural look
            if river_size > 1 and np.random.random() < 0.3:
                # Randomly add some "ripple" effects
                for _ in range(1):
                    dx = np.random.randint(-1, 2)
                    dy = np.random.randint(-1, 2)
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        # Add a slightly lighter blue pixel
                        ripple_blue = min(255, blue_intensity + 20)
                        ripple_green = min(255, green_intensity + 10)
                        map_img.putpixel((nx, ny), (65, ripple_green, ripple_blue))

    # Draw political boundaries with improved appearance
    if "kingdoms" in map_system.layers:
        political_layer = map_system.layers["kingdoms"]
        terrain_layer = map_system.layers["terrain"]

        # First identify all boundary pixels
        boundary_pixels = []
        territory_info = {}  # Store territory info for coloring water

        for y in range(1, map_height-1):
            for x in range(1, map_width-1):
                territory_data = political_layer.get_data_at(x, y)
                if not territory_data:
                    continue

                territory_id = territory_data.get("territory_id", -1)
                territory_name = territory_data.get("name", "Unknown")

                # Store territory info
                if territory_id not in territory_info:
                    # Generate a color for this territory
                    # Use a consistent color based on territory_id
                    r = (territory_id * 73) % 200 + 55  # Range 55-255
                    g = (territory_id * 47) % 200 + 55
                    b = (territory_id * 91) % 200 + 55
                    territory_info[territory_id] = {
                        "name": territory_name,
                        "color": (r, g, b),  # Territory fill color
                        "border_color": (139, 0, 0)  # Red border color
                    }

                # Check if any neighboring pixel has a different territory
                is_boundary = False
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < map_width and 0 <= ny < map_height:
                        neighbor_data = political_layer.get_data_at(nx, ny)
                        if not neighbor_data:
                            continue
                        neighbor_id = neighbor_data.get("territory_id", -2)
                        if neighbor_id != territory_id:
                            is_boundary = True
                            break

                if is_boundary:
                    # Store boundary pixel with territory info
                    boundary_pixels.append((x, y, territory_id, territory_name))

        # First, add a very subtle tint to each territory (land only)
        # This helps visualize territory extents
        for territory_id, info in territory_info.items():
            # For each pixel in this territory, add a very subtle tint
            for y in range(map_height):
                for x in range(map_width):
                    territory_data = political_layer.get_data_at(x, y)
                    if territory_data and territory_data.get("territory_id", -1) == territory_id:
                        # Get terrain data to check if it's water
                        terrain_data = terrain_layer.get_data_at(x, y)
                        is_water = terrain_data.get("is_water", False) if terrain_data else False

                        # Skip tinting water areas
                        if is_water:
                            continue

                        # Get current pixel color
                        current_color = map_img.getpixel((x, y))

                        # Add a very subtle tint (10% territory color, 90% original)
                        tint_factor = 0.1
                        r = int(current_color[0] * (1 - tint_factor) + info["color"][0] * tint_factor)
                        g = int(current_color[1] * (1 - tint_factor) + info["color"][1] * tint_factor)
                        b = int(current_color[2] * (1 - tint_factor) + info["color"][2] * tint_factor)

                        # Apply the tinted color
                        map_img.putpixel((x, y), (r, g, b))

        # Now draw the actual boundaries (land only)
        for x, y, territory_id, territory_name in boundary_pixels:
            # Get terrain data to check if it's water
            terrain_data = terrain_layer.get_data_at(x, y)
            is_water = terrain_data.get("is_water", False) if terrain_data else False

            # Skip drawing boundaries on water
            if is_water:
                continue

            # Get current pixel color
            current_color = map_img.getpixel((x, y))

            # Create a semi-transparent boundary effect
            # Blend dark red with the current terrain color
            blend_factor = 0.7  # 70% boundary color, 30% terrain
            r = int(139 * blend_factor + current_color[0] * (1 - blend_factor))
            g = int(0 * blend_factor + current_color[1] * (1 - blend_factor))
            b = int(0 * blend_factor + current_color[2] * (1 - blend_factor))

            # Apply the blended color
            map_img.putpixel((x, y), (r, g, b))

        # Add territory labels at the center of each territory
        territory_centers = {}
        territory_pixels = {}

        # Count pixels for each territory and track positions
        for y in range(map_height):
            for x in range(map_width):
                territory_data = political_layer.get_data_at(x, y)
                if not territory_data:
                    continue

                territory_id = territory_data.get("territory_id", -1)
                territory_name = territory_data.get("name", "Unknown")

                if territory_id not in territory_pixels:
                    territory_pixels[territory_id] = []
                    territory_centers[territory_id] = {"name": territory_name, "sum_x": 0, "sum_y": 0, "count": 0}

                territory_pixels[territory_id].append((x, y))
                territory_centers[territory_id]["sum_x"] += x
                territory_centers[territory_id]["sum_y"] += y
                territory_centers[territory_id]["count"] += 1

        # Calculate center of each territory
        for territory_id, data in territory_centers.items():
            if data["count"] > 0:
                center_x = data["sum_x"] // data["count"]
                center_y = data["sum_y"] // data["count"]

                # Draw territory name if territory is large enough
                if data["count"] > 500:  # Only label larger territories
                    # Create a semi-transparent background for the text
                    text = data["name"]
                    # Get text size - handle different PIL versions
                    try:
                        # For newer PIL versions (9.5.0+)
                        bbox = font.getbbox(text)
                        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    except AttributeError:
                        try:
                            # For older PIL versions
                            text_width, text_height = font.getsize(text)
                        except AttributeError:
                            # Fallback
                            text_width, text_height = 50, 10

                    # Draw a white background for the text
                    draw.rectangle(
                        [(center_x - text_width//2 - 5, center_y - text_height//2 - 5),
                         (center_x + text_width//2 + 5, center_y + text_height//2 + 5)],
                        fill=(255, 255, 255)
                    )

                    # Draw the territory name
                    draw.text(
                        (center_x - text_width//2, center_y - text_height//2),
                        text,
                        fill=(0, 0, 0),
                        font=font
                    )

    # Draw settlements and roads
    if "settlements" in map_system.layers:
        settlements_layer = map_system.layers["settlements"]

        # Draw roads and paths first (they go under settlements)
        # Draw paths first (they go under roads)
        for path in settlements_layer.paths:
            points = path["points"]
            # Convert list of points to flat list for PIL
            flat_points = []
            for x, y in points:
                flat_points.extend([x, y])

            # Draw path as dotted line
            if len(flat_points) >= 4:  # Need at least 2 points
                # Draw a slightly lighter path underneath for visibility
                draw.line(flat_points, fill=(210, 180, 140), width=2)  # Tan color

                # Draw dotted line on top
                for i in range(0, len(points) - 1, 2):  # Skip every other segment for dotted effect
                    if i + 1 < len(points):
                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]
                        draw.line((x1, y1, x2, y2), fill=(139, 69, 19), width=1)  # Brown

        # Draw roads by type
        road_styles = {
            "major": {"width": 3, "color": (120, 120, 120)},  # Gray
            "medium": {"width": 2, "color": (150, 150, 150)},  # Light gray
            "minor": {"width": 1, "color": (180, 180, 180)}   # Very light gray
        }

        for road in settlements_layer.roads:
            points = road["points"]
            road_type = road["type"]

            # Convert list of points to flat list for PIL
            flat_points = []
            for x, y in points:
                flat_points.extend([x, y])

            # Draw road
            if len(flat_points) >= 4:  # Need at least 2 points
                style = road_styles.get(road_type, road_styles["minor"])

                # Draw a slightly wider black line underneath for road borders
                draw.line(flat_points, fill=(50, 50, 50), width=style["width"] + 2)

                # Draw the actual road on top
                draw.line(flat_points, fill=style["color"], width=style["width"])

        # Draw settlements by type
        for settlement in settlements_layer.settlements:
            x, y = settlement["x"], settlement["y"]

            if settlement["type"] == "city":
                # Draw a large square for cities
                draw.rectangle((x-5, y-5, x+5, y+5), fill=(255, 0, 0), outline=(0, 0, 0))

                # Add a star for capitals
                if settlement["is_capital"]:
                    points = []
                    for i in range(5):
                        # Outer points of the star
                        angle = np.pi/2 + i * 2*np.pi/5
                        points.append((x + 8 * np.cos(angle), y + 8 * np.sin(angle)))
                        # Inner points of the star
                        angle += np.pi/5
                        points.append((x + 4 * np.cos(angle), y + 4 * np.sin(angle)))
                    draw.polygon(points, fill=(255, 215, 0))  # Gold
            elif settlement["type"] == "town":
                # Draw a medium circle for towns
                draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 165, 0), outline=(0, 0, 0))
            else:  # village
                # Draw a small circle for villages
                draw.ellipse((x-2, y-2, x+2, y+2), fill=(255, 255, 0), outline=(0, 0, 0))

    # Draw journey path
    if journey_log:
        # Extract points from journey log
        path_points = [log_entry["position"] for log_entry in journey_log]

        # Draw lines connecting the points
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            draw.line((x1, y1, x2, y2), fill=(255, 0, 255), width=2)

        # Draw points along the path with different markers for each time of day
        for i, entry in enumerate(journey_log):
            x, y = entry["position"]
            time_of_day = entry.get("time_of_day", "morning")
            is_resting = entry.get("resting", False)

            # Base marker size
            marker_size = 6

            if is_resting:
                # Tent/camp symbol for resting (night)
                # Draw a triangle for tent
                draw.polygon([(x, y-marker_size), (x-marker_size, y+marker_size), (x+marker_size, y+marker_size)],
                            fill=(100, 100, 255), outline=(0, 0, 0))
                # Add a small line at the bottom for tent entrance
                draw.line((x-2, y+marker_size, x+2, y+marker_size), fill=(0, 0, 0), width=1)
            elif time_of_day == "morning":
                # Sun symbol for morning
                # Draw a circle for sun
                draw.ellipse((x-marker_size, y-marker_size, x+marker_size, y+marker_size),
                            fill=(255, 200, 0), outline=(0, 0, 0))
                # Add rays
                for angle in range(0, 360, 45):
                    rad = angle * 3.14159 / 180
                    x1 = x + int(marker_size * 1.2 * np.cos(rad))
                    y1 = y + int(marker_size * 1.2 * np.sin(rad))
                    x2 = x + int(marker_size * 1.8 * np.cos(rad))
                    y2 = y + int(marker_size * 1.8 * np.sin(rad))
                    draw.line((x1, y1, x2, y2), fill=(255, 200, 0), width=1)
            elif time_of_day == "midday":
                # Circle for midday
                draw.ellipse((x-marker_size, y-marker_size, x+marker_size, y+marker_size),
                            fill=(255, 255, 0), outline=(0, 0, 0))
            elif time_of_day == "evening":
                # Half-moon for evening
                draw.ellipse((x-marker_size, y-marker_size, x+marker_size, y+marker_size),
                            fill=(200, 200, 255), outline=(0, 0, 0))
                # Cover half to make a half-moon
                draw.rectangle((x, y-marker_size, x+marker_size, y+marker_size),
                            fill=(0, 0, 100), outline=None)
            else:
                # Default marker (should not happen with our current setup)
                draw.ellipse((x-marker_size, y-marker_size, x+marker_size, y+marker_size),
                            fill=(255, 0, 255), outline=(0, 0, 0))

            # Add number
            draw.text((x-2, y-4), str(i+1), fill=(0, 0, 0))

    # Paste the map onto the canvas
    img.paste(map_img, (0, 0))

    # Mark start and end points
    start_x, start_y = start_point
    end_x, end_y = end_point

    # Start point - green triangle
    draw.polygon([(start_x, start_y-8), (start_x-6, start_y+4), (start_x+6, start_y+4)],
                fill=(0, 255, 0), outline=(0, 0, 0))
    draw.text((start_x-15, start_y+10), "Start", fill=(0, 0, 0), font=font)

    # End point - red square
    draw.rectangle((end_x-6, end_y-6, end_x+6, end_y+6),
                  fill=(255, 0, 0), outline=(0, 0, 0))
    draw.text((end_x-10, end_y+10), "End", fill=(0, 0, 0), font=font)

    # Add a scale bar and coordinate grid
    draw = ImageDraw.Draw(img)

    # Define scale parameters
    scale_bar_length = 100  # pixels
    scale_distance = 50     # miles/km (whatever unit you prefer)
    scale_position = (map_width - 120, map_height - 30)

    # Draw scale bar
    draw.rectangle(
        [scale_position, (scale_position[0] + scale_bar_length, scale_position[1] + 10)],
        outline=(0, 0, 0),
        fill=(255, 255, 255)
    )

    # Add scale text
    draw.text(
        (scale_position[0] + scale_bar_length // 2 - 15, scale_position[1] - 15),
        f"{scale_distance} miles",
        fill=(0, 0, 0)
    )

    # Add coordinate grid (every 100 pixels)
    grid_spacing = 100
    grid_color = (100, 100, 100, 128)  # Semi-transparent gray

    # Try to find a font that works
    try:
        # Try to load a system font
        font = ImageFont.truetype("Arial", 10)
    except IOError:
        try:
            # Try a different font that might be available
            font = ImageFont.truetype("DejaVuSans", 10)
        except IOError:
            # Fall back to default font
            font = ImageFont.load_default()

    # Draw vertical grid lines
    for x in range(0, map_width, grid_spacing):
        # Draw a lighter, thinner line
        for i in range(x, x+1):
            if i < map_width:
                for y in range(0, map_height):
                    # Get current pixel color
                    r, g, b = img.getpixel((i, y))
                    # Blend with grid color (make it subtle)
                    r = int(r * 0.8 + grid_color[0] * 0.2)
                    g = int(g * 0.8 + grid_color[1] * 0.2)
                    b = int(b * 0.8 + grid_color[2] * 0.2)
                    img.putpixel((i, y), (r, g, b))

        # Add coordinate label at the bottom
        if x > 0:  # Skip the first line at x=0
            draw.text((x, map_height - 15), str(x), fill=(0, 0, 0), font=font)

    # Draw horizontal grid lines
    for y in range(0, map_height, grid_spacing):
        # Draw a lighter, thinner line
        for i in range(y, y+1):
            if i < map_height:
                for x in range(0, map_width):
                    # Get current pixel color
                    r, g, b = img.getpixel((x, i))
                    # Blend with grid color (make it subtle)
                    r = int(r * 0.8 + grid_color[0] * 0.2)
                    g = int(g * 0.8 + grid_color[1] * 0.2)
                    b = int(b * 0.8 + grid_color[2] * 0.2)
                    img.putpixel((x, i), (r, g, b))

        # Add coordinate label at the left
        if y > 0:  # Skip the first line at y=0
            draw.text((5, y), str(y), fill=(0, 0, 0), font=font)

    # Add a compass rose in the bottom-left corner
    compass_center = (50, map_height - 50)
    compass_radius = 30

    # Draw compass circle
    draw.ellipse(
        [
            (compass_center[0] - compass_radius, compass_center[1] - compass_radius),
            (compass_center[0] + compass_radius, compass_center[1] + compass_radius)
        ],
        outline=(0, 0, 0),
        fill=(255, 255, 255, 128)  # Semi-transparent white
    )

    # Draw compass points
    # North
    draw.line(
        [compass_center, (compass_center[0], compass_center[1] - compass_radius)],
        fill=(0, 0, 0),
        width=2
    )
    draw.text(
        (compass_center[0] - 5, compass_center[1] - compass_radius - 15),
        "N",
        fill=(0, 0, 0),
        font=font
    )

    # East
    draw.line(
        [compass_center, (compass_center[0] + compass_radius, compass_center[1])],
        fill=(0, 0, 0),
        width=2
    )
    draw.text(
        (compass_center[0] + compass_radius + 5, compass_center[1] - 5),
        "E",
        fill=(0, 0, 0),
        font=font
    )

    # South
    draw.line(
        [compass_center, (compass_center[0], compass_center[1] + compass_radius)],
        fill=(0, 0, 0),
        width=2
    )
    draw.text(
        (compass_center[0] - 5, compass_center[1] + compass_radius + 5),
        "S",
        fill=(0, 0, 0),
        font=font
    )

    # West
    draw.line(
        [compass_center, (compass_center[0] - compass_radius, compass_center[1])],
        fill=(0, 0, 0),
        width=2
    )
    draw.text(
        (compass_center[0] - compass_radius - 15, compass_center[1] - 5),
        "W",
        fill=(0, 0, 0),
        font=font
    )

    # Add a title and legend
    # Title
    draw.rectangle(
        [(map_width // 2 - 100, 10), (map_width // 2 + 100, 40)],
        fill=(255, 255, 255, 200)  # Semi-transparent white
    )
    draw.text(
        (map_width // 2 - 80, 15),
        "Procedurally Generated Fantasy Map",
        fill=(0, 0, 0),
        font=font
    )

    # Legend - position in the extended area to the right of the map
    legend_x = map_width + 20  # 20 pixels padding from the map edge
    legend_y = 50
    legend_spacing = 20

    # Draw a border around the legend area
    draw.rectangle(
        [(map_width + 5, 10), (canvas_width - 10, canvas_height - 10)],
        outline=(100, 100, 100),
        width=1
    )

    # Add map seed information
    if current_map_seed is not None:
        draw.text(
            (map_width + 20, canvas_height - 60),
            f"Map Seed: {current_map_seed}",
            fill=(0, 0, 0),
            font=font
        )

    # Add travel pace information
    draw.text(
        (map_width + 20, canvas_height - 45),
        f"Travel Pace (6-hour period): Road: {TRAVEL_PACE['road']} mi, Clear: {TRAVEL_PACE['clear']} mi,",
        fill=(0, 0, 0),
        font=font
    )
    draw.text(
        (map_width + 20, canvas_height - 30),
        f"Difficult: {TRAVEL_PACE['difficult']} mi, Very Difficult: {TRAVEL_PACE['very_difficult']} mi",
        fill=(0, 0, 0),
        font=font
    )

    # Add scale information
    draw.text(
        (map_width + 20, canvas_height - 15),
        "Map Scale: 1 pixel = 0.5 miles",
        fill=(0, 0, 0),
        font=font
    )

    # Legend background
    draw.rectangle(
        [(legend_x - 10, legend_y - 10), (legend_x + 100, legend_y + 180)],
        fill=(255, 255, 255, 200)  # Semi-transparent white
    )

    # Legend title
    draw.text(
        (legend_x, legend_y),
        "Legend",
        fill=(0, 0, 0),
        font=font
    )

    # Terrain types
    legend_y += legend_spacing
    # Water
    draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(65, 105, 225)  # Blue
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Water",
        fill=(0, 0, 0),
        font=font
    )

    # Plains
    legend_y += legend_spacing
    draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(34, 139, 34)  # Green
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Plains",
        fill=(0, 0, 0),
        font=font
    )

    # Hills
    legend_y += legend_spacing
    draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(107, 142, 35)  # Olive green
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Hills",
        fill=(0, 0, 0),
        font=font
    )

    # Mountains
    legend_y += legend_spacing
    draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(128, 128, 128)  # Gray
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Mountains",
        fill=(0, 0, 0),
        font=font
    )

    # Political Boundaries
    legend_y += legend_spacing
    draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(139, 0, 0)  # Dark red
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Kingdom Boundaries",
        fill=(0, 0, 0),
        font=font
    )

    # Territory Fill
    legend_y += legend_spacing
    # Create a semi-transparent rectangle
    territory_overlay = Image.new('RGBA', (15, 15), (100, 100, 200, 40))
    img.paste(territory_overlay, (legend_x, legend_y), territory_overlay)
    # Add border
    canvas_draw.rectangle(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        outline=(0, 0, 0)
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Territory Area",
        fill=(0, 0, 0),
        font=font
    )

    # Settlements
    # City
    legend_y += legend_spacing
    draw.ellipse(
        [(legend_x, legend_y), (legend_x + 15, legend_y + 15)],
        fill=(255, 0, 0)
    )
    draw.text(
        (legend_x + 20, legend_y),
        "City",
        fill=(0, 0, 0),
        font=font
    )

    # Town
    legend_y += legend_spacing
    draw.ellipse(
        [(legend_x + 3, legend_y + 3), (legend_x + 12, legend_y + 12)],
        fill=(255, 165, 0)
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Town",
        fill=(0, 0, 0),
        font=font
    )

    # Roads
    legend_y += legend_spacing
    # Major road
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(50, 50, 50),
        width=5
    )
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(120, 120, 120),
        width=3
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Major Road",
        fill=(0, 0, 0),
        font=font
    )

    # Medium road
    legend_y += legend_spacing
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(50, 50, 50),
        width=4
    )
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(150, 150, 150),
        width=2
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Medium Road",
        fill=(0, 0, 0),
        font=font
    )

    # Path
    legend_y += legend_spacing
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(210, 180, 140),
        width=2
    )
    # Dotted line
    for i in range(0, 15, 4):
        draw.line(
            [(legend_x + i, legend_y + 7), (legend_x + i + 2, legend_y + 7)],
            fill=(139, 69, 19),
            width=1
        )
    draw.text(
        (legend_x + 20, legend_y),
        "Path",
        fill=(0, 0, 0),
        font=font
    )

    # Journey path
    legend_y += legend_spacing
    draw.line(
        [(legend_x, legend_y + 7), (legend_x + 15, legend_y + 7)],
        fill=(255, 0, 255),
        width=2
    )
    draw.text(
        (legend_x + 20, legend_y),
        "Journey Path",
        fill=(0, 0, 0),
        font=font
    )

    # Journey markers
    marker_size = 6

    # Morning marker (sun)
    legend_y += legend_spacing
    # Draw a circle for sun
    draw.ellipse((legend_x-marker_size+7, legend_y-marker_size+7, legend_x+marker_size+7, legend_y+marker_size+7),
                fill=(255, 200, 0), outline=(0, 0, 0))
    # Add rays
    for angle in range(0, 360, 45):
        rad = angle * 3.14159 / 180
        x1 = legend_x + 7 + int(marker_size * 1.2 * np.cos(rad))
        y1 = legend_y + 7 + int(marker_size * 1.2 * np.sin(rad))
        x2 = legend_x + 7 + int(marker_size * 1.8 * np.cos(rad))
        y2 = legend_y + 7 + int(marker_size * 1.8 * np.sin(rad))
        draw.line((x1, y1, x2, y2), fill=(255, 200, 0), width=1)
    draw.text(
        (legend_x + 20, legend_y),
        "Morning Stop",
        fill=(0, 0, 0),
        font=font
    )

    # Midday marker (circle)
    legend_y += legend_spacing
    draw.ellipse((legend_x-marker_size+7, legend_y-marker_size+7, legend_x+marker_size+7, legend_y+marker_size+7),
                fill=(255, 255, 0), outline=(0, 0, 0))
    draw.text(
        (legend_x + 20, legend_y),
        "Midday Stop",
        fill=(0, 0, 0),
        font=font
    )

    # Evening marker (half-moon)
    legend_y += legend_spacing
    draw.ellipse((legend_x-marker_size+7, legend_y-marker_size+7, legend_x+marker_size+7, legend_y+marker_size+7),
                fill=(200, 200, 255), outline=(0, 0, 0))
    # Cover half to make a half-moon
    draw.rectangle((legend_x+7, legend_y-marker_size+7, legend_x+marker_size+7, legend_y+marker_size+7),
                fill=(0, 0, 100), outline=None)
    draw.text(
        (legend_x + 20, legend_y),
        "Evening Stop",
        fill=(0, 0, 0),
        font=font
    )

    # Night/resting marker (tent)
    legend_y += legend_spacing
    # Draw a triangle for tent
    draw.polygon([(legend_x+7, legend_y-marker_size+7), (legend_x-marker_size+7, legend_y+marker_size+7), (legend_x+marker_size+7, legend_y+marker_size+7)],
                fill=(100, 100, 255), outline=(0, 0, 0))
    # Add a small line at the bottom for tent entrance
    draw.line((legend_x+7-2, legend_y+marker_size+7, legend_x+7+2, legend_y+marker_size+7), fill=(0, 0, 0), width=1)
    draw.text(
        (legend_x + 20, legend_y),
        "Night Camp",
        fill=(0, 0, 0),
        font=font
    )

    # Save the image
    img.save("output/map_with_journey.png")
    print("Map visualization saved to output/map_with_journey.png")

    return img


# Main execution
if __name__ == "__main__":
    # Create test map and simulate journey
    journey_log = create_test_map_and_simulate_journey()

    # Print journey log
    print("\nJourney Log:")
    print("===========")
    for entry in journey_log:
        print(f"\nTurn {entry['turn']} at position {entry['position']}:")
        print(entry['description'])

    print("\nTest complete! Check the output directory for the map visualization.")
