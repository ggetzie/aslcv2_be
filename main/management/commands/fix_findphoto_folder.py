import pathlib
from django.core.management.base import BaseCommand

from main.models import ObjectFind, FindPhoto


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # check all ObjectFinds, if the findphoto folder is named "photo" change it to "photos"
        # if the folder "photos" already exists copy the files from "photo" to "photos"
        # then delete "photo".
        # Update the path attribute in all associated FindPhoto objects
        for object_find in ObjectFind.objects.all():
            fp_folder = object_find.absolute_findphoto_folder
            old_fp_folder = fp_folder.parent / "photo"
            if fp_folder.exists() and old_fp_folder.exists():
                print(f"Moving files from 'photo' to 'photos' for {object_find}")
                for photo in old_fp_folder.iterdir():
                    photo.rename(fp_folder / photo.name)
                old_fp_folder.rmdir()
            elif old_fp_folder.exists() and not fp_folder.exists():
                print(f"renaming 'photo' to 'photos' for {object_find}")
                old_fp_folder.rename(fp_folder)
            else:
                pass
            for find_photo in object_find.findphoto_set():
                rel_fp_path = object_find.findphoto_folder
                p = pathlib.Path(find_photo.photo.path)
                find_photo.photo.name = f"{rel_fp_path}/{p.name}"
