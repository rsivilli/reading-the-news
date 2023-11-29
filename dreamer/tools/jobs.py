from dreamer.models import DreamJob, JobStatus, JobType
from dreamer.tools.base import ContentGenerator
from datetime import datetime
from dreamer.tools import speech, image_gen, assembler

SAFETY = 1000
JOB_ORDER = [
    JobType.AUDIO_GEN_PARTIAL,
    JobType.AUDIO_GEN_FULL,
    JobType.IMAGE_GEN_PARTIAL,
    JobType.IMAGE_GEN_FULL,
    JobType.VIDEO_GEN,
]


def get_next_job(start_time: datetime, job_type: JobType | None = None):
    if job_type is None:
        return (
            DreamJob.objects.filter(job_status=JobStatus.QUEUED)
            .filter(created_time__lt=start_time)
            .order_by("-created_time", "-id")
            .first()
        )
    else:
        return (
            DreamJob.objects.filter(job_status=JobStatus.QUEUED)
            .filter(created_time__lt=start_time)
            .filter(job_type=job_type)
            .order_by("-created_time", "-id")
            .first()
        )


def get_job_handler(job_type: JobType) -> ContentGenerator:
    if (
        job_type is JobType.AUDIO_GEN_FULL
        or job_type is JobType.AUDIO_GEN_PARTIAL
    ):
        return speech.SpeechGenerator()
    elif (
        job_type is JobType.IMAGE_GEN_FULL
        or job_type is JobType.IMAGE_GEN_PARTIAL
    ):
        return image_gen.StableDiffusionWrapper()
    elif job_type is JobType.VIDEO_GEN:
        return assembler.VideoGenerator()
    else:
        raise NotImplementedError(
            f"JobType {job_type} is not currently supported"
        )


def run():
    # obtain all queued jobs (last in, first out order
    # to help with dup or old jobs)
    start_time = datetime.now()
    count = 0
    for job_type in JOB_ORDER:
        job = get_next_job(start_time, job_type)

        while job and count < SAFETY:
            handler = get_job_handler(job_type)
            try:
                handler.generate_content(job.article.id, job.job_args_dict)
                DreamJob.objects.filter(job_status=JobStatus.QUEUED).filter(
                    job_type=job.job_type
                ).filter(created_time__lt=start_time).update(
                    status_message=f"Overridden by newer job with id {job.id}",
                    job_status=JobStatus.COMPLETE_OVERRIDDEN,
                    updated_time=datetime.now(),
                )
                job.job_status = JobStatus.COMPLETE_SUCCESS
                job.status_message = None

            except Exception as e:
                job.status_message = str(e)
                job.job_status = JobStatus.COMPLETE_ERROR
                job.updated_time = datetime.now()
                raise e
            job.updated_time = datetime.now()
            job.save()
            # Do job
            job = get_next_job(start_time, job_type)
            count += 1
        if count >= SAFETY:
            raise AssertionError(
                f"Safety Count Iterator of {SAFETY} was exceeded"
            )
