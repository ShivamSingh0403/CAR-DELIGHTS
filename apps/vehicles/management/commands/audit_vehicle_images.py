import os
import hashlib
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.vehicles.models import Vehicle, VehicleImage

class Command(BaseCommand):
    help = 'Audits all vehicles to ensure 100% genuine real photographs, zero illustrations, zero duplicates, and zero broken files.'

    def _file_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                buf = f.read(65536)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(65536)
            return hasher.hexdigest()
        except Exception:
            return None

    def handle(self, *args, **options):
        vehicles = Vehicle.objects.prefetch_related('images').all()
        total_vehicles = vehicles.count()
        
        real_photos_count = 0
        missing_photos_count = 0
        duplicate_assignments = 0
        illustrations_count = 0
        broken_files_count = 0
        invalid_files_count = 0

        v_hash_map = {}
        v_path_map = {}

        for v in vehicles:
            primary_img = v.primary_image
            if not primary_img or not primary_img.image:
                missing_photos_count += 1
                continue

            img_name = primary_img.image.name
            full_path = os.path.join(settings.MEDIA_ROOT, img_name)

            # Check if file is an illustration / SVG
            if img_name.lower().endswith('.svg') or 'placeholder' in img_name.lower() or 'outline' in img_name.lower() or 'gallery/' in img_name.lower():
                illustrations_count += 1
                continue

            if not os.path.exists(full_path):
                broken_files_count += 1
                continue

            # Check file integrity & size
            try:
                size = os.path.getsize(full_path)
                if size < 500:
                    invalid_files_count += 1
                    continue
            except Exception:
                broken_files_count += 1
                continue

            # Check for duplicate binary images across distinct vehicles
            f_hash = self._file_hash(full_path)
            if f_hash:
                if f_hash in v_hash_map and v_hash_map[f_hash] != v.id:
                    duplicate_assignments += 1
                else:
                    v_hash_map[f_hash] = v.id

            if img_name in v_path_map and v_path_map[img_name] != v.id:
                duplicate_assignments += 1
            else:
                v_path_map[img_name] = v.id

            if primary_img.license_status in ['REAL_PHOTO', 'VALID', 'PROPRIETARY', 'EDITORIAL']:
                real_photos_count += 1
            else:
                missing_photos_count += 1

        self.stdout.write("-------------------------------------")
        self.stdout.write("CAR DELIGHTS IMAGE AUDIT")
        self.stdout.write("-------------------------------------")
        self.stdout.write("")
        self.stdout.write(f"Total vehicles: {total_vehicles}")
        self.stdout.write("")
        self.stdout.write(f"Real photographs: {real_photos_count}")
        self.stdout.write(f"Missing photographs: {missing_photos_count}")
        self.stdout.write(f"Duplicate assignments: {duplicate_assignments}")
        self.stdout.write(f"Illustrations: {illustrations_count}")
        self.stdout.write(f"Broken files: {broken_files_count}")
        self.stdout.write(f"Invalid files: {invalid_files_count}")
        self.stdout.write("")
        self.stdout.write("-------------------------------------")
