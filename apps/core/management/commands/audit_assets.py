from django.core.management.base import BaseCommand
from services.image_validator import ImageAuditService

class Command(BaseCommand):
    help = 'Audits all product and vehicle assets to ensure zero missing, broken, or duplicate images.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("="*60))
        self.stdout.write(self.style.NOTICE("   CAR DELIGHTS — MASTER REAL ASSET AUDIT REPORT"))
        self.stdout.write(self.style.NOTICE("="*60))
        
        auditor = ImageAuditService()
        rep = auditor.audit()

        # Vehicles
        self.stdout.write(self.style.SUCCESS("\nVehicles:"))
        self.stdout.write(f"Total: {rep['vehicles']['total']}")
        self.stdout.write(f"With real images: {rep['vehicles']['with_images']}")
        self.stdout.write(f"Missing images: {rep['vehicles']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['vehicles']['duplicates']}")

        # Products Total
        self.stdout.write(self.style.SUCCESS("\nProducts:"))
        self.stdout.write(f"Total: {rep['products']['total']}")
        self.stdout.write(f"With images: {rep['products']['with_images']}")
        self.stdout.write(f"Missing images: {rep['products']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['products']['duplicates']}")

        # Accessories
        self.stdout.write(self.style.SUCCESS("\nAccessories:"))
        self.stdout.write(f"Total: {rep['accessories']['total']}")
        self.stdout.write(f"With images: {rep['accessories']['with_images']}")
        self.stdout.write(f"Missing images: {rep['accessories']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['accessories']['duplicates']}")

        # Tyres
        self.stdout.write(self.style.SUCCESS("\nTyres:"))
        self.stdout.write(f"Total: {rep['tyres']['total']}")
        self.stdout.write(f"With images: {rep['tyres']['with_images']}")
        self.stdout.write(f"Missing images: {rep['tyres']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['tyres']['duplicates']}")

        # Wheels
        self.stdout.write(self.style.SUCCESS("\nWheels:"))
        self.stdout.write(f"Total: {rep['wheels']['total']}")
        self.stdout.write(f"With images: {rep['wheels']['with_images']}")
        self.stdout.write(f"Missing images: {rep['wheels']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['wheels']['duplicates']}")

        # Maintenance
        self.stdout.write(self.style.SUCCESS("\nMaintenance & Engine:"))
        self.stdout.write(f"Total: {rep['maintenance']['total']}")
        self.stdout.write(f"With images: {rep['maintenance']['with_images']}")
        self.stdout.write(f"Missing images: {rep['maintenance']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['maintenance']['duplicates']}")

        # Services
        self.stdout.write(self.style.SUCCESS("\nServices:"))
        self.stdout.write(f"Total: {rep['services']['total']}")
        self.stdout.write(f"With images: {rep['services']['with_images']}")
        self.stdout.write(f"Missing images: {rep['services']['missing']}")
        self.stdout.write(f"Duplicate assignments: {rep['services']['duplicates']}")

        self.stdout.write(self.style.NOTICE("\n" + "="*60))
        if rep['errors']:
            self.stdout.write(self.style.ERROR(f"FAILURES DETECTED ({len(rep['errors'])}):"))
            for err in rep['errors'][:15]:
                self.stdout.write(self.style.ERROR(f" - {err}"))
        else:
            self.stdout.write(self.style.SUCCESS("ASSET VERIFICATION PASSED: ALL VEHICLE & PRODUCT ASSETS ARE 100% REAL & COMPLIANT!"))
        self.stdout.write(self.style.NOTICE("="*60 + "\n"))
