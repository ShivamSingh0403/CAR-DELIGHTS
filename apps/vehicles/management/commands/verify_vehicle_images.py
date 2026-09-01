import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.vehicles.models import Vehicle, VehicleImage
from services.image_provider import VehicleImageProvider

class Command(BaseCommand):
    help = 'Performs deep integrity and format verification on all vehicle image assets.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("="*65))
        self.stdout.write(self.style.NOTICE("   CAR DELIGHTS — VEHICLE IMAGE INTEGRITY VERIFIER"))
        self.stdout.write(self.style.NOTICE("="*65))

        images = VehicleImage.objects.select_related('vehicle', 'vehicle__brand').all()
        total_images = images.count()
        provider = VehicleImageProvider()

        valid_count = 0
        broken_count = 0
        corrupted_count = 0

        for img in images:
            if not img.image:
                broken_count += 1
                continue

            full_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
            is_valid, msg, meta = provider.validate_image_file(full_path)
            if is_valid:
                valid_count += 1
                if not img.verified:
                    img.verified = True
                    img.save(update_fields=['verified'])
            else:
                corrupted_count += 1
                self.stdout.write(self.style.ERROR(f"Invalid image #{img.id} ({img.vehicle.full_name}): {msg}"))

        self.stdout.write(self.style.SUCCESS(f"\nVerification Results:"))
        self.stdout.write(f"Total Images Inspected: {total_images}")
        self.stdout.write(f"100% Valid Photographs: {valid_count}")
        self.stdout.write(f"Broken / Missing Files: {broken_count}")
        self.stdout.write(f"Corrupted Files: {corrupted_count}")
        self.stdout.write(self.style.NOTICE("="*65 + "\n"))
