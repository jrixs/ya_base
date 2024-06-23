import logging
import uvicorn
import os
from core.logger import LOGGING

port = os.getenv('PORT')

if __name__ == '__main__':
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    # но чтобы не терять возможность использовать дебагер,
    # запустим uvicorn-сервер через python
    pass
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=int(port),
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True,
        # workers=3
    )
