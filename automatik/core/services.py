import importlib
import os

from automatik import logger, SRC_DIR
from automatik.core.base_service import BaseService


class ServiceLoader:
    services = []

    @staticmethod
    def load_services():
        """Instantiates the 'Main' class of each service and appends said instance to 'ServiceLoader.services'"""
        ServiceLoader.services = []  # Avoids service duplication after reload
        for i in os.listdir(os.path.join(SRC_DIR, "services")):
            service_name, service_extension = os.path.splitext(i)

            if service_extension == ".py" and service_name != "__init__":
                try:
                    imported_service = importlib.import_module(f"automatik.services.{service_name}")
                    # Creates an instance of the Main class of the imported service
                    Klass = getattr(imported_service, "Service")
                    ServiceLoader.services.append(Klass())
                    logger.debug(f"Service '{service_name}' loaded successfully")
                except AttributeError:
                    logger.exception(f"Service '{service_name}' could not be loaded (missing 'Service' class)")
                except:
                    logger.exception(f"Service '{service_name}' could not be loaded due to an unexpected error")
        logger.info(f"{len(ServiceLoader.services)} service(s) loaded: {[s.SERVICE_ID for s in ServiceLoader.services]}")

    @staticmethod
    def get_service_ids():
        return [i.SERVICE_ID for i in ServiceLoader.services]

    @staticmethod
    def get_service(service_id) -> BaseService | None:
        for service in ServiceLoader.services:
            if service.SERVICE_ID == service_id:
                return service
        return None
