import pytest

from earth_twin_engine.domain.temporal.temporal_resolution import (
    TemporalResolution,
)
from earth_twin_engine.domain.variables.earth_variable import EarthVariable
from earth_twin_engine.domain.variables.variable_category import VariableCategory
from earth_twin_engine.domain.variables.variable_metadata import VariableMetadata


@pytest.fixture
def temperature_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="air_temperature",
        name="Air Temperature",
        description="Near-surface atmospheric air temperature",
        category=VariableCategory.ATMOSPHERE,
        metadata=VariableMetadata(
            unit="K",
            temporal_resolutions=(
                TemporalResolution.HOURLY,
                TemporalResolution.DAILY,
            ),
            keywords=("temperature", "atmosphere", "weather"),
            source_ids=("nasa_airs", "nasa_merra2"),
        ),
    )


@pytest.fixture
def precipitation_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="precipitation",
        name="Precipitation",
        description="Accumulated precipitation over a period",
        category=VariableCategory.HYDROLOGY,
        metadata=VariableMetadata(
            unit="mm",
            temporal_resolutions=(
                TemporalResolution.DAILY,
                TemporalResolution.MONTHLY,
            ),
            keywords=("rainfall", "water", "precipitation"),
            source_ids=("nasa_gpm",),
        ),
    )


@pytest.fixture
def vegetation_variable() -> EarthVariable:
    return EarthVariable(
        variable_id="vegetation_index",
        name="Vegetation Index",
        description="Satellite-derived vegetation condition indicator",
        category=VariableCategory.BIOSPHERE,
        metadata=VariableMetadata(
            unit="index",
            temporal_resolutions=(TemporalResolution.MONTHLY,),
            keywords=("vegetation", "ndvi", "plants"),
            source_ids=("nasa_modis",),
        ),
    )
