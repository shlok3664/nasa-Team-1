"""Constructs and launches the Earth Twin Engine application."""

from __future__ import annotations

from earth_twin_engine.application.commands import CommandDispatcher
from earth_twin_engine.application.core.application_configuration import (
    ApplicationConfiguration,
)
from earth_twin_engine.application.core.application_context import (
    ApplicationContext,
)
from earth_twin_engine.application.core.module_manager import ModuleManager
from earth_twin_engine.application.core.service_registry import ServiceRegistry
from earth_twin_engine.application.error_handling import ApplicationErrorHandler
from earth_twin_engine.application.events import EventDispatcher
from earth_twin_engine.application.launcher.configuration_loader import (
    ApplicationConfigurationLoader,
)
from earth_twin_engine.application.logging import (
    LoggerFactory,
    LoggingConfiguration,
    LogLevel,
)
from earth_twin_engine.application.queries import QueryDispatcher
from earth_twin_engine.application.resource_management import ResourceManager
from earth_twin_engine.application.runtime import ApplicationRuntime


class ApplicationLauncher:
    """Builds the application services, context, and runtime."""

    def __init__(
        self,
        configuration: ApplicationConfiguration,
        module_manager: ModuleManager | None = None,
    ) -> None:
        if not isinstance(configuration, ApplicationConfiguration):
            raise TypeError("configuration must be an ApplicationConfiguration")

        if module_manager is not None and not isinstance(module_manager, ModuleManager):
            raise TypeError("module_manager must be a ModuleManager or None")

        self._configuration = configuration
        self._module_manager = module_manager if module_manager is not None else ModuleManager()
        self._service_registry = ServiceRegistry()
        self._resource_manager = ResourceManager()
        self._event_dispatcher = EventDispatcher()
        self._command_dispatcher = CommandDispatcher()
        self._query_dispatcher = QueryDispatcher()
        self._error_handler = ApplicationErrorHandler()

        log_level = LogLevel.DEBUG if configuration.debug else LogLevel.INFO
        logging_configuration = LoggingConfiguration(level=log_level)
        self._logger_factory = LoggerFactory(logging_configuration)

        self._service_registry.register(ModuleManager, self._module_manager)
        self._service_registry.register(ResourceManager, self._resource_manager)
        self._service_registry.register(EventDispatcher, self._event_dispatcher)
        self._service_registry.register(CommandDispatcher, self._command_dispatcher)
        self._service_registry.register(QueryDispatcher, self._query_dispatcher)
        self._service_registry.register(ApplicationErrorHandler, self._error_handler)
        self._service_registry.register(LoggerFactory, self._logger_factory)

        self._context = ApplicationContext(
            configuration=self._configuration,
            services=self._service_registry,
        )

        self._runtime = ApplicationRuntime(
            module_manager=self._module_manager,
            context=self._context,
            resource_manager=self._resource_manager,
        )

    @property
    def context(self) -> ApplicationContext:
        """Application context containing registered services."""
        return self._context

    @property
    def runtime(self) -> ApplicationRuntime:
        """Application runtime managed by this launcher."""
        return self._runtime

    @property
    def module_manager(self) -> ModuleManager:
        """Module manager used by the application."""
        return self._module_manager

    @property
    def event_dispatcher(self) -> EventDispatcher:
        """Shared application event dispatcher."""
        return self._event_dispatcher

    @property
    def command_dispatcher(self) -> CommandDispatcher:
        """Shared application command dispatcher."""
        return self._command_dispatcher

    @property
    def query_dispatcher(self) -> QueryDispatcher:
        """Shared application query dispatcher."""
        return self._query_dispatcher

    def launch(self) -> ApplicationRuntime:
        """Initialize and start the application."""

        try:
            self._runtime.initialize()
            self._runtime.start()
        except Exception:
            self._runtime.shutdown()
            raise

        return self._runtime

    @classmethod
    def from_configuration_file(
        cls,
        config_path: str | None = None,
        environ: dict[str, str] | None = None,
    ) -> ApplicationLauncher:
        """Construct a launcher using a JSON configuration file."""

        loader = ApplicationConfigurationLoader()
        configuration = loader.load(
            config_path=config_path,
            environ=environ,
        )

        return cls(configuration)
