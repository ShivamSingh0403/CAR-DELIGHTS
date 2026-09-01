import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.vehicles.models import Vehicle, VehicleImage
from services.image_provider import VehicleImageProvider

class Command(BaseCommand):
    help = 'Repairs broken images, regenerates missing thumbnails, and restores primary image flags.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("="*65))
        self.stdout.write(self.style.NOTICE("   CAR DELIGHTS — VEHICLE IMAGE AUTO-REPAIR ENGINE"))
        self.stdout.write(self.style.NOTICE("="*65))

        vehicles = Vehicle.objects.prefetch_related('images').all()
        provider = VehicleImageProvider()
        repaired_count = 0

        for v in vehicles:
            primary = v.primary_image
            needs_repair = False

            if not primary or not primary.image:
                needs_repair = True
            else:
                full_path = os.path.join(settings.MEDIA_ROOT, primary.image.name)
                is_valid, _, _ = provider.validate_image_file(full_path)
                if not is_valid:
                    needs_repair = True

            if needs_repair:
                self.stdout.write(f"Repairing #{v.id} {v.full_name}...")
                provider.ingest_vehicle_images(v, force_refresh=True)
                repaired_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nAuto-Repair Complete! Repaired {repaired_count} vehicle records."))
        self.stdout.write(self.style.NOTICE("="*65 + "\n"))
