from redis import Redis

from tests.functional.utils.backoff import backoff


@backoff()
def ping_remote_service_host(
    service: Redis,
    service_name: str,
) -> None:
    """Проверяет связь с хостом заданного сервиса.

    Функция обернута в backoff. Таким образом проверка связи будет итеративной.

    Args:
        service ( Redis): объект клиента сервиса.
        service_name (str): название сервиса.

    Raises:
        ConnectionError: если сервис не доступен.
    """
    if not service.ping():
        raise ConnectionError(f'Failed to connect with {service_name}...')
