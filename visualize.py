from src.visualizer import visualizer
from src.configurator import configurator
import getopt,os,sys
from pathlib import Path

try:
    opts,args = getopt.getopt(sys.argv[1:],"ho:",["help","outputs="])
except getopt.GetoptError:
    print('usage: visualize.py -o <output_folder_name>')
    sys.exit(2)

outputs=''
for opt, arg in opts:
    # help option
    if opt in ('-h','--help'):
        print('usage: visualize.py -o <output_folder_name>')
        sys.exit()
    elif opt in ('-o','--outputs'):
        outputs=os.path.join(os.path.dirname(os.path.realpath(__file__)),arg)
        if not Path(outputs).exists():
            print('Specified outputs folder',arg,'does not exist')
            sys.exit(2)


if outputs == '':
    with os.scandir(os.path.dirname(os.path.realpath(__file__))) as folder:
        greatest=''
        for file in folder:
            if file.is_dir() and file.name.startswith('outputs-') and file.name[8:] > greatest:
                greatest=file.name[8:]
                outputs=str(file.path)
if outputs == '':
    print('Nothing to visualize')
    sys.exit()

# change cwd to this file's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

config=configurator()
config.configurate('data/configuration.json','',outputs)

vis = visualizer()
vis.visualize(outputs)