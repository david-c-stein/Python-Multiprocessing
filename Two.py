#!/usr/bin/env python

try:
    from Global import __MULTIPROCESSING__
    if __MULTIPROCESSING__:
        import multiprocessing
except:
    __MULTIPROCESSING__ = False
    import Logger
    pass

import sys
import threading
import time


class Two(multiprocessing.Process if __MULTIPROCESSING__ else threading.Thread):

    def __getstate__(self):
        # Process safe copy - for items not pickleable
        d = self.__dict__.copy()
        if 'logger' in d:
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        # Process safe copy - for items not pickleable
        if 'logger' in d:
            logging.config.dictConfig(d['logconfig'])
            d['logger'] = logging.getLogger(d['logger'])
        self.__dict__.update(d)

    def __init__(self, logger, logconfig, qOne, qTwo, qThr):
        if __MULTIPROCESSING__:
            #-- multiprocessing
            multiprocessing.Process.__init__(self)
            self.exit = multiprocessing.Event()
        else:
            #-- threading
            super(Two, self).__init__()

        self.logger = logger
        self.logconfig = logconfig

        self.logger.info("Initializing " + __file__)

        # message queues
        self.getMsgQue = qTwo
        self.putMsgOne = qOne.put
        self.putMsgThr = qThr.put

        self.RUNNING = True;
        return

    def run(self):
        try:
            self.logger.info("Running Two process")

            while self.RUNNING:
                try:
                    # check for messages
                    if (not self.getMsgQue.empty()):
                        msg = self.getMsgQue.get()

                        self.logger.debug(str(msg))

                        if (msg != None):

                            event = msg['event']
                            data = msg['data']

                            if (event == 'print'):
                                self.logger.info("Print : " + str(data))

                            else:
                                self.logger.warn('Unknown event type')

                            self.putMsgThr( msg )

                    else:
                        time.sleep(.2)

                except (KeyboardInterrupt, SystemExit):
                    self.logger.info("Interrupted")
                    self.stop()

                except Exception as e:
                    self.logger.exception(str(e))
                    self.stop()

        except Exception as e:
            self.logger.exception(e)
            self.stop()

        finally:
            self.logger.info("Exiting")

    def stop(self):
        self.RUNNING = False
        return

#-----------------------
# test

def test():

    if sys.version_info[0] < 3:
        from Queue import Queue
    else:
        from queue import Queue

    import Logger

    logger = Logger.logging.getLogger(__name__)
    logconfig = Logger.logconfig
    qOne = Queue()
    qTwo = Queue()
    qThr = Queue()

    logger.info('Local Two vTest Mode')

    pTest = None

    try:
        pTest = Two(logger, logconfig, qOne, qTwo, qThr)
        pTest.start()

        while(True):
            msg = { 'event' : 'print', 'data' : 'Local Test' }
            qTwo.put(msg)
            logger.info(str(msg))
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        logger.info("Interrupted")

    except Exception as e:
        logger.exception(str(e))

    if pTest:
        pTest.stop()

    logger.info("Exiting")


if __name__== '__main__':
    test()