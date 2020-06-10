import sys, os
from subprocess import Popen, PIPE
from shutil import rmtree
from datetime import datetime

from src.arg_parser import arg_parser
from src.visualizer import visualizer
from src.constants import OUTPUT_PATH,SCENE_NAMES
# initializer param parser
parser = arg_parser()

# if there are some settings, parse them
parser.parse_settings('settings.json')
# if there are some command line arguments, they override the settings
parser.parse_command_line(sys.argv[1:])
# check for mandatory
parser.check()

# prepare dir for outputs
os.mkdir(OUTPUT_PATH)
# start the benchmark
print("Benchmark started\n")
i=1
was_terminated=False
for s in SCENE_NAMES:
    if parser.scene == 0 or parser.scene == i:
        print("Scene",i,":", s,'\n')
        # prepare arguments for subprocess
        scene_path = "data/" + parser.renderer + "/" + "scene_"+s+"/"
        scene_file =  scene_path +s+".xml"
        args = [parser.executable, scene_file, '-o', OUTPUT_PATH + '/' + s + '.exr']
        for param in parser.params:
            args.append(param)
        # run the renderer
        try:
            # prepare render log
            if parser.log:
                log=open(OUTPUT_PATH + '/render-log-' + i + '.txt','x')
                proc = Popen(args,stdout=log)
            else:
                proc = Popen(args)
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
            was_terminated=True
            print('Rendering stopped')
    i+=1
print("Benchmark ended")

if not was_terminated and parser.visualize:
    vis = visualizer()
    vis.visualize(OUTPUT_PATH)
