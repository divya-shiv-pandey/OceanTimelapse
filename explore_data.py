import xarray as xr
import numpy as np

# Load the netCDF file
ds = xr.open_dataset('waves_2019-01-01/waves_2019-01-01.nc')

print("Dataset structure:")
print(ds)
print("\n" + "="*50)

print("\nData variables:")
print(ds.data_vars)
print("\n" + "="*50)

print("\nCoordinates:")
print(ds.coords)
print("\n" + "="*50)

print("\nDimensions:")
print(ds.dims)
