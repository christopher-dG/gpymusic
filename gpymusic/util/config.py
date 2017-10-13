import os
import yaml

from gpymusic.util import err


class Config:
    """
    Config contains all relevant configuration options
    extracted from a YAML file.
    """
    def __init__(self, config_file):
        with open(config_file) as f:
            config = yaml.load(f)

        if "ui" not in config:
            err("Missing key in config: 'ui'")
        if config["ui"] not in _available_modules("ui"):
            err("Invalid value for 'ui': '%s'" % config["ui"])

        if "music" not in config:
            err("Missing key in config: 'music'")
        if config["music"] not in _available_modules("provider"):
            err("Invalid value for 'provider': '%s'" % config["provider"])

        self.ui = config["ui"]
        self.provider = config["music"]

        if self.ui not in config:
            err("Missing key in config: '%s'" % self.ui)
        if self.provider not in config:
            err("Missing key in config: '%s'" % self.provider)

        self.ui_settings = config[self.ui]
        self.provider_settings = config[self.provider]


def _available_modules(dirname):
    """Get all available modules in a directory."""
    dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), dirname)
    files = list(os.walk(dir))[0][2]
    try:
        files.remove("__init__.py")
    except:
        pass
    # Drop the trailing '.py'.
    return [f[:-3] for f in files]
