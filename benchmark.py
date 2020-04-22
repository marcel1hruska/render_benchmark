import sys, os
from subprocess import Popen
from pathlib import Path
from shutil import rmtree
import json

from src.arg_parser import arg_parser
from src.visualizer import visualizer


OUTPUT = "outputs/"

# initializer param parser
parser = arg_parser()

# if there are some settings, parse them
parser.parse_settings('settings.json')
# if there are some command line arguments, they override the settings
parser.parse_command_line(sys.argv[1:])
# check for mandatory
parser.check()

# prepare dir for outputs
rmtree(OUTPUT)
os.mkdir(OUTPUT)

# prepare render log
log=''
if parser.log:
    if os.path.exists(OUTPUT + '/render-log.txt'):
        os.remove(OUTPUT + '/render-log.txt')
    log=' >> '+ OUTPUT + '/render-log.txt'

# start the benchmark
print("Benchmark started\n")
i=1
for s in parser.SCENE_NAMES:
    if parser.scene == 0 or parser.scene == i:
        print("Scene",i,":", s,'\n')

        scene_path = "data/" + parser.renderer + "/" + "scene_"+s+"/"
        scene_file =  scene_path +s+".xml"
        # run the renderer
        os.system(parser.executable + " " + parser.params + " " + scene_file + " -o " + OUTPUT + s + ".exr" + log)
    i+=1


print("Benchmark ended")

vis = visualizer()
vis.visualize(OUTPUT,parser.renderer)