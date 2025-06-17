from openalea.soiltemp.model import SiriusQuality
from openalea.soiltemp import standalone as sa

def test_apsim():
    trt = sa.Treatment()
    config = trt(sa.WST_IDs[0], soil=sa.SOIL_IDs[0], water_content=sa.AWCs[0],lai=sa.LAIDs[0])
    all_data = config.to_dict()

    assert(len(all_data))

    my_model = SiriusQuality()
    res = my_model.run(config=config, nb_steps=10)
    assert(len(res) == 110)
    assert(7.28 < (res[res.Layer==1].TSLD).mean() <7.29)
