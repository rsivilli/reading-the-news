from dreamer.models import ArticleAudio, ArticleImage, ArticleVideo
from newsfeed.models import Article

from PIL import Image
import imageio
from moviepy import editor
from pathlib import Path
from uuid import uuid4
from tqdm import tqdm

from django.db.models import Manager


def get_audio_files(
    article_id: int, order_by="paragraph_number"
) -> Manager[ArticleAudio]:
    return (
        ArticleAudio.objects.filter(article__id=article_id)
        .all()
        .order_by(order_by)
    )


def get_image_files(
    article_id: int, order_by="paragraph_number"
) -> Manager[ArticleImage]:
    return (
        ArticleImage.objects.filter(article__id=article_id)
        .order_by(order_by)
        .all()
    )


def assemble_article_content(
    article_id: int,
    build_directory: str = "tmp",
    save_directory: str = "article_video",
) -> None:
    article = Article.objects.get(pk=article_id)
    audio_files = get_audio_files(article_id)
    image_files = get_image_files(article_id)
    if len(audio_files) != len(image_files):
        raise ValueError(
            f"There are a difference number of audio files ({len(audio_files)}) than image files ({len(image_files)}) for artcile {article_id}"  # noqa: E501
        )
    # combine image/audio segments into video clips
    files = []
    for i in tqdm(range(len(audio_files)), "Converting to clips"):
        audio = editor.AudioFileClip(audio_files[i].location)

        image = Image.open(image_files[i].image_location)
        Path(build_directory).mkdir(exist_ok=True)
        tmp_guid = uuid4()
        gif_file = Path(build_directory, f"{tmp_guid}.gif").as_posix()
        video_file = Path(build_directory, f"{tmp_guid}.mp4").as_posix()
        imageio.mimsave(gif_file, [image], fps=1 / audio.duration)

        video = editor.VideoFileClip(gif_file)
        final_video: editor.VideoFileClip = video.set_audio(audio)
        final_video.write_videofile(
            fps=60, codec="libx264", filename=video_file
        )
        files.append(video_file)

    clips = [editor.VideoFileClip(f) for f in files]

    full_video = editor.concatenate_videoclips(clips)

    full_video_location = Path(save_directory, f"{uuid4()}.mp4").as_posix()
    full_video.write_videofile(full_video_location)

    ArticleVideo(location=full_video_location, article=article)

    # concat clips
