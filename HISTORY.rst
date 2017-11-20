.. :changelog:

History
-------

2.0.2 (2017-11-20)
++++++++++++++++++

* fix TypeError in HtmlFormatter.format (by tompipen)


2.0 (2017-03-01)
++++++++++++++++

* Refactored HtmlFormatter and MarkdownFormatter
* Refactored TelegramHandler
* No more need to call a command to obtain a chat_id - it will be obtained automatically on handler init
* Rewritten tests
* Escape LogRecord things in HtmlFormatter
* Added optional emoji symbols in HtmlFormatter.

1.1.3 (2016-09-22)
++++++++++++++++++

* Setting escape_message field of StyledFormatter missed (@ihoru)

1.1.2 (2016-05-13)
++++++++++++++++++

* Fixed setup.py requires option (changed to install_requires)

1.1.1 (2016-04-20)
++++++++++++++++++

* Use HTML Formatter as default formatter for telegram handler

1.1.0 (2016-04-20)
++++++++++++++++++

* Introduced HTML Formatter
* Added log text escaping (closed #3)
* Added requests timeout setting (closed  #1)
* Catching and logging all requests and their exceptions (closed #2)

1.0.0 (2016-04-19)
++++++++++++++++++

* First PyPi release

0.1.0 (2016-04-19)
++++++++++++++++++

* Initial release