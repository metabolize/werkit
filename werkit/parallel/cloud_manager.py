from __future__ import print_function
from executor import execute
from .invoke import DEFAULT_QUEUE_NAME


class Config(object):
    def __init__(
        self,
        local_repository=None,
        aws_region="us-east-1",
        ecr_repository=None,
        ecs_task_name="werkit-default",
        task_args=None,
        default_task_count=1,
        redis_url=None,
        queue_name=DEFAULT_QUEUE_NAME,
    ):
        self.local_repository = local_repository
        self.aws_region = aws_region
        self.ecr_repository = ecr_repository
        self.ecs_task_name = ecs_task_name
        self.task_args = task_args
        self.default_task_count = default_task_count
        self.redis_url = redis_url
        self.queue_name = queue_name


class CloudManager(object):
    def __init__(self, config):
        if not isinstance(config, Config):
            raise ValueError("Should be an instance of Config")
        self.config = config

    @property
    def redis_url(self):
        import os

        return self.config.redis_url or os.environ["WERKIT_REDIS_URL"]

    @property
    def redis_connection(self):
        from redis import Redis

        return Redis.from_url(self.redis_url)

    def login(self):
        login_cmd = execute(
            "aws",
            "ecr",
            "get-login",
            "--region",
            self.config.aws_region,
            "--no-include-email",
            capture=True,
        )
        execute(login_cmd)

    def remote_tag(self, tag):
        return "{}:{}".format(self.config.ecr_repository, tag)

    def build_and_push(self, tag):
        local_tag = "{}:{}".format(self.config.local_repository, tag)

        execute("docker", "build", "-f", "Dockerfile-rq.dev", ".", "--tag", local_tag)
        execute("docker", "tag", local_tag, self.remote_tag(tag))
        execute("docker", "push", self.remote_tag(tag))

    def clean(self):
        from .invoke import clean as _clean

        _clean(queue_name=self.config.queue_name, connection=self.redis_connection)

    def run(self, tag, count=None):
        if count is None:
            count = self.config.default_task_count
        execute(
            "fargate",
            "task",
            "run",
            self.config.ecs_task_name,
            "--image",
            self.remote_tag(tag),
            "--num",
            str(count),
            "--env",
            "REDIS_URL={}".format(self.config.redis_url),
            *self.config.task_args
        )

    def dashboard(self):
        execute(
            "rq-dashboard", "--bind", "localhost", "--redis-url", self.config.redis_url
        )

    def ps(self):
        execute("fargate", "task", "ps", self.config.ecs_task_name)

    def get_results(self, wait_until_done=False):
        from .invoke import get_results as _get_results

        return _get_results(
            wait_until_done=wait_until_done,
            queue_name=self.config.queue_name,
            connection=self.redis_connection,
        )
