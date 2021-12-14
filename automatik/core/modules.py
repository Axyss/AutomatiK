import importlib
import os

from automatik import logger, SRC_DIR


class ModuleLoader:
    modules = []

    @staticmethod
    def load_modules():
        """Instantiates the 'Main' class of each module and appends said instance to 'ModuleLoader.modules'"""
        ModuleLoader.modules = []  # Avoids module duplication after reload
        for i in os.listdir(os.path.join(SRC_DIR, "modules")):
            module_name, module_extension = os.path.splitext(i)

            if module_extension == ".py" and module_name != "__init__":
                try:
                    imported_module = importlib.import_module(f"automatik.modules.{module_name}")
                    # Creates an instance of the Main class of the imported module
                    Klass = getattr(imported_module, "Main")
                    ModuleLoader.modules.append(Klass())
                except AttributeError:
                    logger.exception(f"Module '{module_name}' couldn't be loaded")
                except:
                    logger.exception(f"Unexpected error while loading module {module_name}")
        logger.info(f"{len(ModuleLoader.modules)} modules loaded")

    @staticmethod
    def get_module_ids():
        return [i.MODULE_ID for i in ModuleLoader.modules]

    @staticmethod
    def get_service_names():
        return [i.SERVICE_NAME for i in ModuleLoader.modules]

    @staticmethod
    def get_module_authors():
        return [i.SERVICE_NAME for i in ModuleLoader.modules]
