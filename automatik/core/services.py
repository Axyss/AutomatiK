import importlib
import os
from importlib.metadata import Deprecated

from automatik import logger, SRC_DIR


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
                    Klass = getattr(imported_service, "Main")
                    ServiceLoader.services.append(Klass())
                except AttributeError:
                    logger.exception(f"Service '{service_name}' couldn't be loaded")
                except:
                    logger.exception(f"Unexpected error while loading service {service_name}")
        logger.info(f"{len(ServiceLoader.services)} services loaded")

    @staticmethod
    def get_service_ids():
        return [i.SERVICE_ID for i in ServiceLoader.services]

    @staticmethod
    def get_service_names():
        return [i.SERVICE_NAME for i in ServiceLoader.services]
