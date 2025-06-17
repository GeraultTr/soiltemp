from openalea.soiltemp.model import APSIM_Campbell
from openalea.soiltemp import standalone as sa

def test_apsim():
    trt = sa.Treatment()
    config = trt(sa.WST_IDs[0], soil=sa.SOIL_IDs[0], water_content=sa.AWCs[0],lai=sa.LAIDs[0])
    all_data = config.to_dict()

    assert(len(all_data))

    my_model = APSIM_Campbell()
    res = my_model.run(config=config, nb_steps=10)
