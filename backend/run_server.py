import uvicorn
import logging
import sys
from main import app
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting SentinelGuard server...")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except TypeError as e:
        logger.critical(f"A TypeError occurred on startup: {e}")
        logger.critical("This is often caused by an incorrect dependency injection. Please check monitor constructors.")
    except Exception as e:
        logger.critical(f"A critical error prevented the server from starting: {e}")
