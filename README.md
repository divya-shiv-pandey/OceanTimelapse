# Floating Solar - Wave Height Inspector

Interactive web application to inspect maximum wave heights globally for floating solar site selection.

## Quick Start

1. Create and Activate virtual environment:
```bash
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if not already installed):
```bash
pip install xarray netCDF4 numpy flask
```

3. Run the application:
```bash
python app.py
```

4. Open your browser to: `http://localhost:5000`

5. Click anywhere on the map to see wave height data

## Project Structure

```
.
├── app.py                          # Flask web application
├── templates/
│   └── index.html                  # Interactive map interface
├── q1_max_wave_at_origin.py        # Script answering Q1
├── explore_data.py                 # Data exploration script
├── waves_2019-01-01/
│   └── waves_2019-01-01.nc         # Wave data (NetCDF format)
├── NOTES.md                        # Detailed project documentation
└── README.md                       # This file
```

## Features

- Interactive global map
- Click-to-query wave height data
- Shows maximum, mean, and minimum wave heights for 2019-01-01
- Nearest-neighbor interpolation for clicked coordinates
- Clean, focused UI

## Question Answers

### Q1: Maximum wave height at (0.0, 0.0)?

**Answer: 2.326 meters**

Run `python q1_max_wave_at_origin.py` to see the full calculation.

### Q2: Interactive map

Launch the application with `python app.py` and access at `http://localhost:5000`

### Q3 & Q4: See NOTES.md

Detailed explanations for scaling to 70 years of data and questions for the designer are in `NOTES.md`.

## Data Source

Wave data from ERA5 reanalysis dataset (ECMWF)
- Date: 2019-01-01
- Provided Resolution: 0.5° x 0.5° (approx 50km)
- Temporal: Hourly (24 timesteps)
- Coverage: Global (-60° to 70° latitude)

## Key Variables

- `hmax`: Maximum individual wave height (meters)
- `swh`: Significant wave height
- `mwd`: Mean wave direction
- `mwp`: Mean wave period
