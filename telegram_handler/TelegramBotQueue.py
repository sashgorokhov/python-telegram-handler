import telegram
from telegram.ext import MessageQueue
from telegram.ext.messagequeue import queuedmessage


class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = kwargs.get('is_queued_def', True)
        self._msg_queue = kwargs.get('mqueue') or MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        return super(MQBot, self).send_message(*args, **kwargs)