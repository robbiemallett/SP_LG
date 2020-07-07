class config:
    def __init__(self):
        self.met_dir = None
        self.output_dir = None
        self.tmp_dir = None
        self.tracks_dir = None
        self.custom_input_list = None
        self.frequencies = [19e9, 37e9]

    pass

def merge(run_config, machine_config, names):

    for n in names:
        if hasattr(machine_config, n):
            v = getattr(machine_config, n)
            setattr(run_config, n, v)


    return(run_config)