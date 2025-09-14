"""
Service for uploading files to Cloudinary.
Provides configuration and upload functionality for user avatars.
"""

import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    Service class for uploading files to Cloudinary.
    Handles configuration and file upload for user avatars.
    """

    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize Cloudinary configuration.
        Args:
            cloud_name (str): Cloudinary cloud name.
            api_key (str): Cloudinary API key.
            api_secret (str): Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file to Cloudinary and return the image URL.
        Args:
            file: File object to upload (should have .file attribute).
            username (str): Username to use in public_id.
        Returns:
            str: URL of the uploaded image.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
