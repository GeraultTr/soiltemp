from openalea.soiltemp import model
from openalea.soiltemp import standalone as sa

def my_config():
    trt = sa.Treatment()
    config = trt(sa.WST_IDs[0], soil=sa.SOIL_IDs[0], water_content=sa.AWCs[0],lai=sa.LAIDs[0])
    return config

def test_apsim():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['APSIM_Campbell']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_campbell():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['PyCampbell']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_dssat_epic():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['DSSAT_EPIC']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_dssat_st():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['DSSAT_ST']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_simplace_apex():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['SIMPLACE_APEX']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_bioma_parton_swat():

    mods = model.Model.models()
    config = my_config()

    my_model = mods['BioMA_Parton_SWAT']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_bioma_swat():

    mods = model.Model.models()
    config = my_config()

    my_model = mods['BioMA_SWAT']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_monica():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['MONICA']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)

def test_sirius_quality():
    mods = model.Model.models()
    config = my_config()

    my_model = mods['SiriusQuality']()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)
