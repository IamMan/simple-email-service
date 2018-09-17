import abc

from .helpers import LambdaEventWrapper, Response


class Handler:
    @abc.abstractmethod
    def handle(self, event: LambdaEventWrapper) -> Response:
        pass
