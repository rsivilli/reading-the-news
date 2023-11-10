import os
import django
import torch
import numpy as np
from transformers import BarkConfig,BarkCoarseConfig, BarkSemanticConfig,BarkFineConfig
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reading_the_news.settings')

django.setup()
from dreamer.tools.image_gen import StableDiffusionWrapper
from dreamer.tools.speech import SpeechGenerator
from dreamer.tools.assembler import assemble_article_content


# speech_gen = SpeechGenerator( )
# speech_gen.generate_audio_for_article(55)
# del speech_gen
wrapper = StableDiffusionWrapper()
wrapper.replace_images_for_article(55, [2,3])
del wrapper
# assemble_article_content(55)
