from os.path import abspath, dirname, join

from dynaconf import Dynaconf

cwd: str = abspath(dirname(__file__))

settings = Dynaconf(
    envvar_prefix=False,
    environments=True,
    env_switcher='HOSTING_ENVIRONMENT',
    settings_files=[join(cwd, 'settings.toml'), join(cwd, '.secrets.toml')]
)
