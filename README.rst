python-telegram-handler
***********************

.. image:: https://badge.fury.io/py/python-telegram-handler.svg
    :target: https://badge.fury.io/py/python-telegram-handler

.. image:: https://travis-ci.org/sashgorokhov/python-telegram-handler.svg?branch=master
    :target: https://travis-ci.org/sashgorokhov/python-telegram-handler

.. image:: https://codecov.io/github/sashgorokhov/python-telegram-handler/coverage.svg?branch=master
    :target: https://codecov.io/github/sashgorokhov/python-telegram-handler?branch=master

A python logging handler that sends logs via Telegram Bot Api

Installation
============

Via pip:

.. code-block:: shell

    pip install python-telegram-handler

Usage
=====

Register a new telegram bot and obtain a ``authentication token``. (Instructions here https://core.telegram.org/bots#3-how-do-i-create-a-bot)

After that, you must obtain a ``chat_id``. You can do that using included simple script. Start a new conversation with newly created bot, write something to it (it is important to initiate conversation first).


Then run a command:

.. code-block:: shell

    telegram_handler <your token here>
    
If all went ok, a ``chat_id`` will be printed to stdout.

Using ``token`` and ``chat_id``, configure log handler in your desired way.
For example, using dictConfig:

.. code-block:: python

        {
            'version': 1,
            'handlers': {
                'telegram': {
                    'class': 'telegram_handler.TelegramHandler',
                    'token': 'your token',
                    'chat_id': 'chat id'
                }
            },
            'loggers': {
                'my_logger': {
                    'handlers': ['telegram'],
                    'level': 'DEBUG'
                }
            }
        }

Formatting
==========

Currently the format of sent messages is very simple: ``%(asctime)s %(name)s %(levelname)s %(message)s``
Exception traceback will be formatted as pre-formatted fixed-width code block.

If you want to tweak it, configure a ``telegram_handler.MarkdownFormatter`` with your desired format string.
Using a dictConfig:

.. code-block:: python
        
        ...
        {
            'formatters': {
                'telegram': {
                    'class': 'telegram_handler.MarkdownFormatter',
                    'fmt': '%(levelname)s %(message)s'
                }
            }
            'handlers': {
                'telegram': {
                    'class': 'telegram_handler.TelegramHandler',
                    'formatter': 'telegram',
                    'token': 'your token',
                    'chat_id': 'chat id'
                }
            }
        }
        ...

