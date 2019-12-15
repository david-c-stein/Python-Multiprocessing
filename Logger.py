#!/usr/bin/env python

import logging
import logging.config
import logging.handlers
import traceback
import time
import os


class SizedTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0, when='h', interval=1, utc=False):
        if maxBytes > 0:
            mode = 'a'
        logging.handlers.TimedRotatingFileHandler.__init__(self, filename, when, interval, backupCount, encoding, delay, utc)
        self.back_count = backupCount
        self.maxBytes = maxBytes

    def shouldRollover(self, record):
        if self.stream == None:
            self.stream = self._open()

        # check rollover by size
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1

        # check rollover by time
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        
        return 0

    def rotate(self, source, dest):
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)


logconfig = {
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '[%(levelname)-4s][%(asctime)-15s][%(processName)-10s][%(filename)-10s][%(funcName)-8s][%(lineno)-3s] : %(message)s'
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '[%(levelname)-4s] : %(message)s'
        }       
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple'
        },
        'file': {
            'class': 'Logger.SizedTimedRotatingFileHandler',
            'filename': 'appLogger.log',
            'mode': 'w',
            'formatter': 'detailed',
            'when': 'S',                # seconds
            'interval': 86400,          # 86400 seconds = 1 day
            'backupCount': 5,
            'maxBytes': 5342880,        # 5Mb
            'encoding': 'utf8'
        },
        'errors': {
            'class': 'Logger.SizedTimedRotatingFileHandler',
            'filename': 'appErrors.log',
            'mode':'w',
            'level': 'ERROR',
            'formatter': 'detailed',
            'when': 'S',                # seconds
            'interval': 86400,          # 86400 seconds = 1 day
            'backupCount': 5,
            'maxBytes': 5342880,        # 5Mb
            'encoding': 'utf8'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file', 'errors']
    }   
}

logging.config.dictConfig(logconfig)

