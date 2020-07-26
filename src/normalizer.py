from os import listdir, rename
from os.path import isfile, join

class normalizer:
    def normalize(self,renderer,path):
        # workaround for a custom naming convention of the single wavelength EXRs from ART
        if renderer == 'ART':
            for file in listdir(path):
                if "polarizing_spheres" in file:
                    new_file = file.replace('.550nm','')
                    rename(path+"/"+file,path+"/"+new_file)