import sys, os,webbrowser
from subprocess import Popen
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from shutil import copyfile
import json

from arg_parser import arg_parser


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
if not os.path.exists(OUTPUT):
    os.mkdir(OUTPUT)

# prepare render log
log=''
if parser.log:
    if os.path.exists(OUTPUT + '/render-log.txt'):
        os.remove(OUTPUT + '/render-log.txt')
    log=' >> '+ OUTPUT + '/render-log.txt'

# start the benchmark
print("Benchmark started\n")
i=0
for s in parser.SCENE_NAMES:
    if parser.scene == -1 or parser.scene == i:
        print("Scene",i,":", s,'\n')

        scene_path = "data/" + parser.renderer + "/" + "scene_"+s+"/"
        scene_file =  scene_path +s+".xml"
        # run the renderer
        os.system(parser.executable + " " + parser.params + " " + scene_file + " -o " + OUTPUT + s + ".exr" + log)
    i+=1


print("Benchmark ended, visualizing...")
# run http server for jeri
webbrowser.open('http://localhost:8000/jeri/page/results_viewer.html?renderer=' + parser.renderer)
f = open(OUTPUT + "/jeri-log.txt", "w")
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