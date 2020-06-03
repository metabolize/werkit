import os
import pytest
from redis import Redis
from rq import Worker
from .invoke import (
    DEFAULT_QUEUE_NAME,
    clean,
    get_aggregate_status,
    get_results,
    invoke_for_each,
)
from .testing import multiply, square


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

    Worker([DEFAULT_QUEUE_NAME], connection=redis_conn).work(burst=True)

    assert get_aggregate_status(connection=redis_conn) == "finished"

    assert get_results(connection=redis_conn) == {k: x * x for k, x in items.items()}


def test_repeat_invoke_raises_error(new_redis_proc, redis_conn):
    items = {"item_{}".format(i): i for i in range(10)}

    clean(connection=redis_conn)

    invoke_for_each(square, items, connection=redis_conn)
    with pytest.raises(ValueError):
        invoke_for_each(square, items, connection=redis_conn)


def test_invoke_for_each_with_kwargs(new_redis_proc, redis_conn):
    items = {"item_{}".format(i): i for i in range(10)}
    invoke_for_each(
        multiply, items, kwargs={"multiplier": 5}, clean=True, connection=redis_conn
    )

    Worker([DEFAULT_QUEUE_NAME], connection=redis_conn).work(burst=True)

    assert get_results(connection=redis_conn) == {k: 5 * x for k, x in items.items()}
