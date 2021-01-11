import PIL
import pathlib

from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from main.models import ContextPhoto

@shared_task
def create_thumbnail(photo_id):
    print(f"Received id {photo_id}")
    cp = ContextPhoto.objects.get(id=photo_id)
    photo_path = pathlib.Path(cp.photo.file.name)
    basewidth = 50
    tn_name = f"tn_{photo_path.name}"
    img = PIL.Image.open(photo_path)
    if img.size[0] <= 50:
        return
    # scale image to 50px width
    height = int(img.size[1] * basewidth / img.size[0])
    resized = img.resize((basewidth, height), PIL.Image.ANTIALIAS)
    buffer = BytesIO()
    resized.save(fp=buffer, format="JPEG")
    cf = ContentFile(buffer.getvalue())
    cp.thumbnail.save(tn_name,
                      InMemoryUploadedFile(cf,
                                           None,
                                           tn_name,
                                           "image/jpeg",
                                           cf.tell,
                                           None))
    return cp.thumbnail.file.name
