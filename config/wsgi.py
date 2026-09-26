import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
# Wrap the app with WhiteNoise to serve media files in production
application = WhiteNoise(application, root=settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
app = application
