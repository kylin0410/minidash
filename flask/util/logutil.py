# Import build-in or 3rd-party modules
import logging
from logging.handlers import RotatingFileHandler, WatchedFileHandler
import multiprocessing


class ThreadLogger:
    """
    Use it in thread to log messages in your own log file in /tmp.
    """
    def __init__(self,
                 name,
                 log_file,
                 level=logging.DEBUG,
                 mode='a',
                 maxBytes=512000,
                 backupCount=4):
        # Initialize members.
        formatter = "%(asctime)s [%(threadName)-10s] %(levelname)s " + \
            "%(filename)-19s %(lineno)d\n    %(message)s\n"
        self.logger = logging.getLogger(name)
        self.logFile = log_file
        self.fileHandler = SafeRotatingFileHandler(self.logFile, mode,
                                                   maxBytes, backupCount)

        # Initialize logger.
        self.fileHandler.setFormatter(logging.Formatter(formatter))
        self.logger.setLevel(level)
        self.logger.addHandler(self.fileHandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def close(self):
        self.logger.removeHandler(self.fileHandler)
        self.fileHandler.flush()
        self.fileHandler.close()


class SafeRotatingFileHandler(RotatingFileHandler, WatchedFileHandler):
    """
    @Summary: Modify RotatingFileHandler for multiple process.
              Log file can auto re-create if it was deleted by testing.
              Rotate log file with multiple process correctly.
    """
    _rollover_lock = multiprocessing.Lock()

    def __init__(self,
                 filename,
                 mode='a',
                 maxBytes=0,
                 backupCount=0,
                 encoding=None,
                 delay=False):
        super().__init__(filename, mode, maxBytes, backupCount, encoding,
                         delay)
        self.dev, self.ino = -1, -1
        self._statstream()

    def emit(self, record):
        """
        Emit a record.
        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            with self._rollover_lock:
                # Auto re-create log file if it was deleted.
                # self.reopenIfNeeded()  # Python 3.6
                if self.shouldRollover(record):
                    if self.shouldRollover(record):
                        self.doRollover()
                logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def shouldRollover(self, record):
        if self._should_rollover():
            # if some other process already did the rollover we might
            # checked log.1, so we reopen the stream and check again on
            # the right log file
            if self.stream:
                self.stream.close()
            self.stream = self._open()
            return self._should_rollover()

        return 0

    def _should_rollover(self):
        if self.maxBytes > 0:
            self.stream.seek(0, 2)
            if self.stream.tell() >= self.maxBytes:
                return True

        return False
