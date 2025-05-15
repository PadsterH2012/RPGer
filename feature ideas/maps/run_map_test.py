"""
Run Map Weather Journey Test

This script runs the map weather journey test, which:
1. Creates a procedurally generated map with terrain, rivers, and settlements
2. Adds dynamic weather patterns to the map
3. Simulates a 10-turn journey between two cities
4. Generates rich descriptions of each turn, including terrain, weather, and encounters
5. Creates a visualization of the map with the journey path

Requirements:
- numpy
- matplotlib
- noise (pip install noise)
- PIL (pip install pillow)

Make sure the following files are in the same directory:
- seed_based_layered_map_system.py
- additional_map_layers.py
- map_weather_journey_test.py
"""

import os
import sys
from pathlib import Path

# Create output directory if it doesn't exist
Path("output").mkdir(exist_ok=True)

# Import the test module
from map_weather_journey_test import create_test_map_and_simulate_journey

def main():
    """Run the map weather journey test"""
    print("Starting Map Weather Journey Test...")
    print("===================================")
    print("This test will:")
    print("1. Create a procedurally generated map")
    print("2. Add dynamic weather patterns")
    print("3. Simulate a 10-turn journey")
    print("4. Generate a visualization")
    print("\nPlease wait, this may take a minute...\n")

    # Run the test
    journey_log = create_test_map_and_simulate_journey()

    # Print journey log
    print("\nJourney Log:")
    print("===========")

    # Group entries by day
    current_day = 0
    daily_miles = 0
    total_miles = 0

    for entry in journey_log:
        # Print day header if this is a new day
        if entry.get('day', 0) > current_day:
            if current_day > 0:
                print(f"\nTotal distance traveled on Day {current_day}: {daily_miles:.1f} miles")
            current_day = entry.get('day', 0)
            daily_miles = 0
            print(f"\n\n--- DAY {current_day} ---")

        # Track miles
        miles = entry.get('miles_traveled', 0)
        daily_miles += miles
        total_miles = entry.get('total_miles', total_miles)

        # Print entry details
        time_of_day = entry.get('time_of_day', 'unknown')
        position = entry.get('position', 'unknown')
        resting = " (Resting)" if entry.get('resting', False) else ""

        # Add distance information for travel segments
        distance_info = ""
        if not entry.get('resting', False) and miles > 0:
            distance_info = f" - Traveled {miles:.1f} miles (Total: {total_miles:.1f} miles)"

        print(f"\n{time_of_day.upper()}{resting} at position {position}{distance_info}:")
        print(entry['description'])

    # Print total journey distance
    if current_day > 0:
        print(f"\nTotal distance traveled on Day {current_day}: {daily_miles:.1f} miles")

    # Calculate total journey distance from all entries
    total_journey_miles = sum(entry.get('miles_traveled', 0) for entry in journey_log)
    print(f"\nTotal journey distance: {total_journey_miles:.1f} miles")

    # Print completion message
    print("\nTest complete!")
    print(f"Map visualization saved to: {os.path.abspath('output/map_with_journey.png')}")
    print("You can open this image to see the map with the journey path.")

if __name__ == "__main__":
    main()
