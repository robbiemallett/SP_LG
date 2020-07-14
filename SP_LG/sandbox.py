from snow_models.snowpack.pro_utils import *
import types

config = types.SimpleNamespace()
my_track = types.SimpleNamespace()

my_track.track_no = 500
config.tmp_dir = '/home/robbie/Dropbox/SP_LG/SP_LG/snow_models/snowpack/tmp'

x = read_pro(my_track, config)

print(x[-1])