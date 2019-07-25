import time

try:
    from redis import Redis
    from rq import Queue
    from rq.job import Job, JobStatus
except ImportError:
    Redis = None
    Queue = None
    Job = None
    JobStatus = None


def check_dependencies():
    if Redis is None or Queue is None:
        raise ImportError(
            "Parallel functionality requires redis and rq modules to be installed"
        )


class NotReady(Exception):
    pass


DEFAULT_QUEUE_NAME = "werkit-default"


def _queue(queue_name, rq_kwargs):
    check_dependencies()

    out_rq_kwargs = rq_kwargs.copy()
    if "connection" not in out_rq_kwargs:
        out_rq_kwargs.update(connection=Redis())
    return Queue(queue_name, **out_rq_kwargs)


def invoke_for_each(
    fn,
    items,
    connection=None,
    queue_name=DEFAULT_QUEUE_NAME,
    ensure_empty=True,
    force_empty=False,
    as_kwarg=None,
    job_timeout="20m",
    result_ttl_seconds=60 * 60 * 24 * 30,
    *args,
    **kwargs
):
    """
    Invoke the given function on each of the given items.
    
    If `as_kwarg` is specified, the value is passed in as a keyword arg,
    otherwise as a positional arg.
    
    The additional `args` and `kwargs` are also provided to the function.

    When `ensure_empty` is true, raises an exception if there are already
    jobs in the queue.
    """
    check_dependencies()

    queue = Queue(queue_name, connection=connection)

    if force_empty:
        queue.empty()

    if ensure_empty:
        if len(queue) > 0:
            raise ValueError(
                "Queue is not empty! There are {} jobs waiting".format(len(queue))
            )

    job_ids = []
    for item in items:
        enqueue_kwargs = {
            "job_timeout": job_timeout,
            "result_ttl": result_ttl_seconds,
            "failure_ttl": result_ttl_seconds,
            "description": "{} {}".format(getattr(fn, "__name__", str(fn)), str(item)),
        }
        if as_kwarg:
            out_fn_kwargs = kwargs.copy()
            out_fn_kwargs[as_kwarg] = item
            job = queue.enqueue(fn, args=args, kwargs=out_fn_kwargs, **enqueue_kwargs)
        else:
            job = queue.enqueue(
                fn, args=(item,) + args, kwargs=kwargs, **enqueue_kwargs
            )
        job_ids.append(job.id)
    return job_ids


def get_aggregate_status(job_ids, connection=None, ret_jobs=False):
    check_dependencies()

    if len(job_ids) == 0:
        raise ValueError("At least one job ID is required")

    connection = connection or Redis()
    jobs = Job.fetch_many(job_ids, connection=connection)
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


def get_results(job_ids, wait_until_done=False, connection=None):
    check_dependencies()

    while True:
        status, jobs = get_aggregate_status(
            job_ids=job_ids, connection=connection, ret_jobs=True
        )
        if status == JobStatus.FINISHED:
            return [j.result for j in jobs]
        elif wait_until_done:
            print("Status is {}; sleeping for {} seconds")
            time.sleep(30)
            continue
        else:
            raise NotReady()
