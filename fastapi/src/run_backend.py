import logging
import uvicorn
import os
from core.logger import LOGGING

port = int(os.getenv('PORT'))


if __name__ == '__main__':

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        workers=3
    )
