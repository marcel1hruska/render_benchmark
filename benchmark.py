import sys, os
from subprocess import Popen, PIPE
from shutil import rmtree
from datetime import datetime
import json
from pathlib import Path

from src.arg_parser import arg_parser
from src.visualizer import visualizer
from src.constants import OUTPUT_PATH,SCENARIO_NAMES

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
was_terminated=False
for scenario in SCENARIO_NAMES:
    print("Scenario",scenario)

    parser.parse_config(scenario)
    # for each scene in scenario
    for scene in parser.config['scenes']:
        if parser.scene == '' or parser.scene == scene['name']:
            print('\n')
            print("Scene",scene['name'],'\n')

            # prepare arguments for subprocess
            scene_path = "data/scenarios/"+scenario+"/"+parser.renderer+"/"+scene["file"]
            args = [parser.executable, scene_path, '-o', OUTPUT_PATH+'/'+scene["name"]]
            # append scene specific arguments
            for param in scene["args"]:
                args.append(param)

            # run the renderer
            try:
                # prepare render log
                if parser.log:
                    log=open(OUTPUT_PATH + '/render-log-' + scene['name'] + '.txt','x')
                    proc = Popen(args,stdout=log)
                else:
                    proc = Popen(args)
                proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                was_terminated=True
                print('Rendering stopped')
print("Benchmark ended")

if not was_terminated and parser.visualize:
    vis = visualizer()
    vis.visualize(OUTPUT_PATH)
