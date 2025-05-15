"""
Map Usage Examples for Seed-Based Layered Map System

This file demonstrates how agents can use the seed-based layered map system
for various RPG gameplay functions.
"""

import numpy as np
import json
from seed_based_layered_map_system import MapSystem


def create_sample_map():
    """Create a sample map with multiple layers for demonstration"""
    # Create map system with a fixed seed for reproducibility
    map_system = MapSystem(base_seed=12345)
    
    # Add terrain layer
    map_system.add_layer(
        "terrain", 
        "terrain", 
        seed_modifier=0,  # Use base seed exactly
        parameters={
            "width": 512,
            "height": 512,
            "scale": 100.0,
            "sea_level": -0.1  # More land
        }
    )
    
    # Add rivers layer
    map_system.add_layer(
        "rivers", 
        "rivers", 
        seed_modifier=500,  # Different seed for rivers
        parameters={
            "width": 512,
            "height": 512,
            "num_rivers": 15
        }
    )
    
    # Add political layer
    map_system.add_layer(
        "kingdoms", 
        "political", 
        seed_modifier=1000,  # Different seed for political boundaries
        parameters={
            "width": 512,
            "height": 512,
            "num_territories": 6,
            "territory_names": [
                "Eldoria", "Westmark", "Sunhaven", 
                "Frostpeak", "Greendale", "Shadowvale"
            ]
        }
    )
    
    # Generate all layers
    map_system.generate_all_layers()
    
    return map_system


# Example 1: Location-Based Storytelling
def describe_location(map_system, x, y):
    """Generate a rich description of a location based on map data"""
    # Query all layers at this point
    data = map_system.query_at_point(x, y)
    
    # Build description based on available data
    description = ""
    
    # Terrain description
    if "terrain" in data and data["terrain"]:
        terrain_data = data["terrain"]
        terrain_type = terrain_data["terrain_type"]
        
        if not terrain_data["is_land"]:
            if terrain_type == "deep_water":
                description += "You are sailing on the deep blue sea. "
            else:
                description += "You are in shallow coastal waters. "
        else:
            if terrain_type == "beach":
                description += "You stand on a sandy beach with waves lapping at the shore. "
            elif terrain_type == "plains":
                description += "You are in open grasslands with gentle rolling hills. "
            elif terrain_type == "hills":
                description += "You are in hilly terrain with rocky outcroppings. "
            elif terrain_type == "mountains":
                description += "You are in rugged mountain terrain with steep slopes. "
            elif terrain_type == "snow_peaks":
                description += "You are high in snow-capped mountain peaks. "
    
    # River description
    if "rivers" in data and data["rivers"]:
        river_data = data["rivers"]
        if river_data["has_river"]:
            if river_data["river_size"] > 3:
                description += "A wide, rushing river flows through here. "
            else:
                description += "A small stream trickles nearby. "
    
    # Political information
    if "kingdoms" in data and data["kingdoms"]:
        kingdom_data = data["kingdoms"]
        if kingdom_data["territory_id"] >= 0:
            description += f"You are in the lands of {kingdom_data['territory_name']}. "
            if kingdom_data["is_capital"]:
                description += f"This is the capital city of {kingdom_data['territory_name']}. "
    
    return description


# Example 2: Navigation and Pathfinding
def find_path(map_system, start_x, start_y, dest_x, dest_y, travel_mode="walking"):
    """Find a path between two points, considering terrain difficulty"""
    # A* pathfinding implementation
    import heapq
    
    # Define movement costs based on terrain and travel mode
    def get_movement_cost(x, y):
        data = map_system.query_at_point(x, y)
        
        # Default high cost for impassable terrain
        cost = 1000
        
        if "terrain" in data and data["terrain"]:
            terrain_data = data["terrain"]
            terrain_type = terrain_data["terrain_type"]
            
            # Different costs based on travel mode
            if travel_mode == "walking":
                if not terrain_data["is_land"]:
                    return cost  # Can't walk on water
                
                # Land movement costs
                if terrain_type == "beach":
                    cost = 1.2
                elif terrain_type == "plains":
                    cost = 1.0  # Easiest terrain
                elif terrain_type == "hills":
                    cost = 2.0
                elif terrain_type == "mountains":
                    cost = 5.0
                elif terrain_type == "snow_peaks":
                    cost = 8.0
                    
            elif travel_mode == "boat":
                if terrain_data["is_land"]:
                    return cost  # Can't sail on land
                
                # Water movement costs
                if terrain_type == "deep_water":
                    cost = 1.0
                elif terrain_type == "shallow_water":
                    cost = 1.5
                    
            elif travel_mode == "flying":
                # Flying ignores most terrain but still affected by mountains
                if terrain_type == "mountains" or terrain_type == "snow_peaks":
                    cost = 2.0
                else:
                    cost = 1.0
        
        # Rivers affect movement
        if "rivers" in data and data["rivers"]:
            river_data = data["rivers"]
            if river_data["has_river"]:
                if travel_mode == "walking":
                    cost += river_data["river_size"] * 2  # Harder to cross bigger rivers
        
        return cost
    
    # A* implementation
    open_set = [(0, start_x, start_y)]  # (f_score, x, y)
    came_from = {}
    g_score = {(start_x, start_y): 0}
    f_score = {(start_x, start_y): np.sqrt((dest_x - start_x)**2 + (dest_y - start_y)**2)}
    
    while open_set:
        _, current_x, current_y = heapq.heappop(open_set)
        
        # Check if we reached the destination
        if current_x == dest_x and current_y == dest_y:
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
                width = map_system.layers["terrain"].width
                height = map_system.layers["terrain"].height
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
                    f_score[(neighbor_x, neighbor_y)] = tentative_g + np.sqrt((dest_x - neighbor_x)**2 + (dest_y - neighbor_y)**2)
                    heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], neighbor_x, neighbor_y))
    
    # No path found
    return None


