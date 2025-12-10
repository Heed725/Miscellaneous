# Complete Prettymaps Tutorial: Installation & Usage Guide

## Table of Contents
1. [What is Prettymaps?](#what-is-prettymaps)
2. [Installation Methods](#installation-methods)
3. [Troubleshooting Common Issues](#troubleshooting-common-issues)
4. [Basic Usage](#basic-usage)
5. [Advanced Examples](#advanced-examples)
6. [Tips & Best Practices](#tips-best-practices)

---

## What is Prettymaps?

Prettymaps is a Python library that creates beautiful, artistic maps from OpenStreetMap data. It allows you to generate stunning visualizations of cities, neighborhoods, and landmarks with customizable colors and styles.

### Key Features
- Generate artistic maps from any location
- Highly customizable color schemes
- Support for different map layers (buildings, streets, water, etc.)
- Export to various image formats
- Based on OpenStreetMap data

---

## Installation Methods

### Method 1: Quick Installation (Recommended for New Users)

**Step 1: Open Command Prompt or Terminal**
- Windows: Press `Win + R`, type `cmd`, press Enter
- Mac/Linux: Open Terminal

**Step 2: Install Prettymaps**
```bash
pip install prettymaps
```

**Step 3: Verify Installation**
```bash
python -c "import prettymaps; print('Success!')"
```

---

### Method 2: Clean Installation (For Dependency Issues)

If you're experiencing errors, follow these steps:

**Step 1: Uninstall Existing Installation**
```bash
pip uninstall prettymaps osmnx geopandas pandas -y
```

**Step 2: Clear Pip Cache**
```bash
pip cache purge
```

**Step 3: Install Compatible Versions**
```bash
pip install "numpy<2.0.0,>=1.21.6"
pip install "pandas>=1.4,<3.0"
pip install "Pillow<11.0,>=10.1"
pip install "charset-normalizer<3.0,>=2.0"
pip install setuptools
```

**Step 4: Install Prettymaps**
```bash
pip install prettymaps
```

**Step 5: Verify Installation**
```bash
python -c "import prettymaps; print('Installation successful!')"
```

---

### Method 3: Virtual Environment (Best Practice)

Using a virtual environment isolates your project dependencies and prevents conflicts.

**Step 1: Create a Project Folder**
```bash
mkdir prettymaps_project
cd prettymaps_project
```

**Step 2: Create Virtual Environment**
```bash
python -m venv venv
```

**Step 3: Activate Virtual Environment**

*Windows:*
```bash
venv\Scripts\activate
```

*Mac/Linux:*
```bash
source venv/bin/activate
```

**Step 4: Install Prettymaps**
```bash
pip install "numpy<2.0.0" "pandas>=1.4" "Pillow<11.0" prettymaps
```

**Step 5: Verify Installation**
```bash
python -c "import prettymaps; print('Success!')"
```

**To Deactivate Virtual Environment:**
```bash
deactivate
```

---

## Troubleshooting Common Issues

### Issue 1: AttributeError: module 'pandas' has no attribute '__version__'

**Solution:**
```bash
pip uninstall pandas -y
pip install "pandas>=1.4,<3.0"
```

### Issue 2: Dependency Conflicts

**Solution:**
```bash
pip uninstall prettymaps osmnx numpy pillow charset-normalizer scipy -y
pip install "numpy<2.0.0,>=1.21.6" "Pillow<11.0,>=10.1" "charset-normalizer<3.0,>=2.0" setuptools
pip install prettymaps scipy
```

### Issue 3: ImportError or ModuleNotFoundError

**Solution:**
```bash
pip cache purge
pip uninstall prettymaps -y
pip install prettymaps --no-cache-dir
```

### Issue 4: GDAL Installation Issues

**Windows Solution:**
1. Download GDAL wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
2. Install it: `pip install GDAL‑3.4.3‑cp310‑cp310‑win_amd64.whl`
3. Then install prettymaps

**Alternative:**
```bash
conda install -c conda-forge gdal
pip install prettymaps
```

### Issue 5: Check for Conflicts

```bash
pip check
```

This command will show you any dependency conflicts.

---

## Basic Usage

### Example 1: Simple Map of a City

```python
import prettymaps

# Create a map of New York City
plot = prettymaps.plot('New York City, USA')
```

### Example 2: Save Map to File

```python
import prettymaps

# Create and save map
plot = prettymaps.plot(
    'Paris, France',
    figsize=(12, 12)
)

# Save to file
plot.savefig('paris_map.png', dpi=300, bbox_inches='tight')
```

### Example 3: Custom Location with Coordinates

```python
import prettymaps

# Use coordinates (latitude, longitude)
plot = prettymaps.plot(
    (40.7580, -73.9855),  # Times Square, NYC
    radius=500  # 500 meters radius
)
```

### Example 4: Customize Colors

```python
import prettymaps

# Custom color palette
plot = prettymaps.plot(
    'Tokyo, Japan',
    preset='barcelona',  # Use preset style
    figsize=(15, 15)
)
```

---

## Advanced Examples

### Example 5: Full Customization

```python
import prettymaps

plot = prettymaps.plot(
    'San Francisco, California',
    radius=1000,
    
    # Custom layers and colors
    layers={
        'perimeter': {},
        'streets': {
            'width': {
                'motorway': 5,
                'trunk': 5,
                'primary': 4.5,
                'secondary': 4,
                'tertiary': 3.5,
                'residential': 3,
            },
            'circle': False
        },
        'building': {'tags': {'building': True}},
        'water': {'tags': {'natural': ['water', 'bay']}},
        'green': {'tags': {'landuse': 'grass', 'natural': ['island', 'wood'], 'leisure': 'park'}},
    },
    
    # Color scheme
    style={
        'background': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'hatch': 'ooo...'},
        'perimeter': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'lw': 0, 'hatch': 'ooo...'},
        'green': {'fc': '#D0F1BF', 'ec': '#2F3737', 'lw': 1},
        'water': {'fc': '#a1e3ff', 'ec': '#2F3737', 'hatch': 'ooo...', 'lw': 1},
        'streets': {'fc': '#2F3737', 'ec': '#475657', 'alpha': 1, 'lw': 0},
        'building': {'palette': ['#FFC857', '#E9724C', '#C5283D'], 'ec': '#2F3737', 'lw': .5},
    },
    
    figsize=(12, 12)
)

plot.savefig('san_francisco_custom.png', dpi=300, bbox_inches='tight')
```

### Example 6: Multiple Maps (Multiplot)

```python
import prettymaps

# Create multiple maps in one figure
prettymaps.multiplot(
    ['London, UK', 'Berlin, Germany', 'Rome, Italy'],
    rows=1,
    cols=3,
    figsize=(18, 6)
)
```

### Example 7: Using Different Presets

```python
import prettymaps

# List available presets
print(prettymaps.presets())

# Use different presets
cities = ['Barcelona, Spain', 'Amsterdam, Netherlands', 'Lisbon, Portugal']
presets = ['barcelona', 'minimal', 'cb-bf-f']

for city, preset in zip(cities, presets):
    plot = prettymaps.plot(
        city,
        preset=preset,
        figsize=(10, 10)
    )
    plot.savefig(f'{city.split(",")[0].lower()}_{preset}.png', dpi=300)
```

### Example 8: Create Your Own Preset

```python
import prettymaps

# Define custom preset
my_preset = {
    'layers': {
        'perimeter': {},
        'streets': {'width': {'motorway': 5, 'trunk': 5, 'primary': 4.5}},
        'building': {'tags': {'building': True}},
        'water': {'tags': {'natural': ['water', 'bay']}},
    },
    'style': {
        'background': {'fc': '#1a1a1a'},
        'perimeter': {'fill': False},
        'streets': {'fc': '#ffbe0b', 'ec': '#fb5607', 'lw': 0.5},
        'building': {'palette': ['#ff006e', '#8338ec', '#3a86ff']},
        'water': {'fc': '#06ffa5'},
    }
}

# Save preset
prettymaps.create_preset('my_style', **my_preset)

# Use your preset
plot = prettymaps.plot('Seattle, USA', preset='my_style')
```

---

## Tips & Best Practices

### 1. Start Small
Begin with a small radius (500-1000 meters) to avoid long processing times:
```python
plot = prettymaps.plot('City Name', radius=500)
```

### 2. Handle Large Areas
For larger areas, increase timeout and be patient:
```python
plot = prettymaps.plot(
    'Large City',
    radius=2000,
    # Network request timeout in seconds
)
```

### 3. Save High-Quality Images
Use high DPI for print-quality images:
```python
plot.savefig('map.png', dpi=600, bbox_inches='tight', facecolor='white')
```

### 4. Experiment with Layers
Try different layer combinations:
```python
# Minimal map (only streets and buildings)
layers = {
    'streets': {'width': {'primary': 3, 'secondary': 2}},
    'building': {'tags': {'building': True}},
}
```

### 5. Use Specific Queries
Be as specific as possible with locations:
```python
# Good
plot = prettymaps.plot('Central Park, Manhattan, New York, USA')

# Less precise
plot = prettymaps.plot('Central Park')
```

### 6. Check Your Installation
Always verify after installation:
```python
import prettymaps
import osmnx
import geopandas

print(f"Prettymaps version: {prettymaps.__version__}")
print(f"OSMnx version: {osmnx.__version__}")
```

### 7. Memory Management
Close plots after saving to free memory:
```python
import matplotlib.pyplot as plt

plot = prettymaps.plot('City')
plot.savefig('city.png')
plt.close()
```

### 8. Batch Processing
Process multiple locations efficiently:
```python
cities = ['London', 'Paris', 'Berlin', 'Madrid', 'Rome']

for city in cities:
    try:
        plot = prettymaps.plot(f'{city}, Europe', radius=800)
        plot.savefig(f'{city.lower()}_map.png', dpi=300)
        plt.close()
        print(f"✓ {city} completed")
    except Exception as e:
        print(f"✗ {city} failed: {e}")
```

---

## Complete Working Example

Here's a complete script you can copy and run:

```python
import prettymaps
import matplotlib.pyplot as plt

def create_city_map(location, filename, radius=1000):
    """
    Create and save a prettymaps visualization
    
    Args:
        location: City name or coordinates
        filename: Output filename
        radius: Radius in meters
    """
    try:
        # Create map
        print(f"Creating map for {location}...")
        plot = prettymaps.plot(
            location,
            radius=radius,
            preset='barcelona',  # Try: 'minimal', 'cb-bf-f', 'barcelona'
            figsize=(12, 12)
        )
        
        # Save map
        plot.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Map saved as {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Create maps for different cities
    cities = [
        ('New York City, USA', 'nyc_map.png'),
        ('Paris, France', 'paris_map.png'),
        ('Tokyo, Japan', 'tokyo_map.png'),
    ]
    
    for location, filename in cities:
        create_city_map(location, filename, radius=1000)
        print()
```

---

## Additional Resources

- **Official Documentation**: https://github.com/marceloprates/prettymaps
- **OpenStreetMap**: https://www.openstreetmap.org
- **OSMnx Documentation**: https://osmnx.readthedocs.io
- **Matplotlib Colors**: https://matplotlib.org/stable/gallery/color/named_colors.html

---

## Quick Reference Commands

```bash
# Install
pip install prettymaps

# Upgrade
pip install --upgrade prettymaps

# Uninstall
pip uninstall prettymaps -y

# Check installation
python -c "import prettymaps; print('OK')"

# List dependencies
pip show prettymaps

# Check for conflicts
pip check

# Clear cache and reinstall
pip cache purge && pip install prettymaps --no-cache-dir
```

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Python version: `python --version` (3.8+ recommended)
3. Check installed packages: `pip list`
4. Look for errors in the output
5. Try installing in a fresh virtual environment

Happy mapping! 🗺️
