# fao_cropland

create maps for the study of croplands in LMIC

## Data
- crop production value layer called MapSPAM 2010
- LMIC countries in the FAO GAUL description
- [ESA’s CCI-LC maps](https://climate.esa.int/en/projects/land-cover/data/#cci-lc-user-tool) for the years 2013

## output 
- crop_masked.tif : The mapSPAM 2010 masked to LMICs
- LCCS-[year]-[zone_index]-masked.tif: on the crop_masked extent and crs, represent the cell's fraction in the [zone_index] ecozone for the [year] considered. 0% pixels are all masked.

## usage 

on an instance >= `m4`, pull the repository in your sepal environment:
```
git clone https://github.com/12rambau/fao_cropland.git
```

Then add the data folder that I send you in the `fao_cropland` folder

launch the `cropland.ipynb` notebook and run all cells

The full process takes **3h** 

You could also consider using the `cropland.py` file by runing :

```
cd ~
nohup python3 fao_cropland/cropland.py &
```
:warning: this file has very few printing outpu and they are in french




