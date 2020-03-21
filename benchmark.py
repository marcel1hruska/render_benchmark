import sys, getopt,os,webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

params=''
executable=''
scene=-1
renderers=['mitsuba']
scene_names=['teapot','sphere']

# parse arguments
try:
    opts,args = getopt.getopt(sys.argv[1:],"hr:e:s:",["help","renderer=","exec=","scene="])
except getopt.GetoptError:
    print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_number>]')
    sys.exit(2)
for opt, arg in opts:
    # help option
    if opt == '-h':
        print('usage: benchmark.py -r {mitsuba} -e <path_to_executable> [-s <scene_number>]')
        sys.exit()
    # scene option
    elif opt in ("-s","--scene"):
        try:
            scene = int(arg)
        except ValueError:
            print('Scene must be a number from 0 to',len(scene_names)-1 )
            sys.exit(2)
        if scene > len(scene_names)-1:
            print('Scene must be a number from 0 to',len(scene_names)-1 )
            sys.exit(2)
    # renderer param
    elif opt in ("-r", "--renderer"):
        # check for supported
        if arg in renderers:
            path = Path(arg + '.conf')
            # check whether the config is there
            if path.is_file():
                f = open(path)
                params = f.read()
            else:
                print('Configuration file ', path, ' for ',arg , ' is missing')
                sys.exit(2)
        # unsupported choice, error
        else:
            print('Incorrect renderer. Supported options are:', renderers)
            sys.exit(2)
    # executable param
    elif opt in ("-e","--exec"):
        if Path(arg).is_file():
            executable=arg
        else:
            print("Path to executable", arg, "does not exist")
            sys.exit(2)
# check for mandatory
if executable == '':
    print("Executable is missing")
    sys.exit(2)
if params == '':
    print("Renderer choice is missing")
    sys.exit(2)
# prepare dir for outputs
if not os.path.exists("outputs"):
    os.mkdir("outputs")
# start the benchmark
print("Benchmark started")
i=0
for s in scene_names:
    if scene == -1 or scene == i:
        print("Scene",i,":", s,'\n')
        os.system(executable + " " + params + " data/scene_"+s+"/"+s+".xml" + " -o outputs/" + s + ".exr")
        print('\n')
    i+=1
print("Benchmark ended, visualizing...")
# run http server for jeri
webbrowser.open('http://localhost:8000/jeri/page/results_viewer.html')
f = open("jeri/log.txt", "w")
sto = sys.stderr
sys.stderr = f
try:
    handler = SimpleHTTPRequestHandler
    # make sure the server responds with correct mime type
    handler.extensions_map={
	    '.manifest': 'text/cache-manifest',
	    '.html': 'text/html',
        '.png': 'image/png',
	    '.jpg': 'image/jpg',
	    '.svg':	'image/svg+xml',
	    '.css':	'text/css',
	    '.js':	'application/x-javascript',
	    '': 'application/octet-stream', # Default
    }
    httpd = HTTPServer(('localhost', 8000), handler)
    httpd.serve_forever()
except KeyboardInterrupt:
    httpd.shutdown()
sys.stderr = sto
f.close()
print("Visualization ended")