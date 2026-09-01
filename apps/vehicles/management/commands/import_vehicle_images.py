import time
from django.core.management.base import BaseCommand
from apps.vehicles.models import Vehicle, VehicleImage
from services.image_provider import VehicleImageProvider

class Command(BaseCommand):
    help = 'Automatically imports, downloads, validates, and assigns real-world photographs for all 250+ vehicles.'

    def add_arguments(self, parser):
        parser.add_argument('--missing-only', action='store_true', help='Only process vehicles without verified real images')
        parser.add_argument('--force-refresh', action='store_true', help='Force re-download and re-synthesis of all images')
        parser.add_argument('--brand', type=str, default=None, help='Filter by brand name')

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("="*65))
        self.stdout.write(self.style.NOTICE("   CAR DELIGHTS — MASTER BULK VEHICLE IMAGE INGESTION"))
        self.stdout.write(self.style.NOTICE("="*65))

        missing_only = options['missing_only']
        force_refresh = options['force_refresh']
        brand_filter = options['brand']

        queryset = Vehicle.objects.select_related('brand').all()
        if brand_filter:
            queryset = queryset.filter(brand__name__iexact=brand_filter)

        total_vehicles = queryset.count()
        self.stdout.write(f"Loaded {total_vehicles} vehicles from database for processing.")
        
        provider = VehicleImageProvider()
        processed_count = 0
        success_count = 0
        failed_count = 0
        start_time = time.time()

        for idx, vehicle in enumerate(queryset, start=1):
            if missing_only and vehicle.has_real_photo and not force_refresh:
                continue

            try:
                images = provider.ingest_vehicle_images(vehicle, force_refresh=force_refresh)
                if images:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f"Error processing #{vehicle.id} {vehicle.full_name}: {e}"))

            processed_count += 1
            if idx % 25 == 0 or idx == total_vehicles:
                self.stdout.write(f"[{idx}/{total_vehicles}] Processed {vehicle.brand.name} {vehicle.model}...")

        elapsed = round(time.time() - start_time, 2)
        self.stdout.write(self.style.NOTICE("\n" + "="*65))
        self.stdout.write(self.style.SUCCESS(f"INGESTION COMPLETE IN {elapsed}s:"))
        self.stdout.write(f"Total Processed: {processed_count}")
        self.stdout.write(f"Success / Photographed: {success_count}")
        self.stdout.write(f"Failures / Missing: {failed_count}")
        self.stdout.write(self.style.NOTICE("="*65 + "\n"))
