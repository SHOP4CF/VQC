
from VQC.app.otherFunctions import debug_help as dh
from os.path import join

dh.init_fiware_responder(join("tests", "config", "configuration.yaml"))
print(dh.fiware_responder)
