#!/usr/bin/env python

import datetime
import getopt
import inspect
import json
import os
import platform
import sys
import time
import threading

from Global import __MULTIPROCESSING__

__version__ = "0.1"


if __MULTIPROCESSING__:
    import multiprocessing
    from multiprocessing import Queue
    from multiprocessing import Array
else:
    if sys.version_info[0] < 3:
        from Queue import Queue
    else:
        from queue import Queue

import Logger

starttime = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")

#-----------------------
class myApp(object):

    logger = None
    logconfig = None

    pTwo = None  # Worker Two thread/process
    pThr = None  # Worker Thr thread/process

    def main(self, argv):

        self.logger  = Logger.logging.getLogger(__name__)
        self.logconfig = Logger.logconfig

        self.logger.info("Start time: " + starttime)

        # parse command line arguments
        try:
            opts, args = getopt.getopt(argv, "h", ["help"])
        except getopt.GetoptError as e:
            self.logger.exception(str(e))
            self.usage()
            return
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                return
            else:
                self.usage()
                return

        # initilize and run
        self.initilize()
        self.start()

    #-----------------------
    def initilize(self):
        try:
            # identify platform
            self.logger.info("------------------------------")
            self.logger.info("  machine: " + platform.machine())
            self.logger.info("  version: " + platform.version())
            self.logger.info(" platform: " + platform.platform())
            self.logger.info("   system: " + platform.system())
            self.logger.info("processor: " + platform.processor())
            if __MULTIPROCESSING__:
                self.logger.info("    cores: " + str(multiprocessing.cpu_count()))
            self.logger.info("    nodes: " + platform.node())
            self.logger.info("PythonImp: " + platform.python_implementation())
            self.logger.info("PythonVer: " + platform.python_version())
            self.logger.info("starttime: " + starttime)
            self.logger.info("scriptver: " + __version__)
            self.logger.info("------------------------------")

            # initialize queues
            if __MULTIPROCESSING__:
                self.qOne = multiprocessing.Queue()
                self.qTwo = multiprocessing.Queue()
                self.qThr = multiprocessing.Queue()
            else:
                self.qOne = Queue()
                self.qTwo = Queue()
                self.qThr = Queue()

            # initialize 'two' process
            try:
                import Two
                self.pTwo = Two.Two(self.logger, self.logconfig, self.qOne, self.qTwo, self.qThr)
            except Exception as e:
                self.logger.exception(e)
                print( "Two Initialization Error: " + str(e) )

            # initialize 'three' process
            try:
                import Three
                self.pThr = Three.Three(self.logger, self.logconfig, self.qOne, self.qTwo, self.qThr)
            except Exception as e:
                self.logger.exception(e)
                print( "Three Initialization Error: " + str(e) )

            # Queue for main process
            self.getMsgQue = self.qOne
            self.putMsgTwo = self.qTwo.put
            self.putMsgThr = self.qThr.put

            self.RUNNING = True

        except Exception as e:
            self.logger.exception(e)

    #-----------------------
    def start(self):
        try:
            # start two
            self.pTwo.start()

            # start three
            self.pThr.start()

            simpleCnt = 0

            while self.RUNNING:
                try:
                    #-----------------------
                    # process main

                    if (not self.getMsgQue.empty()):
                        msg = self.getMsgQue.get()

                        self.logger.debug('Main : ' + str(self.msg))

                        if (msg != None):
                            event = msg['event']
                            type = msg['data']

                    else:
                        time.sleep(.2)
                    
                        simpleCnt += 1
                        if (simpleCnt % 6):
                            msgOne = { 'event' : 'print',
                                       'data' : ['Hello from Main', 'two', 3, 4, 'V', 'VI', 'VII', 8, 'nine']}
                            self.putMsgTwo( msgOne )

                        if (simpleCnt > 30):
                            simpleCnt = 0

                except (KeyboardInterrupt, SystemExit):
                    self.logger.info("Interrupted")
                    self.stop()

                except Exception as e:
                    self.logger.exception(str(e))
                    self.stop()

        except Exception as e:
            self.logger.exception(str(e))
            self.stop()

        finally:
            self.logger.info("Exiting")

    #-----------------------
    def stop(self):
        # stop processes
        if(self.pTwo != None):
            self.pTwo.stop()
        if(self.pThr != None):
            self.pThr.stop()

        if(self.pTwo != None):
            self.pTwo.join()
        if(self.pThr != None):
            self.pThr.join()

        self.RUNNING = False


if __name__== '__main__':
    myApp().main(sys.argv[1:])

