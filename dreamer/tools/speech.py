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




def save_audio(audio_array,output, sampling_rate):
    scipy.io.wavfile.write(output, rate=sampling_rate,data=audio_array)

class SpeechGenerator():
    def __init__(self, processor = "suno/bark", model = "suno/bark", semantic_min_eos_p=0.05,semantic_temperature=0.98) -> None:
          self.device = "cuda" if torch.cuda.is_available() else "cpu"
          self.model:BarkModel = AutoModel.from_pretrained(model).to(self.device)
          self.processor:BarkProcessor = AutoProcessor.from_pretrained(processor)
          self.semantic_min_eos_p = semantic_min_eos_p
          self.semantic_temperature = semantic_temperature

    def generate_audio(self,text,preset):

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
        silence = np.zeros(int(0.25 * sampling_rate),np.float32)
        audio_array = speech_values.cpu().numpy().squeeze()
        return [audio_array, silence.copy()]

  
        
        
    def generate_audio_for_article(self,article_id,preset="v2/en_speaker_9"):
            article = Article.objects.filter(pk=article_id).first()
            if article is None:
                raise KeyError(f"There is no article for {article}")
            
            count = 0
            
            for p in tqdm(article.content.split("\n"),"Creating Audio"):
                pieces = []
                filename = f"article_audio/{uuid4().hex}.wav"
                for sentence in nltk.sent_tokenize(p):
                    pieces += self.generate_audio(
                        sentence,preset
                    )
                
                save_audio(np.concatenate(pieces),filename,self.model.generation_config.sample_rate)
                img_db = ArticleAudio(
                    paragraph_number = count ,
                    article = article,
                    location = filename
                )

                
                img_db.save()
                count += 1    
                

