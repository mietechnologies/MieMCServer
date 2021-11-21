from util import logger

if __name__ == "__main__":
	# logger.handleUncaughtException(RuntimeError("Test"))
    raise RuntimeError("Test unhandled")