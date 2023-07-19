from minio import Minio
from minio.error import S3Error
from starlette.datastructures import UploadFile
import shutil
import uuid


ENDPOINT = "192.168.1.254:9000"
ACCESS_KEY = "minioadmin"
SECRET_KEY = "minioadmin"
BUCKET_NAME = "meeting"


class MinioUploader:
    def __init__(self):
        self.client = Minio(
            ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY,
            secure=False,
        )
        self.bucket_name = BUCKET_NAME

    def upload(self, file: UploadFile):
        object_name = f"{uuid.uuid4()}{file.filename}"
        file_path = f"static/uploads/{object_name}"

        with open(file_path, "wb") as local_file:
            # Step 3: Write the uploaded content to the local file
            shutil.copyfileobj(file.file, local_file)
        
        return file_path

        # try:
        #     self.client.fput_object(
        #         self.bucket_name,
        #         object_name,
        #         file_path,
        #     )

        #     # get url without expiration and signature
        #     url = self.client.presigned_get_object(
        #         self.bucket_name,
        #         object_name,
        #     )

        #     return url
        # except S3Error as exc:
        #     print("error occurred.", exc)


# def main():
#     # Create a client with the MinIO server playground, its access key
#     # and secret key.
#     client = Minio(
#         "play.min.io",
#         access_key="Q3AM3UQ867SPQQA43P2F",
#         secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
#     )

#     # Make 'asiatrip' bucket if not exist.
#     found = client.bucket_exists("asiatrip")
#     if not found:
#         client.make_bucket("asiatrip")
#     else:
#         print("Bucket 'asiatrip' already exists")

#     # Upload '/home/user/Photos/asiaphotos.zip' as object name
#     # 'asiaphotos-2015.zip' to bucket 'asiatrip'.
#     client.fput_object(
#         "asiatrip", "asiaphotos-2015.zip", "/home/user/Photos/asiaphotos.zip",
#     )
#     print(
#         "'/home/user/Photos/asiaphotos.zip' is successfully uploaded as "
#         "object 'asiaphotos-2015.zip' to bucket 'asiatrip'."
#     )


# if __name__ == "__main__":
#     try:
#         main()
#     except S3Error as exc:
#         print("error occurred.", exc)
