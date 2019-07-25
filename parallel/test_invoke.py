import os
import pytest
from redis import Redis
from rq import Worker
from .invoke import (
    DEFAULT_QUEUE_NAME,
    invoke_for_each,
    get_results,
    get_aggregate_status,
)
from .testing import square


def path_to_redis():
    import distutils.spawn

    return distutils.spawn.find_executable("redis-server")


if os.environ.get("CI"):

    @pytest.fixture
    def dummy_fixture():
        pass

    @pytest.fixture
    def conn_fixture():
        return Redis()

    new_redis_proc = dummy_fixture
    redis_conn = conn_fixture
else:
    from pytest_redis.factories import redis_proc, redisdb

    new_redis_proc = redis_proc(executable=path_to_redis(), logsdir="/tmp")
    redis_conn = redisdb("new_redis_proc")


def test_invoke_for_each(new_redis_proc, redis_conn):
    items = {"item_{}".format(i): i for i in range(10)}
    invoke_for_each(square, items, connection=redis_conn)
    assert get_aggregate_status(connection=redis_conn) == "queued"

    worker = Worker([DEFAULT_QUEUE_NAME], connection=redis_conn)
    worker.work(burst=True)

    assert get_aggregate_status(connection=redis_conn) == "finished"

    results = get_results(connection=redis_conn)
    assert results == {k: x * x for k, x in items.items()}


def test_repeat_invoke_raises_error(new_redis_proc, redis_conn):
    items = {"item_{}".format(i): i for i in range(10)}
    invoke_for_each(square, items, connection=redis_conn)
    with pytest.raises(ValueError):
        invoke_for_each(square, items, connection=redis_conn)
