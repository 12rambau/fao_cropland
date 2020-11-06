import os
from pathlib import Path
import pandas as pd 

#######################
##      folders      ##
#######################

def get_result_dir():
    folder = Path(Path.home(), 'fao_cropland_results')
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder)

def get_tmp_dir():
    folder = Path(Path.home(), 'fao_cropland_results','tmp')
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder)

def get_data_dir():
    folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    return folder

#####################
##    variables    ##
#####################
ecozones = {
    10: 'Cropland, rainfed',
    20: 'Cropland, irrigated or post-flooding',
    30: 'Mosaic cropland/natural vegetation'
}

#####################
##   tmp file      ##
#####################
llc_2013_map = os.path.join(get_tmp_dir(), 'LCCS-2013-{}.tif')

#####################
##   output file   ##
#####################
crop_masked = os.path.join(get_result_dir(), 'crop_masked.tif')
llc_2013_map_masked = os.path.join(get_result_dir(), 'LCCS-2013-{}_masked.tif')

#####################
##   input file    ##
#####################
cropland_raster = os.path.join(get_data_dir(),  'spam2010V1r1_global_V_agg_VP_CR_AR_A.tif')
llc_2013_raster = os.path.join(get_data_dir(), 'ESACCI-LC-L4-LCCS-Map-300m-P1Y-2013-v2.0.7.tif')
llc_full = os.path.join(get_data_dir(), 'ESACCI-LC-L4-LCCS-Map-300m-P1Y-1992_2015-v2.0.7.tif')

####################
##  dataframes    ##
####################
country_list = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data',  'countries.csv'), sep=',')