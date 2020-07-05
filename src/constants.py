import os,datetime

OUTPUT_PATH=str(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir,'outputs-'+str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))))
REFERENCES_PATH=str(os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir,'data','references'))
RENDERERS=['mitsuba2','ART']
TEST_CASES=['reflectance','spectral_accuracy','polarization']