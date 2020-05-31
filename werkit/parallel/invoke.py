import time

# Import redis and rq lqzily to keep them soft dependencies.


class NotReady(Exception):
    pass


DEFAULT_QUEUE_NAME = "werkit-default"
JOB_ID_SEPARATOR = "____"


def clean(queue_name=DEFAULT_QUEUE_NAME, connection=None):
    from redis import Redis
    from rq import Queue
    from rq.registry import FinishedJobRegistry, FailedJobRegistry

    queue = Queue(queue_name, connection=connection or Redis())
    queue.empty()

    for registry in [FinishedJobRegistry(queue=queue), FailedJobRegistry(queue=queue)]:
        for job_id in registry.get_job_ids():
            registry.remove(job_id)


_clean_queue = clean


def invoke_for_each(
    fn,
    items,
    connection=None,
    queue_name=DEFAULT_QUEUE_NAME,
    clean=False,
    ensure_clean=True,
    as_kwarg=None,
    job_timeout="20m",
    result_ttl_seconds=60 * 60 * 24 * 30,
    args=(),
    kwargs={},
):
    """
    Invoke the given function on each of the given items.

    If `as_kwarg` is specified, the value is passed in as a keyword arg,
    otherwise as a positional arg.

    The additional `args` and `kwargs` are also provided to the function.

    When `ensure_empty` is true, raises an exception if there are already
    jobs in the queue.
    """
    from redis import Redis
    from rq import Queue

    if clean:
        _clean_queue(queue_name=queue_name, connection=connection)

    if ensure_clean:
        jobs = get_all_jobs(connection=connection, queue_name=queue_name)
        if len(jobs) > 0:
            raise ValueError(
                "Registry has not been cleaned! {} jobs were found".format(len(jobs))
            )

    queue = Queue(queue_name, connection=connection or Redis())
    for k, item in items.items():
        enqueue_kwargs = {
            "job_timeout": job_timeout,
            "result_ttl": result_ttl_seconds,
            "failure_ttl": result_ttl_seconds,
            "description": "{} {}".format(getattr(fn, "__name__", str(fn)), str(item)),
            "job_id": "{}{}{}".format(queue_name, JOB_ID_SEPARATOR, k),
        }
        if as_kwarg:
            out_fn_kwargs = kwargs.copy()
            out_fn_kwargs[as_kwarg] = item
            queue.enqueue(fn, args=args, kwargs=out_fn_kwargs, **enqueue_kwargs)
        else:
            queue.enqueue(fn, args=(item,) + args, kwargs=kwargs, **enqueue_kwargs)


def get_all_jobs(connection=None, queue_name=DEFAULT_QUEUE_NAME):
    from redis import Redis
    from rq import Queue
    from rq.job import Job
    from rq.registry import FinishedJobRegistry, FailedJobRegistry

    queue = Queue(queue_name, connection=connection or Redis())
    queued_jobs = queue.job_ids
    finished_jobs = FinishedJobRegistry(queue=queue).get_job_ids()
    failed_jobs = FailedJobRegistry(queue=queue).get_job_ids()
    return Job.fetch_many(
        queued_jobs + finished_jobs + failed_jobs, connection=connection
    )


def get_aggregate_status(
    connection=None, queue_name=DEFAULT_QUEUE_NAME, ret_jobs=False
):
    from rq.job import JobStatus

    jobs = get_all_jobs(connection=connection, queue_name=queue_name)
    if len(jobs) == 0:
        raise ValueError("No jobs found for queue {}".format(queue_name))
    statuses = set([job.get_status() for job in jobs])

    if set([JobStatus.FINISHED, JobStatus.FAILED]).issuperset(statuses):
        aggregate_status = JobStatus.FINISHED
    elif set([JobStatus.QUEUED]).issuperset(statuses):
        aggregate_status = JobStatus.QUEUED
    elif set(
        [JobStatus.QUEUED, JobStatus.STARTED, JobStatus.FINISHED, JobStatus.FAILED]
    ).issuperset(statuses):
        aggregate_status = JobStatus.STARTED
    else:
        aggregate_status = "other"

    return (aggregate_status, jobs) if ret_jobs else aggregate_status


def get_results(wait_until_done=False, queue_name=DEFAULT_QUEUE_NAME, connection=None):
    from rq.job import JobStatus

    while True:
        status, jobs = get_aggregate_status(connection=connection, ret_jobs=True)
        if status == JobStatus.FINISHED:
            return {j.id.split(JOB_ID_SEPARATOR)[-1]: j.result for j in jobs}
        elif wait_until_done:
            print("Status is {}; sleeping for {} seconds")
            time.sleep(30)
            continue
        else:
            raise NotReady()
