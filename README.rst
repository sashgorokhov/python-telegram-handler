python-telegram-handler
***********************

.. image:: https://img.shields.io/pypi/status/python-telegram-handler.svg
    :target: https://github.com/sashgorokhov/python-telegram-handler

.. image:: https://img.shields.io/pypi/pyversions/python-telegram-handler.svg
    :target: https://pypi.python.org/pypi/python-telegram-handler

.. image:: https://badge.fury.io/py/python-telegram-handler.svg 
    :target: https://badge.fury.io/py/python-telegram-handler 

.. image:: https://travis-ci.org/sashgorokhov/python-telegram-handler.svg?branch=master 
    :target: https://travis-ci.org/sashgorokhov/python-telegram-handler 

.. image:: https://codecov.io/github/sashgorokhov/python-telegram-handler/coverage.svg?branch=master 
    :target: https://codecov.io/github/sashgorokhov/python-telegram-handler?branch=master 

.. image:: https://codeclimate.com/github/sashgorokhov/python-telegram-handler/badges/gpa.svg
   :target: https://codeclimate.com/github/sashgorokhov/python-telegram-handler
   :alt: Code Climate

.. image:: https://img.shields.io/github/license/sashgorokhov/python-telegram-handler.svg 
    :target: https://raw.githubusercontent.com/sashgorokhov/python-telegram-handler/master/LICENSE 


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

Also, there is an ability for handler to automatically retrieve ``chat_id``. This will be done on handler initialization. But you still have to start a conversation with bot. Be aware: if program stops, server restarts, or something else will happen - handler will try to retrieve chat id from telegram, and may fail, if it will not find a NEW message from you. So i recommend you to use a script below for obtaining chat id. 

Then run a command:

.. code-block:: shell

    python -m telegram_handler <your token here>
    
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

Currently the format of sent messages is very simple: ``<code>%(asctime)s</code> <b>%(levelname)s</b>\nFrom %(name)s:%(funcName)s\n%(message)s``
Exception traceback will be formatted as pre-formatted fixed-width code block. (https://core.telegram.org/bots/api#html-style)

If you want to tweak it, configure a ``telegram_handler.HtmlFormatter`` with your desired format string.
Using a dictConfig:

.. code-block:: python
        
        ...
        {
            'formatters': {
                'telegram': {
                    'class': 'telegram_handler.HtmlFormatter',
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

If you wish, you can enable emoji symbols in HtmlFormatter. Just specify `use_emoji=True` in HtmlFormatter settings.
This will add to levelname a :white_circle: for DEBUG, :large_blue_circle: for INFO, and :red_circle: for WARNING and ERROR levels. 
