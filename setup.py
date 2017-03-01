from distutils.core import setup

with open('README.rst') as readme:
    with open('HISTORY.rst') as history:
        long_description = readme.read() + '\n\n' + history.read()

setup(
    install_requires=['requests'],
    name='python-telegram-handler',
    version='2.0',
    packages=['telegram_handler'],
    url='https://github.com/sashgorokhov/python-telegram-handler',
    download_url='https://github.com/sashgorokhov/python-telegram-handler/archive/master.zip',
    keywords=['telegram', 'logging', 'handler', 'bot'],
    classifiers=[],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description='A python logging handler that sends logs via Telegram Bot Api.',
)