from pathlib import Path

from django.db.models.signals import post_save
from django.dispatch import receiver

from main.models import ContextPhoto, BagPhoto
from main.tasks import create_thumbnail, create_bp_thumbnail

def tn_is_same(cp):
    """
    Filename for thumbnails should be "tn_" followed by the 
    filename for the full-size photo
    """
    photo_stem = Path(cp.photo.file.name).stem
    tn_stem = Path(cp.thumbnail.file.name).stem
    return tn_stem == f"tn_{photo_stem}"

@receiver(post_save, sender=ContextPhoto)
def start_thumbnail(sender, **kwargs):
    cp = kwargs["instance"]
    if not cp.thumbnail or (not tn_is_same(cp)):
        create_thumbnail.delay(cp.id)
        

@receiver(post_save, sender=BagPhoto)
def start_bp_thumbnail(sender, **kwargs):
    bp = kwargs["instance"]
    if not bp.thumbnail or (not tn_is_same(bp)):
        create_bp_thumbnail.delay(bp.id)        