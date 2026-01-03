import pandas as pd
from collections import OrderedDict 
import dataclasses 
import math
import numpy as np
from array import array
from openalea.soiltemp import standalone as sa


# CONSTANT
digit = 6
na=np.nan

class Model:
    """ Define an model interface for soil temperature models"""

    def init(self, config):
        pass

    def step(self, *args, **kwargs):
        pass

    def run(self, config, nb_steps=0):
        pass

    @classmethod
    def models(cls):
        return dict((m.__name__, m) for m in cls.__subclasses__())

#######################################################################################
# APSIM Campbell
from openalea.ApsimCampbell.soiltemperature import init_soiltemperature as apsim_init, model_soiltemperature as apsim_model

class APSIM_Campbell(Model):
    """ APSIM implementation of the Cambell model.
    """

    def run(self, config, nb_steps=0):

        c = config
        soil = c.soil
        weather = c.weather
        
        # Parameters not in the config
        CONSTANT_TEMPdepth:float = 10000.0
        airPressure:float = 1010.0
        canopyHeight:float = 0.057
        instrumentHeight: float = 1.2
        ES = 0.0
        boundaryLayerConductanceSource:str = 'calc'
        netRadiationSource:str = 'calc'
        windSpeed:float = 3.0

        STEFAN_BOLTZMANNconst:float = 0.0000000567
        AIRnode = 0
        SURFACEnode = 1
        TOPSOILnode = 2
        NUM_PHANTOM_NODES = 5
        soilRoughnessHeight = 0.057
        pom:float = 1.3
        
        # New variables
        ps = 2.63
        timestep = 24.0 * 60.0 * 60.0
        latentHeatOfVapourisation=2.465e6
        constantBoundaryLayerConductance = 20.
        numIterationsForBoundaryLayerConductance = 1
        defaultTimeOfMaximumTemperature = 14.0
        defaultInstrumentHeight = 1.2
        bareSoilRoughness = 57
        thermCondPar1=None
        thermCondPar2=None
        thermCondPar3=None
        thermCondPar4=None
        nu = 0.6
        MissingValue = 999999
        soilConstituentNames= ["Rocks", "OrganicMatter", "Sand", "Silt", "Clay", "Water", "Ice", "Air"]
        
        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)

        # Soil parameter

        # soil unit
        soil.SLLB *= 0.01
        soil.THICK *= 10
        soil.SVSE *= 10**6

        soilId = c.soil_id
        soil['SLROCK'] = 0.

        if(soilId == "SICL"):
            sand = 15.0
            silt = 35.
        elif (soilId == "SILO"):
            sand = 30.0
            silt = 60.0
        elif (soilId == "SALO"):
            sand = 60.0
            silt = 30.0
        elif (soilId == "SAND"):
            sand = 85.0
            silt = 10.0

        soil['SLSAND'] = sand
        soil['SLSILT'] = silt

        def to_array(l):
            """ Convert a list to an array, or return the array if already one """
            if isinstance(l, array):
                return l
            else:
                return array('f', l.tolist())

        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=array('f', soil.THICK.to_list())
        BD=to_array(soil.SLBDM)
        SLCARB=to_array(soil.SLOC) 
        CLAY=to_array(soil.SLCLY)
        SLROCK=to_array(soil.SLROCK) 
        SLSILT=to_array(soil.SLSILT) 
        SLSAND=to_array(soil.SLSAND)
        SLOC = to_array(soil.SLOC) # Organic Carbon

        SW=to_array(soil_water)

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 


        # init
        data_init = apsim_init(
            weather_MinT=wi.TMIN,
            weather_MaxT=wi.TMAX,
            weather_MeanT=wi.T2M,
            weather_Tav=c.TAV,
            weather_Amp=c.TAMP,
            weather_AirPressure=airPressure,
            weather_Wind=windSpeed,
            weather_Latitude=c.XLAT,
            weather_Radn=wi.SRAD,
            clock_Today_DayOfYear=wi.DATE.dayofyear,
            microClimate_CanopyHeight=canopyHeight,
            physical_Thickness=THICK,
            physical_BD=BD,
            ps=ps,
            physical_Rocks=SLROCK,
            physical_ParticleSizeSand=SLSAND,
            physical_ParticleSizeSilt=SLSILT,
            physical_ParticleSizeClay=CLAY,
            organic_Carbon=SLCARB,
            waterBalance_SW=SW,

            waterBalance_Eos=wi.EOAD,# Daily Potential Evapotranspiration
            waterBalance_Eo=wi.EOAD, 
            waterBalance_Es=ES, # TODO
            waterBalance_Salb=c.albedo,
            pInitialValues=None, 
            DepthToConstantTemperature=CONSTANT_TEMPdepth,
            timestep=timestep,
            latentHeatOfVapourisation=latentHeatOfVapourisation,
            stefanBoltzmannConstant=STEFAN_BOLTZMANNconst,
            airNode=AIRnode,
            surfaceNode=SURFACEnode,
            topsoilNode=TOPSOILnode,
            numPhantomNodes=NUM_PHANTOM_NODES,
            constantBoundaryLayerConductance=constantBoundaryLayerConductance,
            numIterationsForBoundaryLayerConductance=numIterationsForBoundaryLayerConductance,
            defaultTimeOfMaximumTemperature=defaultTimeOfMaximumTemperature,
            defaultInstrumentHeight=defaultInstrumentHeight,
            bareSoilRoughness=bareSoilRoughness,
            nodeDepth=None,
            thermCondPar1=thermCondPar1,
            thermCondPar2=thermCondPar2,
            thermCondPar3=thermCondPar3,
            thermCondPar4=thermCondPar4,
            pom=pom,
            soilRoughnessHeight=soilRoughnessHeight,
            nu=nu,
            boundarLayerConductanceSource=boundaryLayerConductanceSource,
            netRadiationSource=netRadiationSource,
            MissingValue=MissingValue, 
            soilConstituentNames= soilConstituentNames,
            )
        """
            NLAYR=c.nb_layers,
            CONSTANT_TEMPdepth=CONSTANT_TEMPdepth, 
            T2M=wi.T2M, #
            TMAX=wi.TMAX, #
            TMIN=wi.TMIN, #
            TAV=c.TAV,
            TAMP=c.TAMP,
            XLAT=c.XLAT,
            DOY=wi.DATE.dayofyear, #
            canopyHeight=canopyHeight,
            SALB=c.albedo,
            SRAD=wi.SRAD, #
            ESP=wi.ESP, #
            ES=ES, 
            EOAD=wi.EOAD, #
            instrumentHeight=instrumentHeight, 
            # soil
            THICK=THICK, 
            BD=BD, 
            SLCARB=SLCARB, 
            CLAY=CLAY, 
            SLROCK=SLROCK, 
            SLSILT=SLSILT, 
            SLSAND=SLSAND,
            SW=SW,     
            airPressure=airPressure, 
            boundaryLayerConductanceSource=boundaryLayerConductanceSource,
            netRadiationSource=netRadiationSource, 
            windSpeed=windSpeed)    
        """    
        (InitialValues, 
         doInitialisationStuff, 
         internalTimeStep, 
         timeOfDaySecs, 
         numNodes, 
         numLayers, 
         nodeDepth, 
         thermCondPar1, 
         thermCondPar2, 
         thermCondPar3, 
         thermCondPar4, 
         volSpecHeatSoil, 
         soilTemp, 
         morningSoilTemp, 
         heatStorage, 
         thermalConductance, 
         thermalConductivity, 
         boundaryLayerConductance, 
         newTemperature, airTemperature, 
         maxTempYesterday, minTempYesterday, 
         soilWater, minSoilTemp, maxSoilTemp, aveSoilTemp, 
         aveSoilWater, thickness, bulkDensity, 
         rocks, carbon, sand, silt, clay, 
         soilRoughnessHeight, instrumentHeight, 
         netRadiation, canopyHeight, instrumHeight)= data_init




        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Call the model

            (heatStorage, 
             instrumentHeight, 
             canopyHeight, 
             minSoilTemp, 
             maxSoilTemp, 
             aveSoilTemp, 
             volSpecHeatSoil, 
             soilTemp, 
             morningSoilTemp, 
             newTemperature, 
             thermalConductivity, 
             thermalConductance, 
             boundaryLayerConductance, 
             soilWater, 
             doInitialisationStuff, 
             maxTempYesterday, 
             minTempYesterday, 
             airTemperature, 
             internalTimeStep, 
             timeOfDaySecs, 
             netRadiation, 
             InitialValues) = apsim_model(
                weather_MinT=wi.TMIN,
                weather_MaxT=wi.TMAX,
                weather_MeanT=wi.T2M,
                weather_Tav=c.TAV,
                weather_Amp=c.TAMP,
                weather_AirPressure=airPressure,
                weather_Wind=windSpeed,
                weather_Latitude=c.XLAT,
                weather_Radn=wi.SRAD,
                clock_Today_DayOfYear=wi.DATE.dayofyear,
                microClimate_CanopyHeight=canopyHeight,
                physical_Thickness=THICK,
                physical_BD=BD,
                ps=ps,
                physical_Rocks=SLROCK,
                physical_ParticleSizeSand=SLSAND,
                physical_ParticleSizeSilt=SLSILT,
                physical_ParticleSizeClay=CLAY,
                organic_Carbon=SLOC,
                waterBalance_SW=SW,
                waterBalance_Eos=wi.EOAD,# Daily Potential Evapotranspiration
                waterBalance_Eo=wi.EOAD, 
                waterBalance_Es=ES, # TODO
                waterBalance_Salb=c.albedo,
                InitialValues=InitialValues,
                pInitialValues=None,
                DepthToConstantTemperature=CONSTANT_TEMPdepth,
                timestep=timestep,
                latentHeatOfVapourisation=latentHeatOfVapourisation,
                stefanBoltzmannConstant=STEFAN_BOLTZMANNconst,
                airNode=AIRnode,
                surfaceNode=SURFACEnode,
                topsoilNode=TOPSOILnode,
                numPhantomNodes=NUM_PHANTOM_NODES,
                constantBoundaryLayerConductance=constantBoundaryLayerConductance,
                numIterationsForBoundaryLayerConductance=numIterationsForBoundaryLayerConductance,
                defaultTimeOfMaximumTemperature=defaultTimeOfMaximumTemperature,
                defaultInstrumentHeight=defaultInstrumentHeight,
                bareSoilRoughness=bareSoilRoughness,
                doInitialisationStuff=doInitialisationStuff,
                internalTimeStep=internalTimeStep,
                timeOfDaySecs=timeOfDaySecs,
                numNodes=numNodes,
                numLayers=numLayers,
                nodeDepth=nodeDepth,
                thermCondPar1=thermCondPar1,
                thermCondPar2=thermCondPar2,
                thermCondPar3=thermCondPar3,
                thermCondPar4=thermCondPar4,
                volSpecHeatSoil=volSpecHeatSoil,
                soilTemp=soilTemp,
                morningSoilTemp=morningSoilTemp,
                heatStorage=heatStorage,
                thermalConductance=thermalConductance,
                thermalConductivity=thermalConductivity,
                boundaryLayerConductance=boundaryLayerConductance,
                newTemperature=newTemperature,
                airTemperature=airTemperature,
                maxTempYesterday=maxTempYesterday,
                minTempYesterday=minTempYesterday,
                soilWater=soilWater,
                minSoilTemp=minSoilTemp,
                maxSoilTemp=maxSoilTemp,
                aveSoilTemp=aveSoilTemp,
                aveSoilWater=aveSoilWater,
                thickness=thickness,
                bulkDensity=bulkDensity,
                rocks=rocks,
                carbon=carbon,
                sand=sand,
                pom=pom,
                silt=silt,
                clay=clay,
                soilRoughnessHeight=soilRoughnessHeight,
                instrumentHeight=instrumentHeight,
                netRadiation=wi.SRAD,
                canopyHeight=canopyHeight,
                instrumHeight=instrumHeight,
                nu=nu,
                boundarLayerConductanceSource=boundaryLayerConductanceSource,
                netRadiationSource=netRadiationSource,
                MissingValue=MissingValue,
                soilConstituentNames= soilConstituentNames,
            )
            # TODO : check the output of apsim_model, it seems to be a tuple with the same values as inputs            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(aveSoilTemp[1]); TSLXs.append(maxSoilTemp[1]); TSLNs.append(minSoilTemp[1]); Layers.append(0)
            for j in range(2, c.nb_layers+2):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j-2])); SLLBs.append(int(SLLB[j-2]*100)); TSLDs.append(aveSoilTemp[j]); TSLXs.append(maxSoilTemp[j]); TSLNs.append(minSoilTemp[j]); Layers.append(j-1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df
            
#######################################################################################
# APSIM Campbell
from openalea.Campbell.campbell import init_campbell, model_campbell

class PyCampbell(Model):
    """ APSIM implementation of the Cambell model.
    """

    def run(self, config, nb_steps=0, previous_outputs=None):

        c = config
        soil = c.soil.copy(deep=True)
        weather = c.weather
        
        # Parameters not in the config
        CONSTANT_TEMPdepth:float = 10000.0
        airPressure:float = 1010.0
        canopyHeight:float = 0.057
        instrumentHeight: float = 1.2
        ES = 0.0
        boundaryLayerConductanceSource:str = 'calc'
        netRadiationSource:str = 'calc'
        windSpeed:float = 3.0

        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)

        # Soil parameter

        # soil unit NOTE: DANGEROUS
        soil.SLLB *= 0.01
        soil.THICK *= 10
        soil.SVSE *= 10**6

        soilId = c.soil_id
        soil['SLROCK'] = 0.

        if (not hasattr(soil, "SLSAND")) or (not hasattr(soil, "SLSILT")):
            if(soilId == "SICL"):
                sand = 15.0;
                silt = 35.0;
            elif (soilId == "SILO"):
                sand = 30.0;
                silt = 60.0;
            elif (soilId == "SALO"):
                sand = 60.0;
                silt = 30.0;
            elif (soilId == "SAND"):
                sand = 85.0;
                silt = 10.0;

            soil['SLSAND'] = sand
            soil['SLSILT'] = silt

        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()
        BD=soil.SLBDM.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        # init
        data_init = init_campbell(
            NLAYR=c.nb_layers,
            CONSTANT_TEMPdepth=CONSTANT_TEMPdepth, 
            T2M=wi.T2M, #
            TMAX=wi.TMAX, #
            TMIN=wi.TMIN, #
            TAV=c.TAV,
            TAMP=c.TAMP,
            XLAT=c.XLAT,
            DOY=wi.DATE.dayofyear, #
            canopyHeight=canopyHeight,
            SALB=c.albedo,
            SRAD=wi.SRAD, #
            ESP=wi.ESP, #
            ES=ES, 
            EOAD=wi.EOAD, #
            instrumentHeight=instrumentHeight, 
            # soil
            THICK=THICK, 
            BD=BD, 
            SLCARB=SLCARB, 
            CLAY=CLAY, 
            SLROCK=SLROCK, 
            SLSILT=SLSILT, 
            SLSAND=SLSAND,
            SW=SW,     
            airPressure=airPressure, 
            boundaryLayerConductanceSource=boundaryLayerConductanceSource,
            netRadiationSource=netRadiationSource, 
            windSpeed=windSpeed)        
        
        (thickness, 
        depth, 
        bulkDensity, 
        clay, 
        soilWater, 
        soilTemp, 
        newTemperature, 
        minSoilTemp, 
        maxSoilTemp, 
        aveSoilTemp, 
        morningSoilTemp,
        thermalCondPar1, thermalCondPar2, thermalCondPar3, thermalCondPar4, 
        thermalConductivity, thermalConductance, 
        heatStorage, volSpecHeatSoil, 
        maxTempYesterday,
        minTempYesterday, 
        carbon, rocks, silt, sand, 
        boundaryLayerConductance) = data_init

        if previous_outputs is not None:
            (soilTemp, 
            minSoilTemp, 
            maxSoilTemp, 
            aveSoilTemp,
            morningSoilTemp, 
            newTemperature, 
            maxTempYesterday, 
            minTempYesterday, 
            thermalCondPar1, thermalCondPar2, thermalCondPar3, thermalCondPar4, 
            thermalConductivity, thermalConductance, 
            heatStorage, 
            volSpecHeatSoil, 
            boundaryLayerConductance, 
            thickness, 
            depth, 
            bulkDensity, 
            # soilWater, 
            clay,
            rocks, 
            # carbon, 
            sand, 
            silt
            ) = previous_outputs

        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Call the model
            (soilTemp, 
            minSoilTemp, 
            maxSoilTemp, 
            aveSoilTemp,
            morningSoilTemp, 
            newTemperature, 
            maxTempYesterday, 
            minTempYesterday, 
            thermalCondPar1, thermalCondPar2, thermalCondPar3, thermalCondPar4, 
            thermalConductivity, thermalConductance, 
            heatStorage, 
            volSpecHeatSoil, 
            boundaryLayerConductance, 
            thickness, 
            depth, 
            bulkDensity, 
            soilWater, 
            clay,
            rocks, 
            carbon, 
            sand, 
            silt) = model_campbell(
                # idem from init
                NLAYR=c.nb_layers,
                CONSTANT_TEMPdepth=CONSTANT_TEMPdepth, 
                T2M=wi.T2M, 
                TMAX=wi.TMAX, 
                TMIN=wi.TMIN,
                TAV=c.TAV, 
                TAMP=c.TAMP, 
                XLAT=c.XLAT,
                DOY=wi.DATE.dayofyear,
                canopyHeight=canopyHeight, 
                SALB=c.albedo,
                SRAD=wi.SRAD, 
                ESP=wi.ESP, 
                ES=ES, 
                EOAD=wi.EOAD,
                instrumentHeight=instrumentHeight,

                # soil
                THICK=THICK, 
                BD=BD, 
                SLCARB=SLCARB, 
                CLAY=CLAY, 
                SLROCK=SLROCK, 
                SLSILT=SLSILT, 
                SLSAND=SLSAND,
                SW=SW,     

                # APSIM soil internal variable 
                THICKApsim=thickness, 
                BDApsim=bulkDensity, 
                CLAYApsim=clay, 
                SLROCKApsim=rocks, 
                SLSILTApsim=silt, 
                SLSANDApsim=sand, 
                SWApsim=soilWater,
                DEPTHApsim =depth, 
                SLCARBApsim=carbon, 

                soilTemp=soilTemp, 
                minSoilTemp=minSoilTemp, 
                maxSoilTemp=maxSoilTemp, 
                aveSoilTemp=aveSoilTemp,
                morningSoilTemp=morningSoilTemp, 
                newTemperature=newTemperature, 
                maxTempYesterday=maxTempYesterday, 
                minTempYesterday=minTempYesterday, 
                thermalCondPar1=thermalCondPar1,
                thermalCondPar2=thermalCondPar2, 
                thermalCondPar3=thermalCondPar3, 
                thermalCondPar4=thermalCondPar4, 
                thermalConductivity=thermalConductivity, 
                thermalConductance=thermalConductance, 
                heatStorage=heatStorage, 
                volSpecHeatSoil=volSpecHeatSoil, 
                _boundaryLayerConductance=boundaryLayerConductance, 
                
                # parameters
                airPressure=airPressure, 
                boundaryLayerConductanceSource=boundaryLayerConductanceSource,
                netRadiationSource=netRadiationSource, windSpeed=windSpeed
                ) 
            
            # Not reused, not changing throughout the simulation are commented, or updated by another model
            raw_outputs = (
            soilTemp, 
            minSoilTemp, 
            maxSoilTemp, 
            aveSoilTemp,
            morningSoilTemp, 
            newTemperature, 
            maxTempYesterday, 
            minTempYesterday, 
            thermalCondPar1, thermalCondPar2, thermalCondPar3, thermalCondPar4, 
            thermalConductivity, thermalConductance, 
            heatStorage, 
            volSpecHeatSoil, 
            boundaryLayerConductance, 
            thickness, 
            depth, 
            bulkDensity, 
            # soilWater, 
            clay,
            rocks, 
            # carbon, 
            sand, 
            silt
            )
            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(aveSoilTemp[1]); TSLXs.append(maxSoilTemp[1]); TSLNs.append(minSoilTemp[1]); Layers.append(0)
            for j in range(2, c.nb_layers+2):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j-2])); SLLBs.append(int(SLLB[j-2]*100)); TSLDs.append(aveSoilTemp[j]); TSLXs.append(maxSoilTemp[j]); TSLNs.append(minSoilTemp[j]); Layers.append(j-1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df, raw_outputs
    
    def static_config(self, nb_layers=10,
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

        soil = self.soil_config(nb_layers=nb_layers, SOIL_ID=SOIL_ID, SOIL_NAME=SOIL_NAME, layer_thickness=layer_thickness, bulk_density=bulk_density, soil_organic_C=soil_organic_C, soil_water_saturated=soil_water_saturated, 
                    field_capacity=field_capacity, permanent_wilting_point=permanent_wilting_point, clay_percentage=clay_percentage, volumetric_specific_heat=volumetric_specific_heat, 
                    rock_percentage=rock_percentage, sand_percentage=sand_percentage, silt_percentage=silt_percentage)

        config = dict(trt=trt, weather=None, soil=soil, AWC=None, 
                    LAI=None, XLAT=XLAT, TAMP=TAMP, TAV=TAV, 
                    albedo=None, nb_layers=nb_layers, soil_depth=soil_depth, bulk_density=bulk_density,
                    irrig=None, surfOrgResidue=0., aboveGroundDM=None, mulch=0., soil_id=SOIL_ID)
        
        return config


    def daily_config(self, static_config,
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
        config_dict["weather"] = self.weather_line(DATE=DATE, T2M=T2M, TMIN=TMIN, TMAX=TMAX, RAIN=RAIN, SRAD=SRAD, DAYLD=DAYLD, SUNUP=SUNUP, SUNDN=SUNDN, EOAD=EOAD, ESP=ESP, LE=LE, G=G, SNOW=SNOW)
        config_dict["AWC"] = pd.DataFrame(dict(AWC=plant_available_water_content))["AWC"]
        config_dict["LAI"] = LAI # adim
        config_dict["albedo"] = albedo # adim
        config_dict["irrig"] = irrig # mm per day
        config_dict["aboveGroundDM"] = aboveGroundDM # kg DM per ha

        config = sa.OneTreatment(**config_dict)
        return config


    def weather_line(self, DATE=pd.to_datetime("1991-12-01"), T2M=6.9, TMIN=3.2, TMAX=11.1, RAIN=0.2, SRAD=5.6, DAYLD=8.81, SUNUP=7.59, SUNDN=16.41, EOAD=1.096, ESP=1.096, LE=0, G=0, SNOW=0):
        weather = dict(DATE=[DATE], T2M=[T2M], TMIN=[TMIN], TMAX=[TMAX], RAIN=[RAIN], SRAD=[SRAD], DAYLD=[DAYLD], SUNUP=[SUNUP], SUNDN=[SUNDN], EOAD=[EOAD], ESP=[ESP], LE=[LE], G=[G], SNOW=[SNOW])
        weather_df = pd.DataFrame(weather)
        return weather_df


    def soil_config(self, nb_layers=10, SOIL_ID="SICL", SOIL_NAME="SiltyClay", layer_thickness=3., bulk_density=1.35, soil_organic_C=1.75, soil_water_saturated=0.481, 
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
    
#######################################################################################
# DSSAT EPIC ST
# TODO Debug : only 3 layers are different

from openalea.DSSAT_EPICST_standalone import stemp_epic

class DSSAT_EPIC(Model):
    # TODO : Write the wmapping explicitly

    def run(self, config, nb_steps=0):

        init_fun = stemp_epic.init_stemp_epic
        model_fun = stemp_epic.model_stemp_epic 


        c = config
        soil = c.soil
        weather = c.weather
        
        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)

        # Soil parameter
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()
        BD=soil.SLBDM.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()
        SLDUL = soil.SLDUL.tolist()
        DS = soil.THICK.cumsum().tolist()
        SLLL = soil.SLLL.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        ####################################
        # ADAPTAION to DSSAT

        BD = BD
        DLAYR = THICK
        SW = soil_water.tolist()
        DS = DS
        DUL = SLDUL
        ISWWAT = "Y"
        LL = SLLL
        NL = c.nb_layers
        NLAYR = NL

        BIOMAS = c.above_ground_dry_mass
        DEPIR = c.irrig
        MULCHMASS = c.mulch
        RAIN = wi.RAIN
        SNOW = wi.SNOW
        TAMP = c.TAMP
        TAV = c.TAV
        TAVG = wi.T2M
        TMAX = wi.TMAX
        TMIN = wi.TMIN


        # init
        data_init = init_fun(
            NL=NL, 
            ISWWAT=ISWWAT,
            BD=BD,
            DLAYR=DLAYR, DS=DS, DUL=DUL, LL=LL, NLAYR=NLAYR, TAMP=TAMP, RAIN=RAIN, SW=SW, 
            TAVG=TAVG, TMAX=TMAX, TMIN=TMIN, TAV=TAV, DEPIR=DEPIR, BIOMAS=BIOMAS, MULCHMASS=MULCHMASS, SNOW=SNOW)
        
        (CUMDPT, DSMID, TDL, TMA, NDays, WetDay, X2_PREV, SRFTEMP, ST) = data_init



        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            RAIN = wi.RAIN
            SNOW = wi.SNOW
            TAVG = wi.T2M
            TMAX = wi.TMAX
            TMIN = wi.TMIN

            # Call the model
            results = model_fun(
                TAV=TAV, RAIN=RAIN, DUL=DUL, WetDay=WetDay,
                SRFTEMP=SRFTEMP,NDays=NDays,BIOMAS=BIOMAS,
                NL=NL,
                NLAYR=NLAYR,
                ST=ST,
                SNOW=SNOW,
                TMA=TMA,
                DS=DS,
                ISWWAT=ISWWAT,
                BD=BD,
                TAVG=TAVG,
                LL=LL,
                DEPIR=DEPIR,
                DLAYR=DLAYR,
                TDL=TDL,
                MULCHMASS=MULCHMASS,
                TMAX=TMAX,
                TMIN=TMIN,
                X2_PREV=X2_PREV,
                DSMID=DSMID,
                TAMP=TAMP,
                CUMDPT=CUMDPT,
                SW=SW,
                ) 
            (CUMDPT, DSMID, TDL, TMA, NDays, WetDay, X2_PREV, SRFTEMP, ST) = results

            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(SRFTEMP); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(ST[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df
            

#######################################################################################
# DSSAT

#######################################################################################
from openalea.DSSAT_ST_standalone import stemp

class DSSAT_ST(Model):

    def run(self, config, nb_steps=0):

        init_fun = stemp.init_stemp
        model_fun = stemp.model_stemp


        c = config
        soil = c.soil
        weather = c.weather
        
        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)

        # Soil parameter
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()
        BD=soil.SLBDM.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()
        SLDUL = soil.SLDUL.tolist()
        DS = soil.THICK.cumsum().tolist()
        SLLL = soil.SLLL.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        ####################################
        # ADAPTAION to DSSAT

        BD = BD
        DLAYR = THICK
        SW = SW
        DS = DS
        DUL = SLDUL
        ISWWAT = "Y"
        LL = SLLL
        NL = c.nb_layers
        NLAYR = NL

        MSALB = c.albedo
        XLAT = c.XLAT
        DOY = wi.DATE.dayofyear
        SRAD = wi.SRAD


        BIOMAS = c.above_ground_dry_mass
        DEPIR = c.irrig
        MULCHMASS = c.mulch
        RAIN = wi.RAIN
        SNOW = wi.SNOW
        TAMP = c.TAMP
        TAV = c.TAV
        TAVG = wi.T2M
        TMAX = wi.TMAX
        TMIN = wi.TMIN


        # init
        data_init = init_fun(
            NL=NL, 
            ISWWAT=ISWWAT,
            BD=BD,
            DLAYR=DLAYR, DS=DS, DUL=DUL, LL=LL, NLAYR=NLAYR, 
            MSALB=MSALB, SRAD=SRAD, SW=SW,
            TAVG=TAVG, TMAX=TMAX, XLAT=XLAT, TAV=TAV, TAMP=TAMP, DOY=DOY)
        
        (CUMDPT, DSMID, TDL, TMA, ATOT, SRFTEMP, ST, HDAY) = data_init

        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            RAIN = wi.RAIN
            SNOW = wi.SNOW
            TAVG = wi.T2M
            TMAX = wi.TMAX
            TMIN = wi.TMIN

            DOY = wi.DATE.dayofyear
            SRAD = wi.SRAD

            # Call the model
            results = model_fun(
                NL=NL,
                ISWWAT=ISWWAT,
                BD=BD,
                DLAYR=DLAYR,
                DS=DS,
                DUL=DUL,
                LL=LL,
                NLAYR=NLAYR,
                MSALB=MSALB,
                SRAD=SRAD,
                SW=SW,
                TAVG=TAVG,
                TMAX=TMAX,
                XLAT=XLAT,
                TAV=TAV, 
                TAMP=TAMP,
                CUMDPT=CUMDPT,
                DSMID=DSMID,
                TDL=TDL,
                TMA=TMA,
                ATOT=ATOT,
                SRFTEMP=SRFTEMP,
                ST=ST,
                DOY=DOY,
                HDAY=HDAY
                ) 
            (CUMDPT, DSMID, TDL, TMA, ATOT, SRFTEMP, ST) = results

            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(SRFTEMP); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(ST[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df
            
#######################################################################################
# Simplace

#######################################################################################
from openalea.Simplace_Soil_Temperature.SoilTemperatureComponent import model_soiltemperature as simplace_model
from openalea.Simplace_Soil_Temperature.snowcovercalculator import init_snowcovercalculator as simplace_init_snow
from openalea.Simplace_Soil_Temperature.stmpsimcalculator import init_stmpsimcalculator as simplace_init_stmp


class SIMPLACE_APEX(Model):

    def run(self, config, nb_steps=0):

        init_snow = simplace_init_snow
        init_temp = simplace_init_stmp
        model_fun = simplace_model

        c = config
        soil = c.soil
        weather = c.weather
        
        # variable
        soil_water = (soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)) * soil.THICK
        watContent = soil_water.sum()

        # Soil parameter
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()
        BD=soil.SLBDM.tolist()
        orgMatter = SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SW=soil_water.tolist()
        SLDUL = soil.SLDUL.tolist()
        DS = soil.THICK.cumsum().tolist()
        SLLL = soil.SLLL.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        ####################################
        # ADAPTAION to SIMPLACE

        cABD = cAverageBulkDensity = c.bulk_density
        cAverageGroundTemperature = cAVT = c.TAV
        cCarbonContent = orgMatter[0] 
        cDampingDepth = 6.0
        cFirstDayMeanTemp = c.TAV # tMeanAnnual
        cSoilLayerDepth = (soil.SLLB * 0.01).tolist()

        iAirTemperatureMax = TMAX = wi.TMAX
        iAirTemperatureMin = TMIN = wi.TMIN
        iCropResidues = MULCHMASS = 0. #c.mulch
        iGlobalSolarRadiation = SRAD = wi.SRAD
        iLeafAreaIndex = c.LAI
        iPotentialSoilEvaporation = wi.ESP
        iRadiation = SRAD = wi.SRAD
        iRAIN = RAIN = wi.RAIN
        iSoilWaterContent = watContent * 10
        iTempMax = TMAX
        iTempMin = TMIN
        SnowWaterContent = SNOW = wi.SNOW
        cAlbedo=Albedo = c.albedo

        
        
        '''        
        BD = BD
        DLAYR = THICK
        SW = soil_water
        DS = DS
        DUL = SLDUL
        ISWWAT = "Y"
        LL = SLLL
        NL = c.nb_layers
        NLAYR = NL

        MSALB = c.albedo
        XLAT = c.XLAT
        DOY = wi.DATE.dayofyear
        SRAD = wi.SRAD


        BIOMAS = c.above_ground_dry_mass
        DEPIR = c.irrig
        MULCHMASS = c.mulch
        RAIN = wi.RAIN
        SNOW = wi.SNOW
        TAMP = c.TAMP
        TAV = c.TAV
        TAVG = wi.T2M
        TMAX = wi.TMAX
        TMIN = wi.TMIN
        '''        

        # Parameter 
        cInitialAgeOfSnow = 0
        cSnowIsolationFactorA = 0.47
        cSnowIsolationFactorB = 0.62
        cInitialSnowWaterContent=0.
        
        # init
        iSoilTempArray = []
        data_init = init_snow(
            cCarbonContent=cCarbonContent,
            cInitialAgeOfSnow=cInitialAgeOfSnow,
            cInitialSnowWaterContent=cInitialSnowWaterContent,
            Albedo=Albedo,
            cSnowIsolationFactorA=cSnowIsolationFactorA,
            cSnowIsolationFactorB=cSnowIsolationFactorB,
            iTempMax=iTempMax,
            iTempMin=iTempMin,
            iRadiation=iRadiation,
            iRAIN=iRAIN,
            iCropResidues=iCropResidues,
            iPotentialSoilEvaporation=iPotentialSoilEvaporation,
            iLeafAreaIndex=iLeafAreaIndex,
            )


        (pInternalAlbedo, SnowWaterContent, SoilSurfaceTemperature, AgeOfSnow) = data_init

        data_init = init_temp(
            cSoilLayerDepth=cSoilLayerDepth,
            cFirstDayMeanTemp=cFirstDayMeanTemp,
            cAVT=cAVT,
            cABD=cABD,
            cDampingDepth=cDampingDepth,
            iSoilWaterContent=iSoilWaterContent
        )
        (SoilTempArray, rSoilTempArrayRate, pSoilLayerDepth) = data_init
        
        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            iAirTemperatureMax = TMAX = wi.TMAX
            iAirTemperatureMin = TMIN = wi.TMIN
            iGlobalSolarRadiation = SRAD = wi.SRAD
            iPotentialSoilEvaporation = wi.ESP
            iRadiation = SRAD = wi.SRAD
            iRAIN = RAIN = wi.RAIN
            iTempMax = TMAX
            iTempMin = TMIN
            SnowWaterContent = SNOW = wi.SNOW

            iCropResidues = c.mulch * 0.1

            DOY = wi.DATE.dayofyear

            # Call the model
            
            results = model_fun(
                cCarbonContent=cCarbonContent,
                cAlbedo=cAlbedo,
                cInitialAgeOfSnow=cInitialAgeOfSnow,
                cInitialSnowWaterContent=cInitialSnowWaterContent,
                cSnowIsolationFactorA=cSnowIsolationFactorA,
                cSnowIsolationFactorB=cSnowIsolationFactorB,
                iAirTemperatureMax=iAirTemperatureMax,
                iAirTemperatureMin=iAirTemperatureMin,
                iGlobalSolarRadiation=iGlobalSolarRadiation,
                iRAIN=iRAIN,
                iCropResidues=iCropResidues,
                iPotentialSoilEvaporation=iPotentialSoilEvaporation,
                iLeafAreaIndex=iLeafAreaIndex,
                SoilTempArray=SoilTempArray,
                cSoilLayerDepth=cSoilLayerDepth,
                cFirstDayMeanTemp=cFirstDayMeanTemp,
                cAverageGroundTemperature=cAverageGroundTemperature,
                cAverageBulkDensity=cAverageBulkDensity,
                cDampingDepth=cDampingDepth,
                iSoilWaterContent=iSoilWaterContent,
                pInternalAlbedo=pInternalAlbedo,
                SnowWaterContent=SnowWaterContent,
                SoilSurfaceTemperature=SoilSurfaceTemperature,
                AgeOfSnow=AgeOfSnow,
                rSoilTempArrayRate=rSoilTempArrayRate,
                pSoilLayerDepth=pSoilLayerDepth
            )
            
            (SoilSurfaceTemperature, SnowIsolationIndex, SnowWaterContent, 
             rSnowWaterContentRate, rSoilSurfaceTemperatureRate, rAgeOfSnowRate, 
             AgeOfSnow, SoilTempArray, rSoilTempArrayRate)= results

            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(SoilSurfaceTemperature); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(SoilTempArray[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df

#######################################################################################

from openalea.BiomaSurfacePartonSoilSWATHourlyPartonC.SurfacePartonSoilSWATHourlyPartonCComponent import (
        model_surfacepartonsoilswathourlypartonc as model_surfacepartonsoilswatc, 
        model_surfacetemperatureparton, 
        model_soiltemperatureswat as model_global_parton
)
from openalea.BiomaSurfacePartonSoilSWATHourlyPartonC.soiltemperatureswat import init_soiltemperatureswat as init_parton

class BioMA_Parton_SWAT(Model):
    """ BioMa implementation of the Parton SWAT model.
    """

    def run(self, config, nb_steps=0):


        init_fun = init_parton
        model_fun = model_surfacepartonsoilswatc

        c = config
        soil = c.soil
        weather = c.weather
        
        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        # Parameters not in the config

        LagCoefficient = 0.8

        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)
        VolumetricWaterContent = soil_water.tolist()

        nbLayers=NLAYR=c.nb_layers
        AirTemperatureAnnualAverage = c.TAV
        AboveGroundBiomass = c.above_ground_dry_mass
        Albedo = c.albedo

        AirTemperatureMaximum = wi.TMAX
        AirTemperatureMinimum = wi.TMIN
        GlobalSolarRadiation = wi.SRAD
        WaterEquivalentOfSnowPack = wi.SNOW

        # Soil parameter

        LayerThickness = (soil.THICK / 100.).tolist()
        SoilProfileDepth = c.soil_depth / 100.
        SoilTemperatureByLayers = [15.] * nbLayers
        BulkDensity = BD=soil.SLBDM.tolist()
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()

        """        
        THICK=soil.THICK.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 
        """
        # init
        SoilTemperatureByLayers = init_fun(
            VolumetricWaterContent=VolumetricWaterContent,
            LayerThickness=LayerThickness,
            LagCoefficient=LagCoefficient,
            AirTemperatureAnnualAverage=AirTemperatureAnnualAverage,
            BulkDensity=BulkDensity,
            SoilProfileDepth=SoilProfileDepth
        )        


        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            AirTemperatureMaximum = TMAX = wi.TMAX
            AirTemperatureMinimum = TMIN = wi.TMIN
            GlobalSolarRadiation = SRAD = wi.SRAD

            DayLength = wi.DAYLD

            # Call the model
            
            (SurfaceTemperatureMinimum, 
             SurfaceTemperatureMaximum, 
             SurfaceSoilTemperature) = model_surfacetemperatureparton(
                DayLength=DayLength, 
                AirTemperatureMaximum=AirTemperatureMaximum,
                AirTemperatureMinimum=AirTemperatureMinimum,
                AboveGroundBiomass=AboveGroundBiomass,
                GlobalSolarRadiation=GlobalSolarRadiation,
                )
            SoilTemperatureByLayers = model_global_parton(
                VolumetricWaterContent=VolumetricWaterContent, 
                SurfaceSoilTemperature=SurfaceSoilTemperature, 
                LayerThickness=LayerThickness, 
                LagCoefficient=LagCoefficient, 
                SoilTemperatureByLayers=SoilTemperatureByLayers, 
                AirTemperatureAnnualAverage=AirTemperatureAnnualAverage, 
                BulkDensity=BulkDensity, 
                SoilProfileDepth=SoilProfileDepth
                )

            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(SurfaceSoilTemperature); TSLXs.append(SurfaceTemperatureMaximum); TSLNs.append(SurfaceTemperatureMinimum); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(SoilTemperatureByLayers[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df

#######################################################################################

from openalea.BiomaSurfaceSWATSoilSWATC.SurfaceSWATSoilSWATCComponent import (
        model_surfacetemperatureswat as model_surface_swat, 
        model_soiltemperatureswat as model_soil_temperature_swat, 
    )
from openalea.BiomaSurfaceSWATSoilSWATC.soiltemperatureswat import init_soiltemperatureswat as init_swat

class BioMA_SWAT(Model):
    """ BioMa implementation of the SWAT model.
    """

    def run(self, config, nb_steps=0):


        init_fun = init_swat

        c = config
        soil = c.soil
        weather = c.weather
        
        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        # Parameters not in the config

        LagCoefficient = 0.8

        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)
        VolumetricWaterContent = soil_water.tolist()

        nbLayers=NLAYR=c.nb_layers
        AirTemperatureAnnualAverage = c.TAV
        AboveGroundBiomass = c.above_ground_dry_mass
        #BulkDensity = c.bulk_density
        Albedo = c.albedo

        AirTemperatureMaximum = wi.TMAX
        AirTemperatureMinimum = wi.TMIN
        GlobalSolarRadiation = wi.SRAD
        WaterEquivalentOfSnowPack = wi.SNOW
        DayLength = wi.DAYLD

        # Soil parameter

        LayerThickness = (soil.THICK / 100.).tolist()
        SoilProfileDepth = c.soil_depth / 100.
        SoilTemperatureByLayers = [15.] * nbLayers
        BulkDensity = BD=soil.SLBDM.tolist()
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()

        """        
        THICK=soil.THICK.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 
        """
        # init
        SoilTemperatureByLayers = init_fun(
            VolumetricWaterContent=VolumetricWaterContent,
            LayerThickness=LayerThickness,
            LagCoefficient=LagCoefficient,
            AirTemperatureAnnualAverage=AirTemperatureAnnualAverage,
            BulkDensity=BulkDensity,
            SoilProfileDepth=SoilProfileDepth
        )        
        


        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            AirTemperatureMaximum = TMAX = wi.TMAX
            AirTemperatureMinimum = TMIN = wi.TMIN
            GlobalSolarRadiation = SRAD = wi.SRAD

            DayLength = wi.SUNDN - wi.SUNUP

            # Call the model
            
            SurfaceSoilTemperature = model_surface_swat(
                GlobalSolarRadiation=GlobalSolarRadiation,
                SoilTemperatureByLayers=SoilTemperatureByLayers,
                AirTemperatureMaximum=AirTemperatureMaximum,
                AirTemperatureMinimum=AirTemperatureMinimum,
                Albedo=Albedo,
                AboveGroundBiomass=AboveGroundBiomass,
                WaterEquivalentOfSnowPack=WaterEquivalentOfSnowPack,
                )
            SoilTemperatureByLayers = model_soil_temperature_swat(
                VolumetricWaterContent=VolumetricWaterContent, 
                SurfaceSoilTemperature=SurfaceSoilTemperature, 
                LayerThickness=LayerThickness, 
                LagCoefficient=LagCoefficient, 
                SoilTemperatureByLayers=SoilTemperatureByLayers, 
                AirTemperatureAnnualAverage=AirTemperatureAnnualAverage, 
                BulkDensity=BulkDensity, 
                SoilProfileDepth=SoilProfileDepth
                )

            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(SurfaceSoilTemperature); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(SoilTemperatureByLayers[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df



#######################################################################################
from openalea.Monica_SoilTemp.soiltemperature import (
    model_soiltemperature as monica_model_soiltemperature,
    init_soiltemperature as monica_init)
from openalea.Monica_SoilTemp.nosnowsoilsurfacetemperature import (
    model_nosnowsoilsurfacetemperature as monica_model_nosnowsoilsurfacetemperature
)
from openalea.Monica_SoilTemp.withsnowsoilsurfacetemperature import (
    model_withsnowsoilsurfacetemperature as monica_model_withsnowsoilsurfacetemperature
)

class MONICA(Model):
    """ Monica implementation of the Cambell model.
    """

    def run(self, config, nb_steps=0):

        c = config
        soil = c.soil
        weather = c.weather
        
        # variable
        soil_water = soil.SLLL + c.AWC * (soil.SLDUL - soil.SLLL)



        # Soil parameter
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()
        BD=soil.SLBDM.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SLSAT = soil.SLSAT.tolist()
        SW=soil_water.tolist()
        SLOC = soil.SLOC.tolist() 

        #########################################@
        # Parameters of soil for Monica
        nb_layers = c.nb_layers
        nb_layers_monica = 42
        monica_layer_depth = 5 # each layer has a 5cm depth
        saturatedMonica = [0.]*nb_layers_monica
        bdMonica = [0.]*nb_layers_monica
        carbonMonica = [0.]*nb_layers_monica
        moistureMonica = [0.]*nb_layers_monica

        base_depth = SLLB
        saturated = SLSAT
        org_matter = SLOC

        for i in range(nb_layers_monica):
            for j in range(nb_layers):
                if monica_layer_depth * i < base_depth[j]:
                    saturatedMonica[i] = saturated[j]
                    bdMonica[i] = BD[j]
                    carbonMonica[i] = org_matter[j]
                    moistureMonica[i] = SW[j]
                    break


        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        globrad = wi.SRAD
        soilSurfaceTemperatureBelowSnow = 0.
        hasSnowCover = False
        soilCoverage = 1. - math.exp(-0.5*c.LAI)
        tmax = wi.TMAX
        tmin = wi.TMIN
        baseTemp = 9.5
        dampingFactor = 0.8
        # constant
        densityAir = 1.25
        densityHumus = 1300
        densityWater = 1000
        initialSurfaceTemp = 10
        
        # LayerThickness is in m. 
        # Each layer is 5 cm depth &nd there are 42 layers.
        noOfSoilLayers = nb_layers_monica
        noOfTempLayers = noOfSoilLayers+2 
        noOfTempLayersPlus1 = noOfTempLayers+1
        layerThickness = [monica_layer_depth/100] * noOfTempLayers
        nTau = 0.65
        quartzRawDensity = 2650

        saturation = list(saturatedMonica)
        soilBulkDensity = [_bd*1000 for _bd in bdMonica]
        soilMoistureConst = list(moistureMonica)
        soilOrganicMatter = [cm/57 for cm in carbonMonica]

        specificHeatCapacityAir = 1005
        specificHeatCapacityHumus = 1920
        specificHeatCapacityQuartz = 750
        specificHeatCapacityWater = 4192

        timeStep = 1.0
        
        # init
        data_init = monica_init(
            noOfSoilLayers,
            noOfTempLayers,
            noOfTempLayersPlus1,
            timeStep,
            soilMoistureConst,
            baseTemp,
            initialSurfaceTemp,
            densityAir,
            specificHeatCapacityAir,
            densityHumus,
            specificHeatCapacityHumus,
            densityWater,
            specificHeatCapacityWater,
            quartzRawDensity,
            specificHeatCapacityQuartz,
            nTau,
            layerThickness,
            soilBulkDensity,
            saturation,
            soilOrganicMatter)    
        
        (soilSurfaceTemperature, 
         soilTemperature, V, B, 
         volumeMatrix, volumeMatrixOld, 
         matrixPrimaryDiagonal, matrixSecondaryDiagonal, 
         heatConductivity, heatConductivityMean, 
         heatCapacity, solution, 
         matrixDiagonal, matrixLowerTriangle, heatFlow) = data_init



        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update meteo variables
            tmax = wi.TMAX
            tmin = wi.TMIN
            globrad = wi.SRAD

            # Call the model

            soilSurfaceTemperature = monica_model_nosnowsoilsurfacetemperature(
                tmin, tmax, globrad, soilCoverage, dampingFactor, soilSurfaceTemperature)
            noSnowSoilSurfaceTemperature = soilSurfaceTemperature
            soilSurfaceTemperature = monica_model_withsnowsoilsurfacetemperature(
                noSnowSoilSurfaceTemperature, soilSurfaceTemperatureBelowSnow, hasSnowCover)
            soilTemperature = monica_model_soiltemperature(
                noOfSoilLayers, 
                noOfTempLayers, noOfTempLayersPlus1, 
                soilSurfaceTemperature, timeStep, 
                soilMoistureConst, baseTemp, 
                initialSurfaceTemp, densityAir, specificHeatCapacityAir, 
                densityHumus, specificHeatCapacityHumus, densityWater, 
                specificHeatCapacityWater, quartzRawDensity, specificHeatCapacityQuartz, nTau, 
                layerThickness, soilBulkDensity, saturation, soilOrganicMatter, 
                soilTemperature, V, B, volumeMatrix, volumeMatrixOld, 
                matrixPrimaryDiagonal, matrixSecondaryDiagonal, heatConductivity, 
                heatConductivityMean, heatCapacity, solution, matrixDiagonal, matrixLowerTriangle, heatFlow)


            
            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(soilSurfaceTemperature); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            temp = 0
            prev_top = 0
            prev_i = -1
            layer = 0
            index = [0, 2, 5, 8, 11, 17, 23, 29, 35, 41]
            for i in range(nb_layers_monica):
                temp += soilTemperature[i]
                if i in index:
                    Dates.append(wi.DATE); 
                    SLLTs.append(prev_top); SLLBs.append(5*(i+1));
                    TSLDs.append(temp /(i-prev_i))
                    TSLXs.append(na); TSLNs.append(na);
                    Layers.append(layer)

                    prev_top = 5*(i+1)
                    prev_i = i
                    layer += 1
                    temp = 0
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df


#######################################################################################
from openalea.SQ_Soil_Temperature.calculatesoiltemperature import model_calculatesoiltemperature as sq_soil_temperature, init_calculatesoiltemperature as init_sq
from openalea.SQ_Soil_Temperature.calculatehourlysoiltemperature import model_calculatehourlysoiltemperature as sq_hourly_soil_temperature

class SiriusQuality(Model):
    """ SiiriusQuality implementation of the soil temperature model."""

    def run(self, config, nb_steps=0):


        init_fun = init_sq

        c = config
        soil = c.soil
        weather = c.weather
        
        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        # Parameters not in the config

        lambda_ = 2.454
        a= 0.5
        b= 1.81
        c_= 0.49
        # variable

        nbLayers=NLAYR=c.nb_layers
        meanAnnualAirTemp = c.TAV
        AboveGroundBiomass = c.above_ground_dry_mass
        #BulkDensity = c.bulk_density
        Albedo = c.albedo

        maxTAir = wi.TMAX
        minTAir= wi.TMIN
        meanTAir = wi.T2M
        heatFlux = wi.G

        #AirTemperatureMinimum = wi.TMIN
        #GlobalSolarRadiation = wi.SRAD
        #WaterEquivalentOfSnowPack = wi.SNOW
        
        dayLength = wi.SUNDN - wi.SUNUP

        # Soil parameter

        #LayerThickness = (soil.THICK / 100.).tolist()
        #SoilProfileDepth = c.soil_depth / 100.
        #SoilTemperatureByLayers = [15.] * nbLayers
        #BulkDensity = BD=soil.SLBDM.tolist()
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()

        """        
        THICK=soil.THICK.tolist()
        SLCARB=soil.SLOC.tolist() 
        CLAY=soil.SLCLY.tolist()
        SLROCK=soil.SLROCK.tolist() 
        SLSILT=soil.SLSILT.tolist() 
        SLSAND=soil.SLSAND.tolist()
        SW=soil_water.tolist()

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 
        """
        # init
        deepLayerT = init_fun(
            meanTAir=meanTAir,
            minTAir=minTAir,
            lambda_=lambda_,
            meanAnnualAirTemp=meanAnnualAirTemp,
            maxTAir=maxTAir
        )        
        


        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            maxTAir = wi.TMAX
            minTAir= wi.TMIN
            meanTAir = wi.T2M
            heatFlux = wi.G

            dayLength = wi.SUNDN - wi.SUNUP

            # Call the model
            
            (minTSoil, 
             deepLayerT, 
             maxTSoil) = sq_soil_temperature(
                 meanTAir=meanTAir, minTAir=minTAir, lambda_=lambda_, deepLayerT=deepLayerT, 
                 meanAnnualAirTemp=meanAnnualAirTemp, heatFlux=heatFlux, maxTAir=maxTAir)
            hourlySoilT = sq_hourly_soil_temperature(minTSoil=minTSoil, dayLength=dayLength, b=b, a=a, maxTSoil=maxTSoil, c=c_)
 

            
            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(na); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            Dates.append(wi.DATE); 
            SLLTs.append(SLLT[0]); SLLBs.append(SLLB[0]); TSLDs.append(round((maxTSoil+minTSoil)/2., digit)); TSLXs.append(maxTSoil); TSLNs.append(minTSoil); Layers.append(1)
            for j in range(1, c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(deepLayerT); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df

#######################################################################################
"""
from openalea.Stics_soil_temperature.temp_amp import model_temp_amp as stics_model_temp_amp
from openalea.Stics_soil_temperature.temp_profile import model_temp_profile as stics_model_temp_profile
from openalea.Stics_soil_temperature.layers_temp import model_layers_temp as stics_model_layers_temp
from openalea.Stics_soil_temperature.canopy_temp_avg import model_canopy_temp_avg as stics_model_canopy_temp_avg
from openalea.Stics_soil_temperature.update import model_update as stics_model_update
from openalea.Stics_soil_temperature.temp_profile import init_temp_profile as stics_init_fun


class STICS(Model):
    def run(self, config, nb_steps=0):

        c = config
        soil = c.soil
        weather = c.weather
        
        # variable

        # Soil parameter
        SLLT = soil.SLLT.tolist()
        SLLB = soil.SLLB.tolist()
        THICK=soil.THICK.tolist()

        layer_thick = list(THICK)

        _wi = dict(config.weather.iloc[0])
        WeatherRecord = dataclasses.make_dataclass('WeatherRecord',list(config.weather.columns) )
        wi = WeatherRecord(**_wi) 

        ####################################
        # ADAPTAION to STICS
        max_canopy_temp = wi.TMAX
        max_temp = wi.TMAX
        min_air_temp = wi.TMIN
        min_canopy_temp = wi.TMIN
        min_temp = wi.TMIN
        air_temp_day1 = wi.T2M

        # init
        data_init = stics_init_fun(
            min_air_temp=min_air_temp,
            air_temp_day1=air_temp_day1,
            layer_thick=layer_thick
            )
        
        (temp_amp, prev_temp_profile, prev_canopy_temp) = data_init
        

        # Outputs
        columns = "Date SLLT SLLB TSLD TSLX TSLN Layer".split()
        Dates = []
        SLLTs = []
        SLLBs = []
        TSLDs = []
        TSLXs = []
        TSLNs = []
        Layers = []

        count = 0
        
        for i, _wi in weather.iterrows():
            if count == nb_steps:
                break
            else:
                count += 1

            wi = WeatherRecord(**_wi) 

            # Update some variables
            max_canopy_temp = wi.TMAX
            max_temp = wi.TMAX
            min_air_temp = wi.TMIN
            min_canopy_temp = wi.TMIN
            min_temp = wi.TMIN
            #air_temp_day1 = wi.T2M

            # Call the model
            temp_amp = stics_model_temp_amp(min_temp, max_temp)
            canopy_temp_avg = stics_model_canopy_temp_avg(min_canopy_temp, max_canopy_temp)
            temp_profile = stics_model_temp_profile(temp_amp, prev_temp_profile, prev_canopy_temp, min_air_temp, air_temp_day1, layer_thick)
            layer_temp = stics_model_layers_temp(temp_profile, layer_thick)
            (prev_canopy_temp, prev_temp_profile) = stics_model_update(canopy_temp_avg, temp_profile)

            # Store the outputs
            #date_formattee = wi.DATE.strftime("%Y-%m-%d")
            #Dates.append(wi.DATE.dayofyear); 
            Dates.append(wi.DATE); 
            SLLTs.append(0); SLLBs.append(0); TSLDs.append(na); TSLXs.append(na); TSLNs.append(na); Layers.append(0)
            for j in range(c.nb_layers):
                #Dates.append(wi.DATE.dayofyear); 
                Dates.append(wi.DATE); 
                SLLTs.append(int(SLLT[j])); SLLBs.append(int(SLLB[j])); TSLDs.append(layer_temp[j]); TSLXs.append(na); TSLNs.append(na); Layers.append(j+1)
 
        df = pd.DataFrame( OrderedDict(
                Date = Dates,
                SLLT = SLLTs,
                SLLB = SLLBs,
                TSLD = TSLDs,
                TSLX = TSLXs,
                TSLN = TSLNs,
                Layer =Layers            
                ),
                columns=columns)
        
        return df

"""

"""
# ICASA

DSSAT_ICASA = dict(NL='NLAYER')

class ICASA(Model)
    
    def __init__(self, mapping, name):
        self.name=name
        self.mapping=mapping

    def run(self, config):
        dssat_input = dssasmodel.inputs()
        icasa_input = [DSSAT_ICASA[input] for input in dssat_input]
        outputs = run_my_model()

        dssasmodel.inputs()
        ICASA_DSSAT = dict((v,k) for k, v in DSSAT_ICASA.iteritems())

"""