import os 
del os.environ['GDAL_DATA']

import itertools

import rasterio
from rasterio.mask import mask
from rasterio.warp import reproject, calculate_default_transform as cdt, Resampling
from rasterstats import zonal_stats
from geocube.api.core import make_geocube
from shapely.geometry import shape, box
from matplotlib.colors import ListedColormap
from matplotlib import cm
import ee
import geemap
import numpy as np
import pandas as pd
import geopandas as gpd

from sepal_ui import mapping as sm

from scripts import parameter as pm

ee.Initialize()

#transform the raster into a gpd cell grid 
def get_grid(src_rst, max_polygon=0):

    with rasterio.open(src_rst) as src:
        data = src.read(1)

        t = src.transform

        move_x = t[0]
        # t[4] is negative, as raster start upper left 0,0 and goes down
        # later for steps calculation (ymin=...) we use plus instead of minus
        move_y = t[4]

        height = src.height
        width = src.width 

        polygons = []
        indices = list(itertools.product(range(height), range(width)))
        index = 0
        data_flat = data.flatten()
        for y,x in indices:
            if data_flat[index] != np.iinfo(np.int16).min:
                x_min, y_max = t * (x,y)
                x_max = x_min + move_x
                y_min = y_max + move_y
                polygons.append(box(x_min, y_min, x_max, y_max))
            
            index += 1
            
            if (max_polygon != 0) & (len(polygons) > max_polygon):
                break

    return gpd.GeoDataFrame(crs='EPSG:4236', geometry=polygons)

def gdf_zonal_stats(init_gdf, rst):
    
    gdf = init_gdf.copy()
    gdf = gdf.join(
        pd.DataFrame(
            zonal_stats(
                vectors=gdf['geometry'], 
                raster=rst, 
                all_touched=True, 
                categorical=True
            )
        ),
        how='left'
    )
    
    return gdf

def fraction_raster(init_gdf, value, template_rst, out_rst):
    
    gdf = init_gdf.copy()
    gdf[f'{value}%'] = gdf[value]/gdf.sum(axis=1)*100
    
    with rasterio.open(template_rst) as src:
        gt = src.transform
        resX = gt[0]
        resY = -gt[4]
        
    cube = make_geocube(
        gdf,
        measurements=[f'{value}%'],
        resolution=(resX, resY),
    )
    
    cube[f'{value}%'].rio.to_raster(out_rst)
    
    return 

def align_raster(src_rst, template_rst, out_rst):
    
    # get template crs and transform 
    with rasterio.open(template_rst) as tplt, rasterio.open(src_rst) as src:      
        
        kwargs = src.meta.copy()
        kwargs.update(
            driver = 'GTiff',
            height = tplt.height,
            width = tplt.width,
            transform = tplt.transform,
            compress='lzw'
        )
        
        #destination
        with rasterio.open(out_rst, 'w', **kwargs) as dst:
            for i in range(1, dst.count+1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=tplt.transform,
                    dst_crs=tplt.crs,
                    resampling=Resampling.bilinear
                ) 
    return


def main():
    # get the countries borders as shapes
    countries = pm.country_list

    shapes = []
    for index, row in countries.iterrows():
        #update_progress(index / (len(countries)-1), 'Countries loaded')
        country = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_CODE', row.GAUL))
        country_json = geemap.ee_to_geojson(country)
        shapes.append(shape(country_json['features'][0]['geometry']))
    
    # cut the map of cropland on the countries
    with rasterio.open(pm.cropland_raster) as src:
        out_image, out_transform = mask(src, shapes, all_touched=True)
    
        out_meta = src.meta.copy()
        out_meta.update(
            driver = 'GTiff',
            height = out_image.shape[1],
            width = out_image.shape[2],
            transform = out_transform,
            compress='lzw'
        )
        
        with rasterio.open(pm.crop_masked, "w", **out_meta) as dest:
            dest.write(out_image)
        
    # get the grid

    # value of max polygone
    # put to 0 to study the full map
    # the 200 first values are placed in the north of kazakstan
    max_polygon = 0
    gdf_grid = get_grid(pm.crop_masked, max_polygon=max_polygon)

    # Create the 2013 map out of the full map
    with rasterio.open(pm.llc_full) as src:
    
        kwargs = src.meta.copy()
        kwargs.update(
            driver = 'GTiff',
            height = src.height,
            width = src.width,
            transform = src.transform,
            compress='lzw',
            count = 1
        )
    
        #24 band in total from 1992 to 2015 so 2013 is 22 ( /!\ indexed from 1)
        data = src.read(22)

        with rasterio.open(pm.llc_2013_raster, 'w', **kwargs) as dst:
            dst.write(data, indexes=1)
            
    # create the ecozones map
    gdf_zonal = gdf_zonal_stats(gdf_grid, pm.llc_2013_raster)

    ecozones = [pm.ecozones[i] for i in pm.ecozones]

    for index, zone in enumerate(ecozones):
    
        if zone in gdf_zonal.columns:
            fraction_raster(gdf_zonal, zone, pm.crop_masked, pm.llc_2013_map.format(zone))
            align_raster(pm.llc_2013_map.format(zone), pm.crop_masked, pm.llc_2013_map_masked.format(zone))
            Map.add_raster(pm.llc_2013_map_masked.format(zone), layer_name=pm.ecozones[zone])
        
    return 

if __name__ == "__main__":
    main()