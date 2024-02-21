# deepsea-ai, Apache-2.0 license
# Filename: config/config.py
# Description: Configuration helper

from configparser import ConfigParser
import os

from sightwire.logger import info

default_training_prefix = 'sightwire'
default_config_ini = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')


class Config:

    def __init__(self, custom_config_ini: str = None, quiet: bool = False):
        """
        Read the .ini file and parse it
        """
        self.parser = ConfigParser()
        if custom_config_ini:
            self.config_ini = custom_config_ini
        else:
            self.config_ini = default_config_ini

        if not os.path.isfile(self.config_ini):
            raise Exception(f'Bad path to {self.config_ini}. Is your {self.config_ini} missing?')

        self.parser.read(self.config_ini)
        lines = open(self.config_ini).readlines()
        if not quiet:
            info(f"=============== Config file {self.config_ini} =================")
            for l in lines:
                info(l.strip())


    def __call__(self, *args, **kwargs):
        assert len(args) == 2
        return self.parser.get(args[0], args[1])

    def save(self, *args, **kwargs):
        assert len(args) == 3
        self.parser.set(section=args[0], option=args[1], value=args[2])
        with open(self.config_ini, 'w') as fp:
            self.parser.write(fp)
