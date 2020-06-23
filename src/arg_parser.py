import sys,getopt
from pathlib import Path
import json

from src.constants import RENDERERS

class arg_parser:
    log=False
    visualize=False
    executable=''
    renderer=''
    scene=''
    config={}

    def parse_settings(self,file):
        path = Path(file)
        if path.is_file():
            f = open(path)
            settings = json.load(f)
            if 'executable_path' in settings: 
                self.executable = settings['executable_path']
            if 'renderer' in settings:
                self.renderer = settings['renderer']
            if 'scene' in settings:
                self.scene = settings['scene']
            if 'log' in settings:
                self.log = settings['log']
            if 'visualize' in settings:
                self.visualize = settings['visualize']
        else:
            print('Settings file is missing.')
            

    def parse_command_line(self,args):
        # parse arguments
        try:
            opts,args = getopt.getopt(args,"hr:e:s:lv",["help","renderer=","exec=","scene=","log","visualize"])
        except getopt.GetoptError:
            print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_name>] [-l, -v]')
            sys.exit(2)

        for opt, arg in opts:
            # help option
            if opt in ('-h','--help'):
                print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_name>] [-l, -v]')
                sys.exit()
            # scene option
            elif opt in ("-s","--scene"):
                self.scene = arg
            # renderer param
            elif opt in ("-r", "--renderer"):
                self.renderer = arg
            # executable param
            elif opt in ("-e","--exec"):
                self.executable = arg
            # log param
            elif opt in ('-l','--log'):
                self.log=True
            # visualize param
            elif opt in ('-v','visualize'):
                self.visualize=True

    def check(self):
        self.__check_exec()
        self.__check_renderer()
    
    def parse_config(self,scenario):
        path = Path('data/scenarios/'+scenario+'/'+self.renderer+'/configuration.json')
        # check whether the config is there
        if path.is_file():
            f = open(path)
            self.config = json.load(f)
        else:
            print('Configuration for renderer',parser.renderer,'and scenario',scenario,'is missing!')
            sys.exit(2)

    def __check_exec(self):
        if self.executable == '':
            print("Executable is missing")
            sys.exit(2)
        if not Path(self.executable).is_file():
            print("Path to executable", self.executable, "does not exist")
            sys.exit(2)

    def __check_renderer(self):
        if self.renderer == '':
            print("Renderer choice is missing")
            sys.exit(2)
        # unsupported choice, error
        if not self.renderer in RENDERERS:
            print('Incorrect renderer. Supported options are:', RENDERERS)
            sys.exit(2)
