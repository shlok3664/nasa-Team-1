"""Earth science variable discovery application module."""

from earth_twin_engine.application.modules.variable_discovery.queries import (
    DiscoverEarthVariablesQuery,
    GetEarthVariableQuery,
)
from earth_twin_engine.application.modules.variable_discovery.variable_catalog import (
    VariableCatalog,
)
from earth_twin_engine.application.modules.variable_discovery.variable_discovery_module import (
    VariableDiscoveryModule,
)

__all__ = [
    "DiscoverEarthVariablesQuery",
    "GetEarthVariableQuery",
    "VariableCatalog",
    "VariableDiscoveryModule",
]
