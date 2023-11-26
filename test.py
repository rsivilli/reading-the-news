import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reading_the_news.settings")

django.setup()

from dreamer.tools.image_gen import (  # noqa: E402, E501 import requires django setup to be run first
    StableDiffusionWrapper,
)


wrapper = StableDiffusionWrapper()
wrapper.replace_images_for_article(55, [2, 3])
del wrapper
