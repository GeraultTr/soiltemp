from openalea.soiltemp import model
from openalea.soiltemp import standalone as sa
import pandas as pd

def my_config():
    trt = sa.Treatment()
    config = trt(sa.WST_IDs[0], soil=sa.SOIL_IDs[0], water_content=sa.AWCs[0], lai=sa.LAIDs[0])
    return config

def static_config(nb_layers=10,
                    SOIL_ID="SICL", SOIL_NAME="SiltyClay", layer_thickness=10., bulk_density=1.35, soil_organic_C=1.75, soil_water_saturated=0.481, 
                    field_capacity=0.385, permanent_wilting_point=0.228, clay_percentage=50, volumetric_specific_heat=2.39, 
                    rock_percentage=0., sand_percentage=15., silt_percentage=35.,
                    XLAT=46.435, TAMP=10, TAV=7.22,
                    soil_depth=100):
    """
    Docstring pour static_config
    
    :param nb_layers: Number of soil layers
    :param SOIL_ID: Soil ID string
    :param SOIL_NAME: Soil name string
    :param layer_thickness: Layer thickness (cm)
    :param bulk_density: Bulk density (g/cm3)
    :param soil_organic_C: SOC (g[C]/100g[soil])
    :param soil_water_saturated: Soil water saturated (adim)
    :param field_capacity: Field capacity (adim)
    :param permanent_wilting_point: Permanent wilting point (adim)
    :param clay_percentage: Clay (%)
    :param volumetric_specific_heat: Volumetric specific heat of soil (MJ/m3/°C)
    :param rock_percentage: Rock (%)
    :param sand_percentage: Sand (%)
    :param silt_percentage: Silt (%)
    :param XLAT: Latitude (°)
    :param TAMP: Yearly temperature amplitude (°C)
    :param TAV: Yearly temperature average (°C)
    :param soil_depth: Soil depth (cm)
    """
    trt = sa.Treatment()

    soil = soil_config(nb_layers=nb_layers, SOIL_ID=SOIL_ID, SOIL_NAME=SOIL_NAME, layer_thickness=layer_thickness, bulk_density=bulk_density, soil_organic_C=soil_organic_C, soil_water_saturated=soil_water_saturated, 
                field_capacity=field_capacity, permanent_wilting_point=permanent_wilting_point, clay_percentage=clay_percentage, volumetric_specific_heat=volumetric_specific_heat, 
                rock_percentage=rock_percentage, sand_percentage=sand_percentage, silt_percentage=silt_percentage)

    config = dict(trt=trt, weather=None, soil=soil, AWC=None, 
                 LAI=None, XLAT=XLAT, TAMP=TAMP, TAV=TAV, 
                 albedo=None, nb_layers=nb_layers, soil_depth=soil_depth, bulk_density=bulk_density,
                 irrig=None, surfOrgResidue=0., aboveGroundDM=None, mulch=0., soil_id=SOIL_ID)
    
    return config


def daily_config(static_config,
                 DATE=pd.to_datetime("1991-07-01"), T2M=10, TMIN=3.2, TMAX=11.1, RAIN=0., SRAD=5.6, DAYLD=8.81, SUNUP=7.59, SUNDN=16.41, EOAD=1.096, ESP=1.096, LE=0, G=0, SNOW=0,
                 plant_available_water_content=[0.1 for _ in range(10)], LAI=0., albedo=0.11, irrig=0., aboveGroundDM=0.):
    """
    Docstring pour daily_config
    
    :param static_config: soiltemp.standalone.Treatment class instance
    :param DATE: pandas-formated date
    :param T2M: Daily mean temperature (°C)
    :param TMIN: Daily min temperature (°C)
    :param TMAX: Daily max temperature (°C)
    :param RAIN: Daily precipitation (mm/day)
    :param SRAD: Solar radiation (MJ/m2)
    :param DAYLD: Day length (h)
    :param SUNUP: Sunrise (h since midnight)
    :param SUNDN: Sunset (h since midnight)
    :param EOAD: Potential evapotranspiration (mm)
    :param ESP: Potential evaporation (mm)
    :param LE: Latent heat flux, not used by the Campbell model
    :param G: Ground heat flux, not used by the Campbell model
    :param SNOW: Snow cover TODO mm or i/o?
    :param plant_available_water_content: Description
    :param LAI: Leaf Area Index (adim)
    :param albedo: Albedo (adim)
    :param irrig: Irrigation (mm/day)
    :param aboveGroundDM: Aboveground total dry matter (kg DM per ha)
    """
    config_dict = static_config
    config_dict["weather"] = weather_line(DATE=DATE, T2M=T2M, TMIN=TMIN, TMAX=TMAX, RAIN=RAIN, SRAD=SRAD, DAYLD=DAYLD, SUNUP=SUNUP, SUNDN=SUNDN, EOAD=EOAD, ESP=ESP, LE=LE, G=G, SNOW=SNOW)
    config_dict["AWC"] = pd.DataFrame(dict(AWC=plant_available_water_content))["AWC"]
    config_dict["LAI"] = LAI # adim
    config_dict["albedo"] = albedo # adim
    config_dict["irrig"] = irrig # mm per day
    config_dict["aboveGroundDM"] = aboveGroundDM # kg DM per ha

    config = sa.OneTreatment(**config_dict)
    return config


