from pathlib import Path
import sys, os, json

class case_info:
    def __init__(self):
        self.name=''
        self.scenes=[]

class scene_info:
    def __init__(self):
        self.name=''
        self.file=''
        self.params=[]
        self.channels=[]

class configurator:
    cases=[]
    global_params=[]
    format=''
    renderers=[]
    output_path=''
    output_nam=''

    def configurate(self,file,current_renderer,output_path):
        self.output_path = output_path
        self.output_name = os.path.basename(os.path.normpath(output_path))

        path = Path(file)
        if path.is_file():
            f = open(path)
            config = json.load(f)

            if current_renderer != '':
                # configure renderer format and params
                if 'renderers' in config:
                    for renderer in config['renderers']:
                        if 'name' in renderer:
                            self.renderers.append(renderer['name'])
                            if renderer['name'] == current_renderer:
                                if 'format' in renderer:
                                    self.format=renderer['format']
                                else:
                                    self.__wrong_config(renderer['name'],'format missing')
                                if 'global_params' in renderer:
                                    self.global_params=renderer['global_params']
                        else:
                            self.__wrong_config('Renderer name missing')
                else:
                    self.__wrong_config('No renderers found')


            if 'root' in config:
                # find all cases
                for case in config['root']:

                    # check case name
                    new_case=case_info()
                    if 'case' in case:
                        new_case.name=case['case']
                    else:
                        print('Case name missing')
                        continue
                    
                    if 'scenes' in case:
                        # for all scenes
                        for scene in case['scenes']:
                            # create new scene
                            new_scene=scene_info()

                            # add name - only warning
                            if 'name' in scene:
                                new_scene.name = scene['name']
                            else:
                                print('Missing scene name in',case_name)
                                continue

                            # add file
                            if 'file' in scene:
                                new_scene.file = scene['file']+'.'+self.format
                            else:
                                new_scene.file = new_scene.name+'.'+self.format

                            # add channels
                            if 'channels' in scene:
                                new_scene.channels = scene['channels']
                            
                            renderer_found=False
                            if current_renderer != '':
                                # check renderers for the scene
                                if 'renderers' in scene:
                                    for renderer in scene['renderers']:
                                        # check name of the renderer
                                        if 'name' in renderer:
                                            # the renderer is wanted and it has params
                                            if current_renderer == renderer['name']:
                                                renderer_found=True
                                                if 'params' in renderer:
                                                    new_scene.params=renderer['params']
                                                break
                                        else:
                                            print('Name of renderer missing in scene',new_scene.name)
                                else:
                                    print('No renderers defined for scene',new_scene.name)
                            
                            # add scene to case
                            # either the renderer was found or we do not care about it
                            if renderer_found or current_renderer == '':
                                new_case.scenes.append(new_scene)
                    else:
                        print('Scenes missing for',case_name)
                        continue
                    
                    # add case
                    if len(new_case.scenes) > 0:
                        self.cases.append(new_case)
            else:
                self.__wrong_config('Root missing in configuration file')
        else:
            self.__wrong_config('Configuration file missing')

        self.__create_jeri_data()

    def __wrong_config(self, text):
        print(text+'\n')
        sys.exit(2)

    def __create_jeri_data(self):
        # initialize
        data = {
            'title': 'root',
            'children': []
        }

        # create contents
        for case in self.cases:
            case_child = {
                'title': 'Test Case ' + self.snake_case_to_pretty(case.name),
                'children': []
            }

            for scene in case.scenes:
                output_images = {}
                if len(scene.channels) == 0:
                    output_images = self.__create_image_data('../../'+self.output_name+'/'+scene.name+'.exr','Output')
                else:
                    output_images = {
                        'title': 'Output',
                        'children': []
                    }
                    for channel in scene.channels:
                        output_images['children'].append(
                            self.__create_image_data('../../'+self.output_name+'/'+scene.name+'.'+channel+'.exr',channel)
                        )

                reference_images = {}
                if len(scene.channels) == 0:
                    reference_images = self.__create_image_data('../../data/references/'+scene.name+'.exr','Reference')
                else:
                    reference_images = {
                        'title': 'Reference',
                        'children': []
                    }
                    for channel in scene.channels:
                        reference_images['children'].append(
                            self.__create_image_data('../../data/references/'+scene.name+'.'+channel+'.exr',channel)
                        )
                
                ssim_images = {}
                if len(scene.channels) == 0:
                    ssim_images = self.__create_difference_image_data('SSIM',scene.name,'SSIM')
                else:
                    ssim_images = {
                        'title': 'SSIM',
                        'children': []
                    }
                    for channel in scene.channels:
                        ssim_images['children'].append(
                            self.__create_difference_image_data('SSIM',scene.name+'.'+channel,channel)
                        )

                l1_images = {}
                if len(scene.channels) == 0:
                    l1_images = self.__create_difference_image_data('L1',scene.name,'L1')
                else:
                    l1_images = {
                        'title': 'L1',
                        'children': []
                    }
                    for channel in scene.channels:
                        l1_images['children'].append(
                            self.__create_difference_image_data('L1',scene.name+'.'+channel,channel)
                        )

                case_child['children'].append({
                    'title': 'Scene ' + self.snake_case_to_pretty(scene.name),
                    'children': [
                            output_images,
                            reference_images,
                            ssim_images,
                            l1_images,
                    ]
                })

            data['children'].append(case_child)

        # write the json
        file=open(self.output_path+'/jeri_data.json','w')
        file.write(json.dumps(data))
        file.close()

    def __create_image_data(self, path, title):
        return { 
            'title' : title,
            'image' : path
        }

    def __create_difference_image_data(self, function, scene, title):
        return { 
            'title': title,
            'tonemapGroup': 'other',
            'lossMap': {
                'function': function,
                'imageA': '../../'+self.output_name+'/'+scene+'.exr',
                'imageB': '../../data/references/'+scene+'.exr'
            }
        }

    def snake_case_to_pretty(self,text):
        return " ".join(w.upper() if w == 'ggx' else w.capitalize() for w in text.split('_'))
