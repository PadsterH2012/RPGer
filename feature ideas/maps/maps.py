import numpy as np
import noise # Install: pip install noise
import matplotlib.pyplot as plt
import os # To create directory if needed

# --- Configuration ---
width, height = 1024, 1024 # Map dimensions (larger)

# Noise parameters tuned for larger features but with more detail
# Experiment with these values!
scale = 300.0           # Larger scale for bigger base features relative to map size
octaves = 8             # Increased octaves for more detail/complexity
persistence = 0.5       # Slightly increased persistence for more prominent detail
lacunarity = 2.0        # Standard, controls frequency increase per octave
seed = np.random.randint(0, 100000) # Use a random seed for variety

# Threshold for land/sea (adjust this to control land vs sea ratio)
# Noise range is typically -1 to 1, so 0 is a common middle
sea_level_threshold = 0.0 # Points > threshold are land

# Saving configuration
output_dir = "generated_maps"
output_filename = f"fantasy_landscape_{seed}.png"
full_output_path = os.path.join(output_dir, output_filename)
dpi = 300 # Higher DPI for better resolution in saved image

# --- Ensure Output Directory Exists ---
os.makedirs(output_dir, exist_ok=True)

# --- Generate Noise Map (Base Elevation) ---
print(f"Generating noise map ({width}x{height}) with seed: {seed}...")
world = np.zeros((height, width))
for y in range(height):
    for x in range(width):
        # Normalize coordinates to a smaller range relative to scale
        # Using x/width * scale, y/height * scale is a common approach
        world[y][x] = noise.pnoise2(x / scale,
                                    y / scale,
                                    octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=width, # Optional: makes map tileable
                                    repeaty=height,
                                    base=seed) # Use a seed for reproducibility or randomness

print("Noise generation complete.")

# --- Determine Land vs. Sea ---
# Create a mask: True for land (above threshold), False for sea
land_mask = world > sea_level_threshold

# --- Prepare Data for Visualization ---
# Create a map array initialized with a 'sea' value (e.g., 0)
visual_map = np.zeros((height, width))

# Assign elevation values to land areas using the original noise
land_elevations = world[land_mask]

if land_elevations.size > 0: # Avoid issues if there's no land generated
    min_elev = np.min(land_elevations)
    max_elev = np.max(land_elevations)

    # Map land elevations to a different range, e.g., 0.2 to 1.0 within our colormap range
    # (keeping 0 and 0.1 for sea/coast)
    if max_elev > min_elev: # Avoid division by zero if land is perfectly flat (unlikely with noise)
        normalized_land_elevations = 0.2 + 0.8 * (land_elevations - min_elev) / (max_elev - min_elev)
        # Place the normalized land elevations back into the visual map using the mask
        visual_map[land_mask] = normalized_land_elevations
    else: # Handle case where all land points have the same noise value
         visual_map[land_mask] = 0.5 # Assign a default land color mid-range


# Sea level can be represented by a low value (e.g., 0 or 0.1)
# The colormap will handle translating these values to colors

# --- Visualize and Save ---
print(f"Saving map to {full_output_path}...")
plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi) # Set figure size based on desired output DPI

# Use a colormap suitable for terrain and sea
# 'gist_earth' or 'terrain' are good matplotlib colormaps
# We use 'gist_earth' and map 0-0.2 to sea/coast, 0.2-1.0 to terrain
plt.imshow(visual_map, cmap='gist_earth', origin='lower') # origin='lower' often feels more like maps

plt.title("Procedurally Generated Landscape")
plt.axis('off') # Hide axes
plt.tight_layout(pad=0) # Adjust layout to remove padding
plt.savefig(full_output_path, bbox_inches='tight', pad_inches=0) # Save the figure
plt.close() # Close the plot to free memory

print(f"Map saved successfully to {full_output_path}")