import sys
import os
from configparser import ConfigParser, BasicInterpolation


class EnvInterpolation(BasicInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)

        if not os.path.expandvars(value).startswith("$"):
            return os.path.expandvars(value)


try:
    config = ConfigParser(interpolation=EnvInterpolation())
    config.read("conf/application.conf")
except Exception as e:
    print(f"Error while loading the config: {e}")
    print("Failed to Load Configuration. Exiting!!!")
    sys.exit(1)


def get_split_config(config, section, key, index):
    try:
        item = str(config.get(section, key)).split("|")[index]
        item = None if item == "none" else item
        return item
    except Exception:
        return None


class Service:
    app_secret = get_split_config(config, "SERVICE", "APP_SEC_DATA", 0)
    admin_secret = get_split_config(config, "SERVICE", "APP_SEC_DATA", 1)
    env_type = get_split_config(config, "SERVICE", "APP_SEC_DATA", 2)
    server_host = get_split_config(config, "SERVICE", "APP_SEC_DATA", 3)


class Log:
    location = get_split_config(config, "LOG", "DATA", 0) if get_split_config(config, "LOG", "DATA", 0) else "internal"


class Postgre:
    uri = config.get("POSTGRE", "URI")


class Storage:
    local = True if get_split_config(config, "STORAGE", "DATA", 0) == "true" else False
    third_party = get_split_config(config, "STORAGE", "DATA", 1)


class Redis:
    uri = config.get("REDIS", "URI")


class Supabase:
    url = get_split_config(config, "SUPABASE", "DATA", 0)
    key = get_split_config(config, "SUPABASE", "DATA", 1)
    bucket = get_split_config(config, "SUPABASE", "DATA", 2)


class AzureBlob:
    url = get_split_config(config, "AZURE", "DATA", 0)
    key = get_split_config(config, "AZURE", "DATA", 1)
    container_name = get_split_config(config, "AZURE", "DATA", 2)


class Axiom:
    org_id = get_split_config(config, "AXIOM", "DATA", 0)
    api_key = get_split_config(config, "AXIOM", "DATA", 1)
    url = get_split_config(config, "AXIOM", "DATA", 2)
