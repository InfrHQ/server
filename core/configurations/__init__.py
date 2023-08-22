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


class Service:
    app_secret = str(config.get("SERVICE", "APP_SEC_DATA")).split("|")[0]
    admin_secret = str(config.get("SERVICE", "APP_SEC_DATA")).split("|")[1]
    env_type = str(config.get("SERVICE", "APP_SEC_DATA")).split("|")[2]
    server_host = str(config.get("SERVICE", "APP_SEC_DATA")).split("|")[3]


class Log:
    path = config.get("LOG", "PATH")
    level = config.get("LOG", "LEVEL") or "INFO"
    size = config.get("LOG", "MAX_SIZE_BYTES")
    backup_count = config.get("LOG", "BACKUP_COUNT")


class Postgre:
    uri = config.get("POSTGRE", "URI")


class Storage:
    local = True if str(config.get("STORAGE", "DATA")).split("|")[0] == "true" else False
    third_party = None if str(config.get("STORAGE", "DATA")).split(
        "|")[1] == "none" else str(config.get("STORAGE", "DATA")).split("|")[1]


class Redis:
    uri = config.get("REDIS", "URI")


class Supabase:
    if Storage.third_party == "supabase":
        url = str(config.get("SUPABASE", "DATA")).split("|")[0]
        key = str(config.get("SUPABASE", "DATA")).split("|")[1]
        bucket = str(config.get("SUPABASE", "DATA")).split("|")[2]
    else:
        url = ""
        key = ""
        bucket = ""


class AzureBlob:
    if Storage.third_party == "azure_blob":
        url = str(config.get("AZURE", "DATA")).split("|")[0]
        key = str(config.get("AZURE", "DATA")).split("|")[1]
        container_name = str(config.get("AZURE", "DATA")).split("|")[2]
    else:
        url = ""
        key = ""
        container_name = ""
