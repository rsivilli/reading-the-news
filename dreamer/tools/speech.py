from transformers import AutoProcessor, AutoModel, BarkConfig,BarkModel,BarkProcessor,BarkSemanticConfig


import scipy
import datetime
import torch
from uuid import uuid4
import numpy as np

import nltk
from tqdm import tqdm
from newsfeed.models import Article
from dreamer.models import ArticleAudio

from pathlib import Path

import os


def save_audio(audio_array,output, sampling_rate):
    scipy.io.wavfile.write(output, rate=sampling_rate,data=audio_array)

class SpeechGenerator():
    def __init__(self, processor = "suno/bark", model = "suno/bark", semantic_min_eos_p=0.05,semantic_temperature=0.98) -> None:
          self.device = "cuda" if torch.cuda.is_available() else "cpu"
          self.model:BarkModel = AutoModel.from_pretrained(model).to(self.device)
          self.processor:BarkProcessor = AutoProcessor.from_pretrained(processor)
          self.semantic_min_eos_p = semantic_min_eos_p
          self.semantic_temperature = semantic_temperature

    def generate_audio(self,text,preset, silence_duration=0.25):

        inputs = self.processor(
            text=text,
            return_tensors="pt",
            voice_preset=preset,
        )
        for k,v in inputs.items():
            inputs[k] = v.to(self.device)

        start_time = datetime.datetime.now()
        speech_values = self.model.generate(
             **inputs, 
             do_sample=True,
             semantic_min_eos_p=self.semantic_min_eos_p,
             semantic_temperature = self.semantic_temperature
             )
        print(f"Time to create voice: {datetime.datetime.now()-start_time}")


        sampling_rate = self.model.generation_config.sample_rate
        silence = np.zeros(silence_duration * sampling_rate,np.float32)
        audio_array = speech_values.cpu().numpy().squeeze()
        return [audio_array, silence.copy()]

  
    def generate_and_save_audio(self,article:Article, paragraph_number:int,paragraph:str, preset="v2/en_speaker_9",audio_folder = "article_audio"):
        file_folder = Path(audio_folder)
        file_folder.mkdir(exist_ok=True)
        for p in tqdm(article.content.split("\n"),"Creating Audio"):
            
            pieces = []
            filename = Path(audio_folder,f"{uuid4().hex}.wav").as_posix()
            
            for sentence in nltk.sent_tokenize(paragraph):
                pieces += self.generate_audio(
                    sentence,preset
                )
            
            save_audio(np.concatenate(pieces),filename,self.model.generation_config.sample_rate)
            
            img_db = ArticleAudio(
                paragraph_number = paragraph_number ,
                article = article,
                location = filename
            )

            
            img_db.save()
        
    def generate_audio_for_article(self,article_id,preset="v2/en_speaker_9",audio_folder = "article_audio"):
            article = Article.objects.filter(pk=article_id).first()
            if article is None:
                raise KeyError(f"There is no article for {article}")
            
            count = 0
            self.generate_and_save_audio(article,count,preset,audio_folder)
            count += 1    
                
    def replace_audio_for_article(self,article_id, paragraph_numbers:int|list[int],preset="v2/en_speaker_9",audio_folder = "article_audio"):
        article = Article.objects.filter(pk=article_id).first()
        if article is None:
            raise KeyError(f"There is no article for {article}")
        article_paragraphs = article.content.split("\n")
        if isinstance(paragraph_numbers,int):
             paragraph_numbers = [paragraph_numbers]
        for p in paragraph_numbers:
            existing_audio = ArticleAudio.objects.filter(article__id = article_id, paragraph_number = p).first()
            if existing_audio is None:
                print(f"There is not an existing audio for Article {article_id}, Paragraph {p}")
            else:
                tmp = Path(existing_audio.location)
                if tmp.exists():
                    os.remove(existing_audio.location)
            if p > len(article_paragraphs):
                raise ValueError(f"Provided paragraph {p} number exceeds number of paragraphs in the article {len(article_paragraphs)}")
            self.generate_and_save_audio(article,p,preset,audio_folder)