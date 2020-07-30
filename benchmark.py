import sys, os
from subprocess import Popen
from datetime import datetime

from src.arg_parser import arg_parser
from src.visualizer import visualizer
from src.normalizer import normalizer
from src.configurator import configurator

# helper method for two different types of running a subprocess
def render(args,log_path):
    if log_path != '':
        # prepare render log
        log_file=open(log_path,'w')
        return Popen(args,stdout=log_file)
    return Popen(args)

# change cwd to this file's directory
cwd=os.path.dirname(os.path.realpath(__file__))
os.chdir(cwd)

# initializer param parser
parser = arg_parser()
# if there are some settings, parse them
parser.parse_settings('settings.json')
# if there are some command line arguments, they override the settings
parser.parse_command_line(sys.argv[1:])

# prepare dir for outputs
output_path = str(os.path.join(cwd,'outputs-'+str(datetime.now().strftime("%Y%m%d-%H%M%S"))))
os.mkdir(output_path)
print("Storing results in",output_path,'\n')

# parse the configuration file
config = configurator()
config.configurate('data/configuration.json',parser.renderer,output_path)

# check for mandatory
parser.check(config.renderers)

# prepare name normalizer
norm = normalizer()

total=0
passed=0

# start the benchmark
print("Benchmark started")

# for each test case scenario
for case in config.cases:
    if parser.case == '' or parser.case == case.name:
        if parser.case != '':
            print(config.snake_case_to_pretty(case.name),"only\n")

        print("Test case",config.snake_case_to_pretty(case.name),'\n')

        # for each scene in the test case
        for scene in case.scenes:
            if parser.scene == '' or parser.scene == scene.name:
                total+=1
                print("Scene",config.snake_case_to_pretty(scene.name),'\n')

                # prepare arguments for subprocess
                scene_path = str(os.path.join('data','cases',case.name,parser.renderer,scene.file))
                args = [parser.executable, scene_path, '-o', output_path+'/'+scene.name]
                # append global renderer specific arguments
                for param in config.global_params:
                    args.append(param)
                # append scene specific arguments
                for param in scene.params:
                    args.append(param)

                # run the renderer
                try:
                    log_path=''
                    if parser.log:
                        log_path=output_path + '/render-log-' + scene.name + '.txt'

                    # render scene and wait for results
                    proc = render(args,log_path)
                    proc.wait()
                    if proc.returncode > 0:
                        print('Rendering failed')
                    else:
                        passed+=1
                except KeyboardInterrupt:
                    proc.terminate()
                    print('Benchmark stopped')
                    sys.exit()
                print('\n')

# in case the scene output names require some custom adjustments, call the normalizer
norm.normalize(parser.renderer,output_path)
                
print("Benchmark ended")
print(passed,"out of",total,"test scenes rendered successfully\n")
if parser.visualize:
    vis = visualizer()
    vis.visualize(output_path)
