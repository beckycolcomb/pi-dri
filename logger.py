import logging, sys
from consts import ENV

if ENV == "dev":
    logging.basicConfig(
        level=logging.DEBUG, 
    )
else:
    logging.basicConfig(
        level=logging.WARNING, 
    )
logger = logging.getLogger("controller-pi")
stdout_streamhandler = logging.StreamHandler(sys.stdout)
logger.addHandler(stdout_streamhandler)