"""
Seed-Based Layered Map System Design

This file contains the design for a comprehensive seed-based map system
that supports multiple layers with independent seeds. This allows for:
- Static layers that remain consistent across campaigns
- Dynamic layers that can change during gameplay
- Shared worlds where different players can experience the same geography
  but with different political, resource, or point-of-interest layers

The system is built around the concept of a base seed that can be modified
per layer, allowing for controlled randomization.
"""

import numpy as np
import noise
import json
import time
from queue import PriorityQueue

# Import layer types - these will be defined later in this file
# and in additional_map_layers.py
from additional_map_layers import RiversLayer, PoliticalLayer

class MapSystem:
    """Master class that manages all map layers and their interactions"""
    def __init__(self, base_seed=None):
        self.base_seed = base_seed or np.random.randint(0, 1000000)
        self.layers = {}  # Store all layer objects
        self.layer_seeds = {}  # Track seeds for each layer
        self.layer_parameters = {}  # Store parameters for each layer
        self.layer_timestamps = {}  # When each layer was last modified

    def add_layer(self, layer_name, layer_type, seed_modifier=0, parameters=None):
        """Add a new layer to the map system"""
        layer_seed = self.base_seed + seed_modifier
        self.layer_seeds[layer_name] = layer_seed
        self.layer_parameters[layer_name] = parameters or {}

        # Create appropriate layer type
        if layer_type == "terrain":
            self.layers[layer_name] = TerrainLayer(layer_seed, parameters)
        elif layer_type == "political":
            self.layers[layer_name] = PoliticalLayer(layer_seed, parameters)
        elif layer_type == "rivers":
            self.layers[layer_name] = RiversLayer(layer_seed, parameters)
        # These layer types are defined in map_weather_journey_test.py
        # and will be added manually
        # elif layer_type == "settlements":
        #     self.layers[layer_name] = SettlementsLayer(layer_seed, parameters)
        # Add more layer types as needed

        self.layer_timestamps[layer_name] = time.time()
        return self.layers[layer_name]

    def generate_all_layers(self):
        """Generate all registered layers in the correct order"""
        # Generate in dependency order (terrain first, then others)
        dependency_order = self._calculate_layer_dependencies()
        for layer_name in dependency_order:
            self._generate_layer_with_dependencies(layer_name)

    def _calculate_layer_dependencies(self):
        """Calculate the order in which layers should be generated"""
        # Simple implementation - predefined order based on common dependencies
        layer_types = {name: layer.layer_type for name, layer in self.layers.items()}

        # Define dependency order
        type_order = ["terrain", "rivers", "resources", "settlements", "political", "points_of_interest"]

        # Sort layer names by their type's position in the dependency order
        sorted_layers = sorted(
            self.layers.keys(),
            key=lambda name: type_order.index(layer_types[name]) if layer_types[name] in type_order else 999
        )

        return sorted_layers

    def _generate_layer_with_dependencies(self, layer_name):
        """Generate a layer, providing it with its dependencies"""
        layer = self.layers[layer_name]

        # Determine which dependencies this layer needs
        if layer.layer_type == "rivers":
            # Rivers need terrain
            terrain_layer = self._find_layer_by_type("terrain")
            if terrain_layer:
                layer.generate(terrain_layer=terrain_layer)
            else:
                raise ValueError(f"Layer {layer_name} requires a terrain layer")

        elif layer.layer_type == "political":
            # Political needs terrain and optionally rivers
            terrain_layer = self._find_layer_by_type("terrain")
            rivers_layer = self._find_layer_by_type("rivers")
            if terrain_layer:
                layer.generate(terrain_layer=terrain_layer, rivers_layer=rivers_layer)
            else:
                raise ValueError(f"Layer {layer_name} requires a terrain layer")

        elif layer.layer_type == "settlements":
            # Settlements need terrain, rivers, and optionally political
            terrain_layer = self._find_layer_by_type("terrain")
            rivers_layer = self._find_layer_by_type("rivers")
            political_layer = self._find_layer_by_type("political")
            if terrain_layer:
                layer.generate(
                    terrain_layer=terrain_layer,
                    rivers_layer=rivers_layer,
                    political_layer=political_layer
                )
            else:
                raise ValueError(f"Layer {layer_name} requires a terrain layer")

        else:
            # Default - no dependencies
            layer.generate()

    def _find_layer_by_type(self, layer_type):
        """Find the first layer of a given type"""
        for layer in self.layers.values():
            if layer.layer_type == layer_type:
                return layer
        return None

    def query_at_point(self, x, y, layer_names=None):
        """Query information at a specific point across specified layers"""
        result = {}
        layers_to_query = layer_names or self.layers.keys()

        for layer_name in layers_to_query:
            if layer_name in self.layers:
                result[layer_name] = self.layers[layer_name].get_data_at(x, y)

        return result

    def save_to_file(self, filename):
        """Save the entire map system to a file"""
        data = {
            "base_seed": self.base_seed,
            "layer_seeds": self.layer_seeds,
            "layer_parameters": self.layer_parameters,
            "layer_timestamps": self.layer_timestamps,
            "layer_data": {}
        }

        # Save each layer's data
        for name, layer in self.layers.items():
            data["layer_data"][name] = layer.serialize()

        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_from_file(cls, filename):
        """Load a map system from a file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        map_system = cls(data["base_seed"])

        # Recreate each layer
        for layer_name, layer_data in data["layer_data"].items():
            layer_type = layer_data["type"]
            parameters = data["layer_parameters"].get(layer_name, {})
            seed_modifier = data["layer_seeds"][layer_name] - data["base_seed"]

            layer = map_system.add_layer(layer_name, layer_type, seed_modifier, parameters)
            layer.deserialize(layer_data)

        return map_system


class BaseLayer:
    """Base class for all map layers"""
    def __init__(self, seed, parameters=None):
        self.seed = seed
        self.parameters = parameters or {}
        self.data = None
        self.width = parameters.get("width", 1024)
        self.height = parameters.get("height", 1024)
        self.generated = False
        self.layer_type = "base"  # Override in subclasses

    def generate(self):
        """Generate the layer data - implement in subclasses"""
        raise NotImplementedError

    def get_data_at(self, x, y):
        """Get data at specific coordinates"""
        if not self.generated:
            self.generate()

        # Implement point query logic
        raise NotImplementedError

    def serialize(self):
        """Convert layer to serializable format"""
        return {
            "type": self.layer_type,
            "width": self.width,
            "height": self.height,
            "seed": self.seed,
            # Subclasses should add their specific data
        }

    def deserialize(self, data):
        """Load layer from serialized data"""
        self.width = data["width"]
        self.height = data["height"]
        self.seed = data["seed"]
        self.generated = True
        # Subclasses should restore their specific data


class TerrainLayer(BaseLayer):
    """Layer for basic terrain and elevation"""
    def __init__(self, seed, parameters=None):
        super().__init__(seed, parameters)
        self.layer_type = "terrain"
        self.elevation = None
        self.land_mask = None
        self.terrain_types = None

    def generate(self):
        """Generate terrain using noise functions"""
        # Similar to your existing maps.py terrain generation
        np.random.seed(self.seed)

        # Get parameters with defaults - adjusted for more natural terrain
        scale = self.parameters.get("scale", 150.0)  # Increased scale for larger features
        octaves = self.parameters.get("octaves", 6)  # Reduced octaves
        persistence = self.parameters.get("persistence", 0.45)  # Slightly reduced persistence
        lacunarity = self.parameters.get("lacunarity", 2.2)  # Increased lacunarity
        sea_level = self.parameters.get("sea_level", 0.0)

        # Generate elevation using noise
        self.elevation = np.zeros((self.height, self.width))

        # Add some randomization to avoid grid patterns
        x_offset = np.random.random() * 100
        y_offset = np.random.random() * 100

        for y in range(self.height):
            for x in range(self.width):
                # Remove the repeatx and repeaty parameters to avoid tiling
                # Add random offsets to coordinates
                self.elevation[y][x] = noise.pnoise2(
                    (x + x_offset) / scale,
                    (y + y_offset) / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    base=self.seed
                )

                # Add a second layer of noise for more variation
                self.elevation[y][x] += 0.3 * noise.pnoise2(
                    (x + x_offset*2) / (scale/3),
                    (y + y_offset*2) / (scale/3),
                    octaves=octaves+2,
                    persistence=persistence-0.1,
                    lacunarity=lacunarity+0.5,
                    base=self.seed+1
                )

        # Create land mask
        self.land_mask = self.elevation > sea_level

        # Classify terrain types
        self.terrain_types = np.zeros((self.height, self.width), dtype=np.uint8)
        self._classify_terrain_types()

        self.generated = True
        return self

    def _classify_terrain_types(self):
        """Classify terrain into types based on elevation"""
        # Example terrain codes:
        # 0 = deep water, 1 = shallow water, 2 = beach, 3 = plains,
        # 4 = hills, 5 = mountains, 6 = snow peaks

        sea_level = self.parameters.get("sea_level", 0.0)

        # Find min/max elevation on land for normalization
        land_elevations = self.elevation[self.land_mask]
        if land_elevations.size > 0:
            min_elev = np.min(land_elevations)
            max_elev = np.max(land_elevations)

            # Classify water
            self.terrain_types[self.elevation <= sea_level - 0.3] = 0  # Deep water
            self.terrain_types[(self.elevation > sea_level - 0.3) &
                              (self.elevation <= sea_level)] = 1  # Shallow water

            # Classify land
            if max_elev > min_elev:  # Avoid division by zero
                norm_range = max_elev - min_elev

                # Beach - just above sea level
                beach_mask = (self.elevation > sea_level) & (self.elevation <= sea_level + 0.05)
                self.terrain_types[beach_mask] = 2

                # Plains - lower elevations
                plains_threshold = sea_level + 0.05 + norm_range * 0.2
                plains_mask = (self.elevation > sea_level + 0.05) & (self.elevation <= plains_threshold)
                self.terrain_types[plains_mask] = 3

                # Hills - middle elevations
                hills_threshold = plains_threshold + norm_range * 0.3
                hills_mask = (self.elevation > plains_threshold) & (self.elevation <= hills_threshold)
                self.terrain_types[hills_mask] = 4

                # Mountains - higher elevations
                mountains_threshold = hills_threshold + norm_range * 0.3
                mountains_mask = (self.elevation > hills_threshold) & (self.elevation <= mountains_threshold)
                self.terrain_types[mountains_mask] = 5

                # Snow peaks - highest elevations
                snow_mask = self.elevation > mountains_threshold
                self.terrain_types[snow_mask] = 6

    def get_data_at(self, x, y):
        """Get terrain data at specific coordinates"""
        if not self.generated:
            self.generate()

        if 0 <= x < self.width and 0 <= y < self.height:
            terrain_type = int(self.terrain_types[y][x])
            terrain_names = ["deep_water", "shallow_water", "beach",
                            "plains", "hills", "mountains", "snow_peaks"]

            return {
                "elevation": float(self.elevation[y][x]),
                "is_land": bool(self.land_mask[y][x]),
                "terrain_type_code": terrain_type,
                "terrain_type": terrain_names[terrain_type] if terrain_type < len(terrain_names) else "unknown"
            }
        return None
