import sys, os
from subprocess import Popen
from shutil import rmtree
from datetime import datetime
import json
from pathlib import Path

from src.arg_parser import arg_parser
from src.visualizer import visualizer
from src.constants import OUTPUT_PATH,TEST_CASES
from src.normalizer import normalizer

def render(args,log_path):
    if log_path != '':
        # prepare render log
        log_file=open(log_path,'w')
        return Popen(args,stdout=log_file)
    return Popen(args)

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
print("Storing results in",OUTPUT_PATH,'\n')

# in case the scene output names require some custom adjustments, call the normalizer
norm = normalizer()

# start the benchmark
print("Benchmark started\n")
for case in TEST_CASES:
    if parser.case == '' or parser.case == case:
        print("Test case",case)

        parser.parse_config(case)
        # for each scene in the test case
        for scene in parser.config['scenes']:
            if parser.scene == '' or parser.scene == scene['name']:
                print('\n')
                print("Scene",scene['name'],'\n')

                # prepare arguments for subprocess
                scene_path = "data/cases/"+case+"/"+parser.renderer+"/"+scene["file"]
                args = [parser.executable, scene_path, '-o', OUTPUT_PATH+'/'+scene["name"]]
                # append scene specific arguments
                for param in scene["args"]:
                    args.append(param)

                # run the renderer
                try:
                    log_path=''
                    if parser.log:
                        log_path=OUTPUT_PATH + '/render-log-' + scene['name'] + '.txt'

                    # render scene and wait for results
                    proc = render(args,log_path)
                    proc.wait()
                    if proc.returncode > 0:
                        print('Rendering failed')
                except KeyboardInterrupt:
                    proc.terminate()
                    print('Rendering stopped')
                    sys.exit()

norm.normalize(parser.renderer)
                
print("Benchmark ended")

if parser.visualize:
    vis = visualizer()
    vis.visualize(OUTPUT_PATH)
