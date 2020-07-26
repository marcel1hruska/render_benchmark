import sys,getopt
from pathlib import Path
import json

class arg_parser:
    log=False
    visualize=False
    executable=''
    renderer=''
    scene=''
    case=''

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
            if 'case' in settings:
                self.case = settings['case']
        else:
            print('Settings file is missing\n')
            

    def parse_command_line(self,args):
        # parse arguments
        try:
            opts,args = getopt.getopt(args,"hr:e:s:c:lv",["help","renderer=","exec=","scene=","case=","log","visualize"])
        except getopt.GetoptError:
            print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_name>, -c <test_case_name>, -l, -v]\n')
            sys.exit(2)

        for opt, arg in opts:
            # help option
            if opt in ('-h','--help'):
                print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_name>, -c <test_case_name>, -l, -v]\n')
                sys.exit()
            # scene option
            elif opt in ("-s","--scene"):
                self.scene = arg
             # case option
            elif opt in ("-c","--case"):
                self.case = arg
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

    def check(self,renderers):
        self.__check_exec()
        self.__check_renderer(renderers)

    def __check_exec(self):
        if self.executable == '':
            print("Executable is missing\n")
            sys.exit(2)
        if not Path(self.executable).is_file():
            print("Path to executable", self.executable, "does not exist\n")
            sys.exit(2)

    def __check_renderer(self,renderers):
        if self.renderer == '':
            print("Renderer choice is missing\n")
            sys.exit(2)
        # unsupported choice, error
        if not self.renderer in renderers:
            print('Incorrect renderer. Supported options are:', renderers,"\n")
            sys.exit(2)
