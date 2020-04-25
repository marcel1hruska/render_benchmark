import sys,getopt
from pathlib import Path
import json

class arg_parser:
    RENDERERS=['mitsuba']
    SCENE_NAMES=['sphere','teapot']
    log=False
    params=''
    executable=''
    renderer=''
    scene=0

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
                self.__set_scene(settings['scene'])
            if 'log' in settings:
                self.log = settings['log']
        else:
            print('Settings file is missing.')
            

    def parse_command_line(self,args):
        # parse arguments
        try:
            opts,args = getopt.getopt(args,"hr:e:s:l",["help","renderer=","exec=","scene=","log"])
        except getopt.GetoptError:
            print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_number>] [-l]')
            sys.exit(2)

        for opt, arg in opts:
            # help option
            if opt in ('-h','--help'):
                print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_number>] [-l]')
                sys.exit()
            # scene option
            elif opt in ("-s","--scene"):
                self.__set_scene(arg)
            # renderer param
            elif opt in ("-r", "--renderer"):
                self.renderer = arg
            # executable param
            elif opt in ("-e","--exec"):
                self.executable = arg
            # log param
            elif opt in ('-l','--log'):
                self.log=True

    def check(self):
        self.__check_exec()
        self.__check_renderer()

    def __set_scene(self,number):
        try:
            self.scene = int(number)
        except ValueError:
            print('Scene must be a number from 1 to',len(self.SCENE_NAMES) )
            sys.exit(2)
        if self.scene > len(self.SCENE_NAMES):
            print('Scene must be a number from 1 to',len(self.SCENE_NAMES) )
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
        # check for supported
        if self.renderer in self.RENDERERS:
            path = Path('data/' + self.renderer + '/configuration.conf')
            # check whether the config is there
            if path.is_file():
                f = open(path)
                self.params = f.read()
            else:
                print('Configuration file', path, 'for',self.renderer , 'is missing')
                sys.exit(2)
        # unsupported choice, error
        else:
            print('Incorrect renderer. Supported options are:', self.RENDERERS)
            sys.exit(2)
