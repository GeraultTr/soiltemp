from openalea.soiltemp.model import PyCampbell

if __name__ == "__main__":
    my_model = PyCampbell()

    static_config_dict = my_model.static_config()

    config = my_model.daily_config(static_config_dict)
    res, previous_outputs = my_model.run(config=config, nb_steps=1)
    print("first", res)
    for _ in range(1000):
        res, previous_outputs = my_model.run(config=config, nb_steps=1, previous_outputs=previous_outputs)
    print("final", res)