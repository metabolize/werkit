import typing as t

# Force some libraries to be imported right away. This keeps the execution time
# of the first Lambda invocation consistent with the subsequent execution.
# Otherwise developers users would have to put a big buffer into the timeout
import rds_graphile_worker_client  # noqa: F401
from werkit.compute import Destination


_graphile_worker_client = None


def get_graphile_worker_client(
    debug: bool = False,
) -> rds_graphile_worker_client.RdsGraphileWorkerClient:
    import os
    from rds_graphile_worker_client import RdsGraphileWorkerClient

    global _graphile_worker_client
    if not _graphile_worker_client:  # pragma: no cover
        config_kwargs = {
            "aws_region": os.environ["AWS_REGION"],
            "pg_username": os.environ["RDS_GRAPHILE_WORKER_PG_USERNAME"],
            "pg_hostname": os.environ["RDS_GRAPHILE_WORKER_PG_HOSTNAME"],
            "pg_port": os.environ["RDS_GRAPHILE_WORKER_PG_PORT"],
            "pg_dbname": os.environ["RDS_GRAPHILE_WORKER_PG_DBNAME"],
        }
        if debug:
            print(f"config_kwargs: {config_kwargs}")
        _graphile_worker_client = RdsGraphileWorkerClient(**config_kwargs)

    return _graphile_worker_client


class RdsGraphileWorkerDestination(Destination):
    def __init__(self, function_name: str, debug: bool = False):
        self.function_name = function_name
        self.debug = debug

    # TODO: Use a cached property. Tricky because we're using a fork of
    # cachedproperty.
    @property
    def queue_client(self) -> rds_graphile_worker_client.RdsGraphileWorkerClient:
        return get_graphile_worker_client(debug=self.debug)

    def debug_queue_message(self) -> None:  # pragma: no cover
        cursor = self.queue_client.conn.cursor()
        try:
            cursor.execute("SELECT * from graphile_worker.jobs")
            column_names = [desc[0] for desc in cursor.description]
            values = cursor.fetchall()
        finally:
            cursor.close()
        result = [dict(zip(column_names, these_values)) for these_values in values]
        print(result)

    def send(self, message_key: t.Any, output_message: t.Any) -> None:
        response = self.queue_client.quick_add_job(self.function_name, output_message)
        print("rds response", response)

        if self.debug:  # pragma: no cover
            self.debug_queue_message()
