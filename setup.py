from distutils.core import setup

with open('README.rst') as readme:
    with open('HISTORY.rst') as history:
        long_description = readme.read() + '\n\n' + history.read()

VERSION = '2.1.0'

setup(
    install_requires=['requests'],
    name='python-telegram-handler',
    version=VERSION,
    packages=['telegram_handler'],
    url='https://github.com/sashgorokhov/python-telegram-handler',
    download_url='https://github.com/sashgorokhov/python-telegram-handler/archive/v%s.zip' % VERSION,
    keywords=['telegram', 'logging', 'handler', 'bot'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Debuggers',
        'Topic :: System :: Logging'
    ],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description='A python logging handler that sends logs via Telegram Bot Api.',
)
