# -*- coding: utf-8 -*-


class FakeMessageHandler(object):

    def __init__(self, queue, message):
        self.queue = queue
        self.message = message
        self.clean = False

    def add(self):
        self.clean = False
        self.queue.append(self.message)

    def mark_as_read(self):
        self.clean = False
        self.message.obj['read'] = True

    def cleanup(self):
        ids_to_remove = []
        for i in range(len(self.queue)):
            if self.queue[i].obj['read']:
                ids_to_remove.append(i)

        ids_to_remove.reverse()
        for id_ in ids_to_remove:
            self.queue.pop(id_)
        self.clean = True