def weather_line(DATE=pd.to_datetime("1991-12-01"), T2M=6.9, TMIN=3.2, TMAX=11.1, RAIN=0.2, SRAD=5.6, DAYLD=8.81, SUNUP=7.59, SUNDN=16.41, EOAD=1.096, ESP=1.096, LE=0, G=0, SNOW=0):
    weather = dict(DATE=[DATE], T2M=[T2M], TMIN=[TMIN], TMAX=[TMAX], RAIN=[RAIN], SRAD=[SRAD], DAYLD=[DAYLD], SUNUP=[SUNUP], SUNDN=[SUNDN], EOAD=[EOAD], ESP=[ESP], LE=[LE], G=[G], SNOW=[SNOW])
    weather_df = pd.DataFrame(weather)
    return weather_df


def soil_config(nb_layers=10, SOIL_ID="SICL", SOIL_NAME="SiltyClay", layer_thickness=3., bulk_density=1.35, soil_organic_C=1.75, soil_water_saturated=0.481, 
                field_capacity=0.385, permanent_wilting_point=0.228, clay_percentage=50, volumetric_specific_heat=2.39, 
                rock_percentage=0., sand_percentage=15., silt_percentage=35.):
    soil_dict = dict()
    soil_dict["SOIL_ID"] = [SOIL_ID for _ in range(nb_layers)]
    soil_dict["SOIL_NAME"] = [SOIL_NAME for _ in range(nb_layers)]
    soil_dict["SLID"] = [k+1 for k in range(nb_layers)]
    soil_dict["SLLT"] = [k*layer_thickness for k in range(nb_layers)]
    soil_dict["SLLB"] = [(k+1)*layer_thickness for k in range(nb_layers)]
    soil_dict["THICK"] = [layer_thickness for _ in range(nb_layers)] # cm
    soil_dict["SLBDM"] = [bulk_density for _ in range(nb_layers)]
    soil_dict["SLOC"] = [soil_organic_C for _ in range(nb_layers)] # g[C]/100g[soil]
    soil_dict["SLSAT"] = [soil_water_saturated for _ in range(nb_layers)]
    soil_dict["SLDUL"] = [field_capacity for _ in range(nb_layers)]
    soil_dict["SLLL"] = [permanent_wilting_point for _ in range(nb_layers)]
    soil_dict["SLCLY"] = [clay_percentage for _ in range(nb_layers)] # %
    soil_dict["SVSE"] = [volumetric_specific_heat for _ in range(nb_layers)] # MJ/m3/°C
    soil_dict["SLROCK"] = [rock_percentage for _ in range(nb_layers)] # %
    soil_dict["SLSAND"] = [sand_percentage for _ in range(nb_layers)] # %
    soil_dict["SLSILT"] = [silt_percentage for _ in range(nb_layers)] # %

    return pd.DataFrame(soil_dict)

if __name__ == "__main__":
    # config = my_config()
    mods = model.Model.models()
    static_config_dict = static_config()

    my_model = mods['PyCampbell']()
    config = daily_config(static_config_dict)
    res, previous_outputs = my_model.run(config=config, nb_steps=1)
    print("first", res)
    for _ in range(1000):
        res, previous_outputs = my_model.run(config=config, nb_steps=1, previous_outputs=previous_outputs)
    print("final", res)