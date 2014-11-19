# -*- coding: utf-8 -*-


class FakeMessageHandler(object):

    def __init__(self, queue):
        self.queue = queue

    def add(self, message):
        self.queue.append(message)

    def mark_as_read(self, message):
        message.obj['read'] = True

    def cleanup(self):
        ids_to_remove = []
        for i in range(len(self.queue)):
            if self.queue[i].obj['read']:
                ids_to_remove.append(i)

        ids_to_remove.reverse()
        for id_ in ids_to_remove:
            self.queue.pop(id_)


def fake_adapter(queue, name):
    return FakeMessageHandler(queue)
