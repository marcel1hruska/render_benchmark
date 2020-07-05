from os import listdir, rename
from os.path import isfile, join

from src.constants import OUTPUT_PATH

class normalizer:
    def normalize(self,renderer):
        # workaround for a custom naming convention of the single wavelength EXRs from ART
        if renderer == 'ART':
            for file in listdir(OUTPUT_PATH):
                if "polarizing_spheres" in file:
                    new_file = file.replace('.550nm','')
                    rename(OUTPUT_PATH+"/"+file,OUTPUT_PATH+"/"+new_file)