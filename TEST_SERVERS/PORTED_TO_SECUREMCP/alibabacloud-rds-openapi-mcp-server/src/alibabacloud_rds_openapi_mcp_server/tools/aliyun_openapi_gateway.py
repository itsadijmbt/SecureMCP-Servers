# -*- coding: utf-8 -*-
import os
import logging
from typing import Type, TypeVar, Dict, Any
from functools import wraps

# --- Core SDK Imports ---
import alibabacloud_tea_openapi.models as OpenApiModels
from alibabacloud_tea_util.models import RuntimeOptions

try:
    from alibabacloud_rds20140815.client import Client as RdsApiClient
except ImportError:
    RdsApiClient = None

try:
    from alibabacloud_ecs20140526.client import Client as EcsApiClient
except ImportError:
    EcsApiClient = None

try:
    from alibabacloud_das20200116.client import Client as DasApiClient
except ImportError:
    DasApiClient = None

logger = logging.getLogger(__name__)

# To add support for a new service, import its client and add it here.
SERVICE_CLIENT_MAP = {
    'rds': RdsApiClient,
    'ecs': EcsApiClient,
    'das': DasApiClient,
}

T = TypeVar('T')


def _api_call_wrapper(func):
    """
    A decorator that encapsulates repetitive API call logic:
    1. Provides default RuntimeOptions.
    2. Automatically calls .body.to_map() on the response.
    3. Provides unified exception logging and handling.
    """

    @wraps(func)
    def wrapper(request_model: T, runtime: RuntimeOptions = None) -> Dict[str, Any]:
        try:
            if runtime is None:
                runtime = RuntimeOptions()

            response = func(request_model, runtime)

            return response.body.to_map()
        except Exception as e:
            logger.error(f"Aliyun API call to '{func.__name__}' failed: {e}", exc_info=True)
            raise

    return wrapper


class _ServiceProxy:
    """
    A private proxy class that dynamically intercepts calls to an SDK client.
    For example, a call to proxy.describe_db_instances(...) will be forwarded
    to the real client's method, with all boilerplate logic handled automatically
    by the _api_call_wrapper.
    """

    def __init__(self, service_client):
        self._service_client = service_client

    def __getattr__(self, method_name: str):
        if hasattr(self._service_client, method_name) and callable(getattr(self._service_client, method_name)):
            actual_method = getattr(self._service_client, method_name)
            return _api_call_wrapper(actual_method)

        raise AttributeError(
            f"'{type(self._service_client).__name__}' object has no callable attribute '{method_name}'")


class AliyunServiceGateway:
    """
    hides all SDK implementation details, providing a clean, explicit, and
    discoverable interface for each service.
    """

    def __init__(self, region_id: str):
        self._config = OpenApiModels.Config(
            access_key_id=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            access_key_secret=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
            security_token=os.environ.get('ALIBABA_CLOUD_SECURITY_TOKEN'),
            region_id=region_id
        )
        self._config.validate()
        self._clients_cache: Dict[str, Any] = {}  # Cache for client instances.

    def rds(self) -> _ServiceProxy:
        """
        Provides access to RDS (ApsaraDB for RDS) service APIs.

        Returns:
            A proxy object for chain-calling RDS API methods.
        """
        return self._get_service_proxy('rds')

    def ecs(self) -> _ServiceProxy:
        """
        Provides access to ECS (Elastic Compute Service) APIs.

        Returns:
            A proxy object for chain-calling ECS API methods.
        """
        return self._get_service_proxy('ecs')

    def das(self) -> _ServiceProxy:
        """
        Provides access to DAS (Database Autonomy Service) APIs.

        Returns:
            A proxy object for chain-calling DAS API methods.
        """
        return self._get_service_proxy('das')

    def _get_service_proxy(self, service_name: str) -> _ServiceProxy:
        """
        Private method to create, cache, and wrap a service client in a proxy.
        """
        if service_name in self._clients_cache:
            client = self._clients_cache[service_name]
        else:
            client_class = SERVICE_CLIENT_MAP.get(service_name)
            if not client_class:
                raise ValueError(
                    f"Service '{service_name}' is not supported or its SDK (e.g., alibabacloud_{service_name}...) is not installed.")

            client = client_class(self._config)
            self._clients_cache[service_name] = client

        return _ServiceProxy(client)