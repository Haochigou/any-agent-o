__author__ = r"oiknow12@gmail.com"
__version__ = r"0.1.0"

import multiprocessing
import argparse

from agent.infra.log.local import getLogger
from agent.api import create_fastapi
from agent import domain

app = create_fastapi()

logger = getLogger("chat")

domain.init_global_resource()


if __name__ == r"__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--host", dest="host", default="0.0.0.0", help="system host")
    
    parser.add_argument("-p", "--port", dest="port", default=8080, help="run on the given port", type=int)

    parser.add_argument("-d", "--debug", dest="debug", default=True, help="run in debug mode", type=bool)
    
    parser.add_argument("-np", "--num_process", dest="num_process", default=2, type=int)

    parser.add_argument(
        "--dialog-history-path", "--history",
        dest="chat_history_path", default="./chat-history", type=str,
        help="path to save the history dialog",
    )

    terminal_args = parser.parse_args()
    
    logger.error(f"The framework is to start {terminal_args.num_process} workers using the gunicorn, version {__version__} at {terminal_args.host}:{terminal_args.port}")
    
    import uvicorn
    uvicorn.run("agent.main:app", host=terminal_args.host, port=terminal_args.port, workers=terminal_args.num_process)