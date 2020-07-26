from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser,sys,os

class visualizer:
    def visualize(self,output_path):
        # check paths
        references_path=str(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir,'data','references'))
        if os.path.exists(output_path) and os.path.exists(references_path):
            print('Data files correct\n')
        else:
            print('Data files incorrect, aborting visualization\n')
            sys.exit(2)

        output_name=os.path.basename(os.path.normpath(output_path))
        print("Visualizing "+ output_name+"...")
        print("URL: http://localhost:8000/jeri/page/results_viewer.html?outputs="+output_name)

        # open jeri website
        webbrowser.open('http://localhost:8000/jeri/page/results_viewer.html?outputs='+output_name)

        # prepare jeri log
        f = open(output_path + "/jeri-log.txt", "w")
        sto = sys.stderr
        sys.stderr = f

        try:
            # instance of custom handler
            handler = CustomHTTPRequestHandler
            # make sure all files have appropriate extensions
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
            # run the server
            server = HTTPServer(('localhost', 8000), handler)
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()

        sys.stderr = sto
        f.close()
        
        print("Visualization ended")

# custom handler provides extra headers to disable caching
class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_no_cache_headers()
        SimpleHTTPRequestHandler.end_headers(self)

    def send_no_cache_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