# Example 3: Resource and Feature Discovery
def find_nearest_resource(map_system, x, y, resource_type, max_distance=50):
    """Find the nearest specified resource or feature"""
    # This is a simplified version - a real implementation would use a more efficient search
    
    # Define what we're looking for based on resource_type
    def is_target(data):
        if resource_type == "water":
            return "terrain" in data and data["terrain"] and not data["terrain"]["is_land"]
        elif resource_type == "river":
            return "rivers" in data and data["rivers"] and data["rivers"]["has_river"]
        elif resource_type == "mountain":
            return ("terrain" in data and data["terrain"] and 
                   data["terrain"]["terrain_type"] in ["mountains", "snow_peaks"])
        elif resource_type == "capital":
            return ("kingdoms" in data and data["kingdoms"] and 
                   data["kingdoms"]["is_capital"])
        return False
    
    # Search in expanding circles
    for distance in range(1, max_distance + 1):
        for dx in range(-distance, distance + 1):
            for dy in [-distance, distance]:  # Top and bottom edges
                nx, ny = x + dx, y + dy
                if 0 <= nx < map_system.layers["terrain"].width and 0 <= ny < map_system.layers["terrain"].height:
                    data = map_system.query_at_point(nx, ny)
                    if is_target(data):
                        return (nx, ny, distance)
                        
        for dy in range(-distance + 1, distance):  # Left and right edges (excluding corners)
            for dx in [-distance, distance]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < map_system.layers["terrain"].width and 0 <= ny < map_system.layers["terrain"].height:
                    data = map_system.query_at_point(nx, ny)
                    if is_target(data):
                        return (nx, ny, distance)
    
    # Not found within max_distance
    return None


# Example 4: Dynamic Event Generation
def generate_encounter(map_system, x, y, party_level):
    """Generate an appropriate encounter based on location"""
    data = map_system.query_at_point(x, y)
    
    # Determine encounter type based on terrain
    encounter_type = "generic"
    encounter_difficulty = 1.0  # Modifier for party level
    
    if "terrain" in data and data["terrain"]:
        terrain_data = data["terrain"]
        terrain_type = terrain_data["terrain_type"]
        
        if not terrain_data["is_land"]:
            encounter_type = "aquatic"
            if terrain_type == "deep_water":
                encounter_difficulty = 1.5  # Deeper water = more dangerous
        else:
            if terrain_type == "beach":
                encounter_type = "coastal"
            elif terrain_type == "plains":
                encounter_type = "plains"
            elif terrain_type == "hills":
                encounter_type = "hills"
                encounter_difficulty = 1.2
            elif terrain_type == "mountains":
                encounter_type = "mountain"
                encounter_difficulty = 1.5
            elif terrain_type == "snow_peaks":
                encounter_type = "alpine"
                encounter_difficulty = 2.0
    
    # Modify based on political control
    if "kingdoms" in data and data["kingdoms"]:
        kingdom_data = data["kingdoms"]
        if kingdom_data["territory_id"] >= 0:
            # Civilized areas have different encounters
            if kingdom_data["is_capital"]:
                encounter_type = "urban"
                encounter_difficulty = 0.8  # Safer in capitals
            else:
                # Mix of wilderness and civilized encounters
                if np.random.random() < 0.7:  # 70% chance of civilized encounter
                    encounter_type = "civilized_" + encounter_type
                    encounter_difficulty *= 0.9  # Slightly safer
    
    # Calculate final difficulty
    final_difficulty = int(party_level * encounter_difficulty)
    if final_difficulty < 1:
        final_difficulty = 1
    
    # Return encounter details
    return {
        "type": encounter_type,
        "difficulty": final_difficulty,
        "location": f"({x}, {y})"
    }


# Example usage
if __name__ == "__main__":
    # Create a sample map
    map_system = create_sample_map()
    
    # Example 1: Describe a location
    print("Location Description:")
    print(describe_location(map_system, 250, 250))
    print()
    
    # Example 2: Find a path
    print("Path Finding:")
    path = find_path(map_system, 200, 200, 300, 300)
    if path:
        print(f"Found path with {len(path)} steps")
    else:
        print("No path found")
    print()
    
    # Example 3: Find nearest resource
    print("Resource Finding:")
    result = find_nearest_resource(map_system, 250, 250, "river")
    if result:
        x, y, distance = result
        print(f"Found river at ({x}, {y}), {distance} units away")
    else:
        print("No river found within search radius")
    print()
    
    # Example 4: Generate encounter
    print("Encounter Generation:")
    encounter = generate_encounter(map_system, 250, 250, 5)
    print(f"Encounter: {encounter['type']}, Difficulty: {encounter['difficulty']}")
    print()
    
    # Save the map for later use
    map_system.save_to_file("sample_map.json")
    print("Map saved to sample_map.json")
