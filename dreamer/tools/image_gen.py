import torch
from diffusers import (
    StableDiffusionXLPipeline,
)
from dreamer.models import ArticleImage
from newsfeed.models import Article
from uuid import uuid4
from pathlib import Path
from tqdm import tqdm
import os


class StableDiffusionWrapper:
    def __init__(
        self,
        model_path: str
        | Path = Path(
            "models", "stablediffusion", "sdXL_v10VAEFix.safetensors"
        ),
        lora: str
        | Path = Path(
            "models", "lora", "Felt-Puppet-base-v1-000008.safetensors"
        ),
    ) -> None:
        lora = Path(lora)
        if not lora.exists():
            raise FileNotFoundError(f"Could not find lora {lora.as_posix()}")
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Could not find model {model_path.as_posix()}"
            )
        self.pipe = StableDiffusionXLPipeline.from_single_file(
            model_path.as_posix(),
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
        ).to("cuda")
        self.pipe.enable_model_cpu_offload()
        # scheduler = DPMSolverMultistepScheduler.from_config(
        #   self.pipe.scheduler.config,
        #   algorithm_type="sde-dpmsolver++",
        #   use_karras_sigmas=True
        # )
        # self.pipe.scheduler = scheduler
        self.pipe.load_lora_weights(lora.as_posix())
        self.pipe.fuse_lora(lora_scale=0.85)
        # not supported by windows
        # self.pipe = torch.compile(
        #   self.pipe.unet,
        #   mode="reduce-overhead",
        #   fullgraph=True
        # )

    def generate_image_from_prompt(self, prompt: str):
        return self.pipe(
            prompt=" in a felt puppet world style," + prompt,
            negative_prompt="(deformed, bad quality, sketch, depth of field, blurry:1.1), grainy, bad anatomy, bad perspective, old, ugly, bad propotions",  # noqa: E501
            num_inference_steps=30,
        ).images[0]

    def generate_images_for_article(self, article_id, delete_existing=False):
        article = Article.objects.filter(pk=article_id).first()
        if article is None:
            raise KeyError(f"There is no article for {article}")
        existing_images = ArticleImage.objects.filter(article__id=article_id)
        if len(existing_images) > 0 and not delete_existing:
            raise ValueError(
                "There are existing images for this article. Either use the replace method or change delete_existing to true"  # noqa: E501
            )
        existing_images.delete()
        count = 0
        for p in tqdm(article.content.split("\n"), "Creating Images"):
            self.generate_and_save_image(
                prompt=p, article=article, paragraph_number=count
            )
            count += 1

    def generate_and_save_image(
        self,
        prompt: str,
        article: Article,
        paragraph_number: int,
        base_path: str = "article_pictures",
    ):
        img = self.generate_image_from_prompt(
            prompt=prompt,
        )
        img_path = Path(base_path, f"{uuid4().hex}.png")
        img.save(img_path)

        img_db = ArticleImage(
            paragraph_number=paragraph_number,
            article=article,
            image_location=img_path,
        )

        img_db.save()

    def replace_images_for_article(
        self, article_id: int, paragraphs: int | list[int]
    ):
        if isinstance(paragraphs, int):
            paragraphs = [paragraphs]
        article = Article.objects.filter(pk=article_id).first()

        article_paragraphs = article.content.split("\n")
        if article is None:
            raise KeyError(f"There is no article for {article}")

        for p in paragraphs:
            if p > len(article_paragraphs):
                raise ValueError(
                    f"Provided paragraph {p} number exceeds number of paragraphs in the article {len(article_paragraphs)}"  # noqa: E501
                )
            prompt = article_paragraphs[p]
            existing_image = ArticleImage.objects.filter(
                article__id=article_id, paragraph_number=p
            ).first()
            if existing_image is None:
                print(
                    f"There is not an existing image for Article {article_id}, Paragraph {p}"  # noqa: E501
                )
            else:
                tmp = Path(existing_image.image_location)
                if tmp.exists():
                    os.remove(existing_image.image_location)

                existing_image.delete()
            self.generate_and_save_image(
                prompt=prompt, article=article, paragraph_number=p
            )


if __name__ == "__main__":
    wrapper = StableDiffusionWrapper()
    wrapper.generate_images_for_article(1)
