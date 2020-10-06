
class HealthChecker:
    """
    Performs regular checks for healthiness.

    Given a set of HealthCheck descriptors it will
    probe them (through HTTP) regularly.
    """

    def __init__(self, checks, handler):
        """
        Creates a new HealthChecker.

        The provided checks must be an iterable of HealthCheck, including
        all the information required to do probing for healthiness.

        The provided handler must be a coroutine (awaitable) that will
        receive the as parameters:

        - url : The url that has been probed
        - status: A health.status.HealthStatus

        The handler will be responsible for handling results for all the
        provided health check targets.
        """
        self.__checks = checks
        self.__handler = handler

    def start(self):
        """
        Starts to periodically check for healthiness.

        This method should be called only once. Calling it
        will start multiple asynchronous tasks that
        will periodically probe HTTP endpoints and call
        a handler with the results.
        """
        pass
