import json
from typing import IO, cast

from google.cloud.exceptions import NotFound

from minimalkv.fsspecstore import FSSpecStore, FSSpecStoreEntry


class GoogleCloudStore(FSSpecStore):
    """A store using ``Google Cloud storage`` as a backend.

    See ``https://cloud.google.com/storage``.
    """

    def __init__(
        self,
        credentials,
        bucket_name: str,
        create_if_missing: bool = True,
        bucket_creation_location: str = "EUROPE-WEST3",
        project=None,
    ):
        if isinstance(credentials, str):
            # Parse JSON from path to extract project name
            try:
                with open(credentials) as f:
                    credentials_dict = json.load(f)
                    project = project or credentials_dict["project_id"]
            except (FileNotFoundError, json.JSONDecodeError) as error:
                print(
                    f"Could not get the project name from the credentials file: {error}"
                )

        self._credentials = credentials
        self.bucket_name = bucket_name
        self.create_if_missing = create_if_missing
        self.bucket_creation_location = bucket_creation_location
        self.project_name = project

        super().__init__(prefix=f"{bucket_name}/", mkdir_prefix=create_if_missing)

    def _create_filesystem(self):
        from gcsfs import GCSFileSystem

        return GCSFileSystem(
            project=self.project_name,
            token=self._credentials,
            access="read_write",
            default_location=self.bucket_creation_location,
        )

    def _open(self, key: str) -> IO:
        if not self._prefix_exists:
            raise NotFound(f"Could not find bucket: {self.bucket_name}")
        return cast(IO, FSSpecStoreEntry(super()._open(key)))
