import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.vehicles.models import VehicleImage
from services.image_provider import VehicleImageProvider

class Command(BaseCommand):
    help = 'Scans for duplicate image binaries assigned to distinct vehicle models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("="*65))
        self.stdout.write(self.style.NOTICE("   CAR DELIGHTS — DUPLICATE IMAGE DETECTOR"))
        self.stdout.write(self.style.NOTICE("="*65))

        images = VehicleImage.objects.select_related('vehicle', 'vehicle__brand').filter(is_primary=True)
        provider = VehicleImageProvider()
        
        hash_map = {}
        duplicates = []

        for img in images:
            if not img.image:
                continue
            full_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
            f_hash = provider.calculate_file_hash(full_path)
            if not f_hash:
                continue

            if f_hash in hash_map:
                existing_v = hash_map[f_hash]
                duplicates.append((img.vehicle.full_name, existing_v.full_name, f_hash))
            else:
                hash_map[f_hash] = img.vehicle

        if duplicates:
            self.stdout.write(self.style.ERROR(f"FOUND {len(duplicates)} DUPLICATE ASSIGNMENTS:"))
            for v1, v2, h in duplicates:
                self.stdout.write(self.style.ERROR(f" - '{v1}' and '{v2}' share identical hash {h[:12]}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"ZERO DUPLICATES FOUND across {len(hash_map)} distinct primary vehicle photographs."))
        
        self.stdout.write(self.style.NOTICE("="*65 + "\n"))
