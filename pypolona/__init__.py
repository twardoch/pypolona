__version__ = "1.1.1"

import os
import logging
from colored import stylize, attr, fg
logging.basicConfig(level=logging.INFO, format='%(levelname)s%(message)s',)
log = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
logging.addLevelName(logging.DEBUG, stylize("# [DEBUG] ", fg("grey_30")))
logging.addLevelName(logging.INFO, '')
logging.addLevelName(logging.WARNING, stylize(
    "# [WARNING] ", fg("dark_orange")))
logging.addLevelName(logging.ERROR, stylize("# [ERROR] ", fg("red")))
logging.addLevelName(logging.CRITICAL, stylize(
    "# [FAILURE] ", fg("light_red") + attr("bold")))
logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, stylize(
    "# [SUCCESS] ", fg("green") + attr("bold")))
setattr(log, 'success', lambda message, *
        args: log._log(logging.SUCCESS, message, args))
