import PIL
import pathlib
import time

from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from main.models import ContextPhoto, BagPhoto

THUMBNAIL_DIM = 100

def create_thumbnail(photo_obj):
    photo_path = pathlib.Path(photo_obj.photo.file.name)
    tn_name = f"tn_{photo_path.name}"
    img = PIL.Image.open(photo_path)
    buffer = BytesIO()
    img.thumbnail((THUMBNAIL_DIM,THUMBNAIL_DIM), 
                  resample=PIL.Image.LANCZOS, 
                  reducing_gap=3.0)
    img.save(fp=buffer, format="JPEG", quality=95)                  
    cf = ContentFile(buffer.getvalue())
    photo_obj.thumbnail.save(tn_name,
                             InMemoryUploadedFile(cf,
                                                  None,
                                                  tn_name,
                                                  "image/jpeg",
                                                  cf.tell,
                                                  None))
    return photo_obj.thumbnail.file.name

@shared_task
def cp_thumbnail(photo_id):
    print(f"Received id {photo_id}")
    time.sleep(1)
    cp = ContextPhoto.objects.get(id=photo_id)
    thumb_name = create_thumbnail(cp)
    return thumb_name

@shared_task
def bp_thumbnail(photo_id):
    print(f"Received id {photo_id}")
    time.sleep(1)
    bp = BagPhoto.objects.get(id=photo_id)
    thumb_name = create_thumbnail(bp)
    return thumb_name
