#!/usr/bin/python

import Queue

class DummySerial(object):
    def __init__(self, queuewrite, queueread):
        self.queuewrite = queuewrite
        self.queueread = queueread

    def write(self, data):
        self.queuewrite.put_nowait(data)

    def read(self, timeout=0.5):
        try:
            result = self.queueread.get(timeout=timeout)
            return result
        except Queue.Empty:
            return ""


def mkserial():
    A, B = Queue.Queue(), Queue.Queue()
    producer = DummySerial(A, B)
    consumer = DummySerial(B, A)
    return (producer, consumer)
