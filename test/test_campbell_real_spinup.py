from openalea.soiltemp.model import PyCampbell
import pickle
import numpy as np
import pandas as pd

if __name__ == "__main__":

    with open('inputs/data_480.pckl', 'rb') as f:
        soil = pickle.load(f)['soil']

    campbell_input_df = pd.read_csv('inputs/daily_grignon_meteo.csv', sep=";")
    campbell_input_df["DATE"] = pd.to_datetime({"year": campbell_input_df["AN"], "month": campbell_input_df["MOIS"], "day": campbell_input_df["JOUR"]}, errors="coerce")

    nb_layers = soil['z2'].shape[1]
    soil_depth = soil['z2'].max() * 100 # m to cm
    layer_thickness = np.unique(soil['z2'] - soil['z1'])[0] * 100 # m to cm
    bulk_density = soil['bulk_density'][0, 0, 0] # g/cm3
    SOC = (soil["MAOC"] + soil["POC"] + soil["DOC"] + soil["microbial_C"]).mean() * 100 # gC/100g of dry soil

    # Silt Loam, Saxon et Rawls 2006 NOTE expected to be different from Hydrus Theta_S and Theta_R, not the same parameters
    permanent_wilting_point = 0.11
    field_capacity=0.31
    soil_water_saturated=0.48

    # TODO soil texture will be passed from the model rather than hardcoded here

    my_model = PyCampbell()

    static_config_dict = my_model.static_config(nb_layers=nb_layers, 
                                                SOIL_ID="SILO",
                                                SOIL_NAME="SiltyLoam",
                                                layer_thickness=layer_thickness,
                                                bulk_density=bulk_density,
                                                soil_depth=soil_depth,
                                                soil_organic_C=SOC,
                                                permanent_wilting_point=permanent_wilting_point,
                                                soil_water_saturated=soil_water_saturated,
                                                field_capacity=field_capacity,
                                                clay_percentage=12.3,
                                                sand_percentage=14.9,
                                                silt_percentage=72.8,
                                                XLAT=48.8442,
                                                TAV=11.3, # Ljutovac 2002 + CLimatik
                                                TAMP=8.0 # based on monthly average (max-min)/2, 12.6 if min/max daily, if hourly will obviously be different TODO sort out
                                                )

    initial_date = pd.to_datetime("1998-01-01")
    current_inputs = campbell_input_df.loc[campbell_input_df["DATE"] == initial_date]
    sunrise = current_inputs["SUNUP"].iat[0]
    sunset = current_inputs["SUNDWN"].iat[0]
    soil_moisture = soil['soil_moisture'].mean(axis=(0, 2)) # cm3/cm3

    config = my_model.daily_config(static_config_dict,
                                   DATE=initial_date,
                                   T2M=current_inputs["TM"].iat[0],
                                   TMIN=current_inputs["TN"].iat[0],
                                   TMAX=current_inputs["TX"].iat[0],
                                   RAIN=current_inputs["RR"].iat[0],
                                   SRAD=current_inputs["RG"].iat[0] / 100, # from J/cm2 to MJ/m2
                                   DAYLD=sunset - sunrise,
                                   SUNUP=sunrise,
                                   SUNDN=sunset,
                                   plant_available_water=(soil_moisture - permanent_wilting_point) / (field_capacity - permanent_wilting_point),
                                   LAI=0.,
                                   albedo=0.12,
                                   irrig=0.,
                                   aboveGroundDM=0.)
    
    res, previous_outputs = my_model.run(config=config, nb_steps=1)
    
    spinup_days = (pd.to_datetime("1998-12-17") - initial_date).days
    print("[INFO] starting temperature model spinup")
    for day in range(spinup_days):
        current_date = initial_date + pd.Timedelta(days=day+1)
        current_inputs = campbell_input_df.loc[campbell_input_df["DATE"] == current_date]
        sunrise = current_inputs["SUNUP"].iat[0]
        sunset = current_inputs["SUNDWN"].iat[0]
        soil_moisture = soil['soil_moisture'].mean(axis=(0, 2)) # cm3/cm3

        config = my_model.daily_config(static_config_dict,
                                    DATE=current_date,
                                    T2M=current_inputs["TM"].iat[0], # °C
                                    TMIN=current_inputs["TN"].iat[0], # °C
                                    TMAX=current_inputs["TX"].iat[0], # °C
                                    RAIN=current_inputs["RR"].iat[0], # mm
                                    SRAD=current_inputs["RG"].iat[0] / 100, # from J/cm2 to MJ/m2
                                    DAYLD=sunset - sunrise, # h
                                    SUNUP=sunrise, # h
                                    SUNDN=sunset, # h
                                    plant_available_water=(soil_moisture - permanent_wilting_point) / (field_capacity - permanent_wilting_point),
                                    LAI=0.,
                                    albedo=0.12,
                                    irrig=0.,
                                    aboveGroundDM=0.)

        res, previous_outputs = my_model.run(config=config, nb_steps=1, previous_outputs=previous_outputs)
    print("[INFO] Finished temperature model spinup")
    print("final", res)