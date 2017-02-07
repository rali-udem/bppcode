import os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
STAND_ALONE = {
          "data" : CURRENT_DIR + "/../data",
          "data-jsrealb" : CURRENT_DIR + "/../data/jsrealb",
          "static" : CURRENT_DIR + "/../static"
               }

def get_conf():
    try :
        d = os.path.dirname(STAND_ALONE["static"])
        if d :
            return STAND_ALONE
    except Exception as e :
        pass
    return APACHE