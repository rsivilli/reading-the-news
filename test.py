import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reading_the_news.settings")

django.setup()

from dreamer.tools.jobs import (  # noqa: E402, E501 import requires django setup to be run first before imports of models
    run,
)


run()
