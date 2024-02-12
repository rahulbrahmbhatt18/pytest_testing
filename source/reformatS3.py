
from reformatFunctions import *


####################
# Description
# Program is designed to sort users data into format that can be easily used
# 
# Please look at the code and suggest how you would test the code and list points for
# each function on what should test for
####################

####################
#  MAIN PROGRAM    #
####################

if __name__ == "__main__":

    ## SETTINGS AND PATHS ##
    # location for output files to be written (script will create if doesn't exist)
    TARGET_DIR = os.path.expanduser("output")
    # location of the download
    s3_dir = os.path.expanduser("input")

    ##################
    ## Main program ##
    ##################

    # copy files from S3 export directory to TARGET_DIR and format nicely
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    listo = qc_s3_download_create_formatted(
        s3_dir,
        result_dir=None,
        target_dir=TARGET_DIR,
        subject_list=None,
        skip_copy=False,
        verbose=False
    )
