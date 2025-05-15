"""
Test script to verify imports are working correctly
"""

print("Testing imports...")

try:
    print("Importing from seed_based_layered_map_system...")
    from seed_based_layered_map_system import MapSystem, TerrainLayer, BaseLayer
    print("✓ Successfully imported from seed_based_layered_map_system")
except Exception as e:
    print(f"✗ Error importing from seed_based_layered_map_system: {e}")

try:
    print("Importing from additional_map_layers...")
    from additional_map_layers import RiversLayer, PoliticalLayer
    print("✓ Successfully imported from additional_map_layers")
except Exception as e:
    print(f"✗ Error importing from additional_map_layers: {e}")

try:
    print("Creating MapSystem...")
    map_system = MapSystem(base_seed=12345)
    print("✓ Successfully created MapSystem")
except Exception as e:
    print(f"✗ Error creating MapSystem: {e}")

try:
    print("Adding terrain layer...")
    map_system.add_layer(
        "terrain", 
        "terrain", 
        seed_modifier=0,
        parameters={
            "width": 128,
            "height": 128,
            "scale": 100.0,
            "sea_level": -0.1
        }
    )
    print("✓ Successfully added terrain layer")
except Exception as e:
    print(f"✗ Error adding terrain layer: {e}")

try:
    print("Adding rivers layer...")
    map_system.add_layer(
        "rivers", 
        "rivers", 
        seed_modifier=500,
        parameters={
            "width": 128,
            "height": 128,
            "num_rivers": 5
        }
    )
    print("✓ Successfully added rivers layer")
except Exception as e:
    print(f"✗ Error adding rivers layer: {e}")

try:
    print("Generating layers...")
    map_system.generate_all_layers()
    print("✓ Successfully generated layers")
except Exception as e:
    print(f"✗ Error generating layers: {e}")

print("\nImport test complete!")
