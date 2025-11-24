import xarray as xr
import numpy as np

# Load the netCDF file
ds = xr.open_dataset('waves_2019-01-01/waves_2019-01-01.nc')
print("structure:")
print(ds)

point_data = ds.sel(longitude=0.0, latitude=0.0, method='nearest')

print(f"Long: {point_data.longitude.values}")
print(f"Lat: {point_data.latitude.values}")
print()

# get all hmax values for this location for the day
hmax_values = point_data['hmax'].values

print(f"No. of time steps: {len(hmax_values)}")

for i, val in enumerate(hmax_values):
    time = point_data['time'].values[i]
    print(f"  {time}: {val:.3f} m")

# find max hmax val
max_hmax = np.nanmax(hmax_values)

print()
print(f"   Hmax:     {max_hmax:.3f} meters")
print()
