from split_settings.tools import include
import sys

import logging

logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s - %(levelname)s - %(message)s",  
    handlers=[
        logging.StreamHandler(sys.stdout)  
    ]
)

try:
    include(
    'components/general.py',
    'components/database.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/templates.py',
    'components/logging.py',
    ) 
except OSError as error:
    logging.error(f'Include Error:{error}')
    sys.exit(1)
