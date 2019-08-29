from setuptools import setup

APP_NAME = "xBan"

APP = ['xBan.py']
DATA_FILES = [('', ['xban.qss', 'xample.xban'])]
OPTIONS = {
    'argv_emulation': True,
    # 'iconfile': '',
    'includes': ["sip", "PyQt5.QtGui", "PyQt5.QtCore", "PyQt5.QtWidgets"],
    'excludes': [
        'PyQt5.QtDesigner',
        'PyQt5.QtNetwork',
        'PyQt5.QtOpenGL',
        'PyQt5.QtScript',
        'PyQt5.QtSql',
        'PyQt5.QtTest',
        'PyQt5.QtWebKit',
        'PyQt5.QtXml',
        'PyQt5.phonon',
    ],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Convert from DOI to .bib",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2018, Peter Sun, All Rights Reserved",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    ## General setup info
    name="xBan",
    version="0.1.0",
    license='MIT',
    author="Peter Sun",
    author_email='peterhs73@outlook.com',
    url='https://github.com/peterhs73/xBan',
    description="Personal Kanban",
)
