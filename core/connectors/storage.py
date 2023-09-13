from supabase import create_client  # type: ignore
from azure.storage.blob import BlobServiceClient
from core.configurations import Supabase, Storage, Service, AzureBlob
from core.connectors.cache import cache_client
from core.utils.general import get_alphnum_id, colored_print
import os
import json
from typing import Optional


class StorageManager:

    def __init__(self):
        if Storage.third_party == "supabase":
            self.supabase = create_client(Supabase.url, Supabase.key)  # type: ignore
            self.blob_service_client = None
            self._validate_bucket()
        elif Storage.third_party == "azure_blob":
            self.blob_service_client = BlobServiceClient(
                account_url=AzureBlob.url, credential=AzureBlob.key)  # type: ignore
            self.supabase = None
            self._validate_container()
        else:
            self.supabase = None
            self.blob_service_client = None
            colored_print(
                "Warning: Third party storage is not configured. Storage client will use local storage.",
                "yellow"
            )

    def _validate_bucket(self):
        res = self.supabase.storage.list_buckets()  # type: ignore
        if Supabase.bucket not in [bucket.name for bucket in res]:  # noqa
            res = self.supabase.storage.create_bucket(Supabase.bucket)  # type: ignore

    def _validate_container(self):
        container_client = self.blob_service_client.get_container_client(AzureBlob.container_name)  # type: ignore
        if not container_client.exists():
            colored_print(
                f"Container {AzureBlob.container_name} does not exist in the Azure Blob Storage. Infr is creating it.",
                "yellow"
            )
            container_client.create_container()
            colored_print(f"Container {AzureBlob.container_name} created successfully.", "green")

    def upload_file(self, file: bytes, file_path: str, store_cloud: bool = True):
        if Storage.local:
            # If directory in path doesn't exist, create it
            if not os.path.exists(f"storage/{os.path.dirname(file_path)}"):
                os.makedirs(f"storage/{os.path.dirname(file_path)}")

            with open(f"storage/{file_path}", 'wb') as f:
                f.write(file)

        if Storage.third_party == "supabase" and store_cloud:
            return self.supabase.storage.from_(Supabase.bucket).upload(file_path, file)  # type: ignore

        elif Storage.third_party == "azure_blob" and store_cloud:
            blob_client = self.blob_service_client.get_blob_client(     # type: ignore
                container=AzureBlob.container_name, blob=file_path  # type: ignore
            )
            blob_client.upload_blob(file)

        return None

    def get_file(self, file_path: str):
        if Storage.local:
            if os.path.exists(f"storage/{file_path}"):
                with open(f"storage/{file_path}", 'rb') as f:
                    return f.read()

        if Storage.third_party == "supabase":
            try:
                file = self.supabase.storage.from_(Supabase.bucket).download(file_path)  # type: ignore
                if Storage.local:
                    self.upload_file(file, file_path, store_cloud=False)
                return file
            except Exception as e:
                print(f"Error while getting the file from the storage: {e}")

        if Storage.third_party == "azure_blob":
            blob_client = self.blob_service_client.get_blob_client(      # type: ignore
                container=AzureBlob.container_name, blob=file_path)  # type: ignore
            stream = blob_client.download_blob()
            return stream.readall()

        return None

    def get_file_url(self, file_path: str, timeout: int = 3600) -> Optional[str]:
        file_ending = file_path.split(".")[-1]
        if not file_ending in ["webp", "lzma", "jpg"]:  # noqa
            return None

        lzma_type = 'json'
        if file_ending == "lzma":
            # Make sure it's a .{valid}.lzma file
            if file_path.split(".")[-2] == "html":
                lzma_type = 'html'
            elif file_path.split(".")[-2] == "json":
                lzma_type = 'json'
            else:
                return None

        is_lzma = False
        mimetype = "image/webp"
        if file_ending == "lzma":
            if lzma_type == "json":
                mimetype = "application/json"
                file_ending = "json"
                is_lzma = True
            elif lzma_type == "html":
                mimetype = "text/html"
                file_ending = "html"
                is_lzma = True
        if file_ending == "jpg":
            mimetype = "image/jpeg"

        random_id = get_alphnum_id(prefix='file_', id_len=32)
        data = {'file_path': file_path, 'mimetype': mimetype, 'lzma_compressed': is_lzma}
        cache_client.set_item(random_id, json.dumps(data), expiry=timeout)
        return f"{Service.server_host}/v1/file/{random_id}.{file_ending}"


storage_client = StorageManager()
