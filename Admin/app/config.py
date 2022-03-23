from distutils.debug import DEBUG
import os 

basedir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    DEBUG = True
    use_reloader = True

