# Earth Twin Engine — Earth Systems Trend Detection and Analysis Platform

> **Challenge:** Be an Earth Systems Trend Detective!  
> **Organization:** NASA Space Apps Challenge  
> **Project:** Earth Twin Engine  
> **Working Name:** Earth Twin Engine  
> **Architecture:** Modular, Actor-Oriented Architecture  
> **Status:** Initial Project Foundation

---

# 1. Project Overview

Earth Twin Engine is a modular Earth science data exploration, trend detection, and statistical analysis platform designed to help users understand how Earth's interconnected environmental systems change over time.

Earth science missions and global models generate enormous quantities of environmental data. These datasets contain variables describing the atmosphere, oceans, land, hydrological systems, and other components of the Earth system.

However, identifying meaningful trends within these datasets is not straightforward.

A variable may increase in one geographical region while decreasing in another, even when the same underlying environmental process contributes to both observations.

The challenge is therefore not simply to visualize environmental measurements. It is to identify variables of interest, acquire their data for specific regions, construct sufficiently long time series, determine the direction and magnitude of change, and establish whether the observed trend is statistically significant.

Earth Twin Engine aims to provide a unified environment for this complete workflow.

The platform will allow users to discover Earth science variables, select geographical regions, retrieve observations or model-derived data, analyze temporal changes, and explore the resulting trends through interactive visualizations.

The application is designed around independent modules so that new data sources, scientific variables, statistical methods, and visualization capabilities can be integrated without restructuring the entire system.

# 2. Problem Statement

**Be an Earth Systems Trend Detective!**

Change is continuously occurring throughout Earth's interconnected environmental systems.

Measured Earth science variables can exhibit increasing or decreasing trends over time. However, these trends may differ across geographical regions.

The NASA challenge identifies several difficulties:

- The enormous number of available Earth science variables.
- Identifying variables that could indicate meaningful environmental change.
- Acquiring data for specific geographical regions.
- Generating sufficiently long time series.
- Understanding the direction and magnitude of change.
- Determining whether an observed trend is statistically significant.
- Interpreting regional differences in the context of Earth's interconnected systems.

Earth Twin Engine addresses these difficulties by providing a unified workflow for variable discovery, regional data acquisition, time-series visualization, and statistical trend analysis.

# 3. Core Objectives

The platform is designed around five primary objectives.

## 3.1 Earth Science Variable Discovery

Provide a structured environment for discovering variables measured by Earth science missions or produced by Earth science models.

Initial examples include:

- Temperature.
- Rainfall and precipitation.
- Evaporation.
- Streamflow.
- Atmospheric composition.
- Ocean-related variables.
- Land and hydrological variables.

The system should provide understandable descriptions, units, temporal resolution, spatial coverage, and source information for each variable.

## 3.2 Regional Data Acquisition

Allow users to select a geographical region and retrieve the corresponding data for a selected variable.

Regional selection should support:

- Geographic coordinates.
- Bounding boxes.
- Map-based region selection.
- Named geographical regions where supported.

The platform must preserve the spatial context of acquired observations.

## 3.3 Time-Series Generation

Generate time series for selected variables and regions over an appropriate period.

The system should support daily and monthly datasets initially, while allowing other temporal resolutions to be introduced.

Time-series generation should account for:

- Temporal coverage.
- Missing observations.
- Data quality.
- Spatial aggregation.
- Temporal aggregation.
- Seasonal patterns.
- Source metadata.

## 3.4 Statistical Trend Analysis

Determine:

- Whether a variable is increasing or decreasing.
- The rate of change over time.
- The magnitude of the observed change.
- Whether the trend is statistically significant.
- The uncertainty associated with the estimated trend.

Initial statistical methods should include:

- Linear regression.
- t-tests where their assumptions are appropriate.
- Mann-Kendall trend testing.
- Confidence intervals.

The analysis engine should clearly distinguish between a detected trend and a statistically significant trend.

## 3.5 Interactive Visualization

Present the analysis through accessible visualizations.

The interface should support:

- Time-series charts.
- Geographical maps.
- Regional comparisons.
- Increasing and decreasing trend indicators.
- Statistical significance indicators.
- Trend magnitude.
- Analysis metadata.
- Explanations of scientific variables.

# 4. Architectural Vision

Earth Twin Engine is designed as a modular scientific application rather than a monolithic dashboard.

The application is divided into independent subsystems with clearly defined responsibilities.

The runtime coordinates module initialization, communication, data exchange, and application lifecycle.

Each module owns its internal implementation and state.

Modules communicate through defined interfaces, commands, events, and responses rather than directly modifying one another's internal data.

The architecture should support future expansion into additional Earth system domains and more advanced scientific analysis.

# 5. System Architecture

```text
                  EARTH TWIN ENGINE
                          |
                          v
                 APPLICATION RUNTIME
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
   MODULE MANAGER    EVENT SYSTEM     RESOURCE MANAGER
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                 SCIENTIFIC DATA LAYER
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
 VARIABLE CATALOG   DATA SOURCE MANAGER   REGION MANAGER
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                  DATA PROCESSING
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
 DATA ACQUISITION   DATA VALIDATION   NORMALIZATION
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                 TIME-SERIES ENGINE
                          |
                          v
                  TREND ANALYSIS
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
 LINEAR REGRESSION   SIGNIFICANCE TESTS   UNCERTAINTY
        |                 |                 |
        +-----------------+-----------------+
                          |
                          v
                 VISUALIZATION RUNTIME
                          |
        +-----------------+-----------------+
        |                 |                 |
        v                 v                 v
    TIME SERIES       GEOGRAPHIC MAPS    TREND REPORTS
```

# 6. Modular Runtime Architecture

## 6.1 Application Core

**Responsibility:** Own the application lifecycle and provide the foundational runtime environment.

Components:

- Application Launcher.
- Application Context.
- Configuration Manager.
- Module Manager.
- Dependency Resolver.
- Event Dispatcher.
- Resource Manager.
- Logging System.
- Error Handler.

The Application Core should remain independent of Earth science calculations and visualization implementations.

## 6.2 Module Manager

**Responsibility:** Manage the lifecycle of independent application modules.

Every module should implement a common lifecycle contract.

```text
Module
 ├── Register()
 ├── Initialize(Context)
 ├── Start()
 ├── Update(DeltaTime)
 ├── Stop()
 └── Shutdown()
```

The Module Manager should:

- Register available modules.
- Validate module dependencies.
- Resolve initialization order.
- Initialize modules.
- Start and stop modules.
- Handle module failures.
- Release module-owned resources.

A module should be replaceable without requiring unrelated modules to be rewritten.

## 6.3 Actor-Oriented Communication

The application should use an actor-oriented communication model.

Each subsystem owns its internal state and processes commands or events through a defined interface.

Example:

```text
Variable Discovery Module
          |
          | Variable Selected
          v
      Event System
          |
          v
Data Acquisition Module
          |
          | Data Retrieval Request
          v
    Data Source Manager
          |
          | Dataset Retrieved
          v
    Data Processing Module
```

Communication should support:

- Commands.
- Events.
- Responses.
- Correlation identifiers.
- Error reporting.
- Asynchronous operations.
- Cancellation for supported long-running operations.

The initial implementation may run all modules within one process. Actor-oriented boundaries do not require separate operating-system processes.

# 7. Functional Modules

## 7.1 Variable Discovery Module

**Responsibility:** Discover and describe available Earth science variables.

Capabilities:

- Variable catalog.
- Variable metadata.
- Scientific descriptions.
- Units.
- Temporal resolution.
- Spatial resolution.
- Available time ranges.
- Data source identification.
- Search and filtering.

The module should provide a normalized catalog independent of the underlying data providers.

## 7.2 Data Source Manager

**Responsibility:** Coordinate connections to external Earth science data resources.

Potential initial integrations include:

- MODIS.
- OMI.
- AIRS.
- GPM.
- MERRA-2.
- GLDAS.

The exact datasets and access methods should be selected according to variable requirements and data availability.

Capabilities:

- Data source registration.
- Provider adapters.
- Request routing.
- Data retrieval.
- Source metadata.
- Availability checking.
- Error handling.
- Caching.
- Provenance tracking.

Each external resource should be accessed through its own adapter.

## 7.3 Region Manager

**Responsibility:** Represent and manage geographical regions selected for analysis.

Capabilities:

- Coordinate-based selection.
- Bounding-box selection.
- Map-based region selection.
- Named region selection.
- Geographic validation.
- Region metadata.
- Spatial boundaries.

A region should have a consistent internal representation so that different data providers can use the same geographical request.

## 7.4 Data Acquisition Module

**Responsibility:** Retrieve the selected variable for the selected geographical region and time range.

Capabilities:

- Construct data requests.
- Resolve data source requirements.
- Retrieve observations or model-derived data.
- Handle temporal ranges.
- Handle spatial subsets.
- Report retrieval progress.
- Handle failed requests.
- Preserve original source metadata.

The module should not perform statistical analysis or visualization.

## 7.5 Data Validation Module

**Responsibility:** Ensure retrieved data is suitable for downstream processing.

Capabilities:

- Missing-value detection.
- Invalid-value detection.
- Unit validation.
- Temporal consistency checks.
- Spatial consistency checks.
- Data quality metadata.
- Duplicate observation detection where applicable.

Validation should not silently remove or modify observations without recording the transformation.

## 7.6 Data Normalization Module

**Responsibility:** Convert provider-specific data into a common internal representation.

Capabilities:

- Variable normalization.
- Unit normalization.
- Timestamp normalization.
- Coordinate normalization.
- Metadata extraction.
- Source provenance.
- Standardized data contracts.

The original source values and metadata should remain traceable.

## 7.7 Time-Series Engine

**Responsibility:** Generate time series from spatially and temporally selected environmental data.

Capabilities:

- Temporal aggregation.
- Spatial aggregation.
- Daily and monthly time series.
- Regional averages.
- Regional statistics.
- Missing-period identification.
- Time-range validation.
- Seasonal information.

The engine should retain the relationship between each time-series value and its original geographical and temporal context.

Different aggregation methods should be explicitly identified rather than treated as interchangeable.

## 7.8 Trend Analysis Module

**Responsibility:** Detect and quantify temporal trends.

Capabilities:

- Increasing trend detection.
- Decreasing trend detection.
- Linear regression.
- Slope calculation.
- Rate-of-change calculation.
- Trend magnitude.
- Confidence intervals.
- Statistical significance.

The module should expose a common analysis interface so additional statistical methods can be integrated independently.

## 7.9 Statistical Testing Module

**Responsibility:** Evaluate whether observed trends are statistically significant.

Initial methods:

- t-test where appropriate.
- Mann-Kendall test.
- Confidence intervals.

The module should report:

- Test method.
- Test statistic.
- p-value where applicable.
- Significance threshold.
- Confidence interval.
- Sample size.
- Assumptions and limitations.

Statistical significance should not be confused with environmental importance or causation.

The system should also identify when data quality, sample size, or temporal coverage limits the reliability of a conclusion.

## 7.10 Regional Comparison Module

**Responsibility:** Compare trends across multiple geographical regions.

This module is particularly important because the challenge highlights that the same variable can trend in opposite directions across different regions.

Capabilities:

- Multiple-region comparison.
- Regional slope comparison.
- Increasing and decreasing regions.
- Spatial trend visualization.
- Regional statistical significance.
- Comparative time-series charts.

The module should make it possible to identify geographical differences that would be hidden by global aggregation.

## 7.11 Visualization Module

**Responsibility:** Present environmental data and analytical results.

Initial visualization components:

- Variable Explorer.
- Geographic Region Selector.
- Time-Series Viewer.
- Trend Chart.
- Regional Comparison Map.
- Statistical Results Panel.
- Data Metadata Panel.

Visualizations should distinguish between:

- Raw observations.
- Aggregated values.
- Estimated trends.
- Statistically significant trends.
- Uncertain or insufficiently supported results.

## 7.12 Scientific Interpretation Module

**Responsibility:** Help users understand the results of their analysis.

Capabilities:

- Variable descriptions.
- Trend summaries.
- Statistical result explanations.
- Regional comparison summaries.
- Scientific terminology explanations.
- Contextual information.

Potential future extension:

- AI-assisted scientific explanations.
- Related variable discovery.
- Research-paper and news context.
- Hypothesis exploration.

AI-generated interpretations must remain separate from measured data and statistical results. The system should not claim that a particular environmental process caused a trend unless the evidence supports that conclusion.

# 8. Shared Data Contracts

The modules should communicate through stable data contracts.

Initial conceptual models:

```text
EarthVariable
VariableMetadata
DataSource
DataRequest
Dataset
DatasetMetadata
DataProvenance

GeographicRegion
SpatialCoordinate
SpatialGrid
SpatialBoundary

TemporalRange
TimeSeries
TimeSeriesPoint
AggregationMetadata

TrendResult
TrendSlope
TrendDirection
StatisticalTestResult
ConfidenceInterval
SignificanceResult

RegionalTrend
RegionalComparison
VisualizationState
AnalysisReport
```

Every model should have a clearly defined owner.

For example:

- Variable Discovery owns the variable catalog.
- Region Manager owns geographic region representations.
- Data Source Manager owns provider adapters.
- Data Acquisition owns retrieval operations.
- Time-Series Engine owns time-series generation.
- Trend Analysis owns trend calculations.
- Statistical Testing owns significance-test results.
- Visualization owns presentation state.

Other modules should access these models through explicit interfaces.

# 9. Runtime Execution Flow

## 9.1 Application Initialization

```text
Application Launcher
        |
        v
Application Core
        |
        v
Load Configuration
        |
        v
Initialize Event System
        |
        v
Register Modules
        |
        v
Resolve Dependencies
        |
        v
Initialize Modules
        |
        v
Start Runtime
        |
        v
Ready for User Interaction
```

## 9.2 Scientific Analysis Workflow

```text
User Opens Variable Explorer
        |
        v
Select Earth Science Variable
        |
        v
Select Geographical Region
        |
        v
Select Time Range
        |
        v
Data Acquisition
        |
        v
Data Validation
        |
        v
Data Normalization
        |
        v
Time-Series Generation
        |
        v
Trend Calculation
        |
        v
Statistical Significance Testing
        |
        v
Regional Comparison
        |
        v
Visualization and Results
        |
        v
Scientific Interpretation
```

# 10. Scientific Requirements

## 10.1 Temporal Coverage

Trend analysis requires a sufficiently long time series.

The platform should display the available temporal coverage and warn users when the selected period may be insufficient for reliable analysis.

## 10.2 Temporal Resolution

The initial implementation should prioritize daily and monthly data, as suggested by the challenge.

Other resolutions can be introduced through the same time-series interfaces.

## 10.3 Seasonal Variability

Some trends may be difficult to identify because regular seasonal cycles influence the observations.

The architecture should allow seasonal analysis and future seasonal adjustment without making complex seasonal modeling a mandatory initial requirement.

## 10.4 Regional Differences

Regional trends should be calculated independently where appropriate.

A global average must not replace regional analysis because opposite regional trends can cancel each other out.

## 10.5 Statistical Significance

The platform must distinguish between:

- An observed increase or decrease.
- The estimated rate of change.
- A statistically significant trend.
- A trend whose significance cannot be established reliably.

The statistical method and its assumptions must be documented with every result.

## 10.6 Reproducibility

Every analysis should retain enough information to reproduce its result:

- Variable identifier.
- Data source.
- Region.
- Time range.
- Temporal resolution.
- Aggregation method.
- Data quality information.
- Statistical method.
- Analysis parameters.

# 11. Proposed Repository Structure

```text
EarthTwinEngine/
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
│
├── docs/
│   ├── architecture/
│   ├── module-contracts/
│   ├── scientific-methods/
│   ├── data-sources/
│   └── development/
│
├── application/
│   ├── Core/
│   ├── Runtime/
│   ├── ModuleManager/
│   ├── DependencyResolver/
│   ├── EventSystem/
│   ├── ResourceManager/
│   └── Configuration/
│
├── domain/
│   ├── Variables/
│   ├── Geography/
│   ├── Temporal/
│   ├── Datasets/
│   └── Analysis/
│
├── modules/
│   │
│   ├── Discovery/
│   ├── Region/
│   ├── DataAcquisition/
│   ├── DataValidation/
│   ├── DataNormalization/
│   ├── TimeSeries/
│   │
│   ├── TrendAnalysis/
│   ├── StatisticalTesting/
│   ├── RegionalComparison/
│   │
│   ├── Visualization/
│   └── ScientificInterpretation/
│
├── data/
│   ├── DataSourceManager/
│   ├── Adapters/
│   │   ├── MODIS/
│   │   ├── OMI/
│   │   ├── AIRS/
│   │   ├── GPM/
│   │   ├── MERRA2/
│   │   └── GLDAS/
│   │
│   ├── Normalization/
│   ├── Validation/
│   ├── Provenance/
│   └── Cache/
│
├── visualization/
│   ├── Map/
│   ├── Charts/
│   ├── TimeSeries/
│   ├── TrendReports/
│   └── Interaction/
│
├── api/
│   ├── DataAPI/
│   ├── AnalysisAPI/
│   └── VisualizationAPI/
│
├── infrastructure/
│   ├── Logging/
│   ├── Storage/
│   ├── Networking/
│   └── Monitoring/
│
├── tests/
│   ├── Unit/
│   ├── Integration/
│   ├── Module/
│   ├── ScientificValidation/
│   └── DataValidation/
│
├── resources/
│   ├── datasets/
│   ├── reference-regions/
│   └── demonstration-cases/
│
├── scripts/
│
└── config/
    ├── application/
    ├── modules/
    └── data-sources/
```

This is a logical starting structure. Physical project boundaries can be adjusted after selecting the technology stack.

# 12. Development Phases

## Phase 0 — Runtime Foundation

- Establish Application Core.
- Define module lifecycle contracts.
- Implement Module Manager.
- Implement dependency resolution.
- Implement Event System.
- Establish shared data contracts.
- Implement configuration and logging.

**Expected result:** An executable application runtime capable of loading and coordinating independent modules.

## Phase 1 — Variable and Data Source Foundation

- Establish the variable catalog.
- Define variable metadata.
- Implement data source adapter interfaces.
- Select initial NASA datasets.
- Implement an initial data retrieval workflow.
- Establish source provenance.

**Expected result:** Users can discover available variables and retrieve an initial dataset.

## Phase 2 — Regional Data Processing

- Implement geographical region selection.
- Implement regional data acquisition.
- Implement validation.
- Implement normalization.
- Establish common spatial and temporal representations.

**Expected result:** Users can retrieve validated data for a selected variable, region, and time range.

## Phase 3 — Time-Series Generation

- Implement temporal aggregation.
- Implement spatial aggregation.
- Generate daily and monthly time series.
- Handle missing observations.
- Preserve aggregation metadata.
- Build the initial time-series viewer.

**Expected result:** Users can explore environmental variables over time for selected regions.

## Phase 4 — Trend Analysis

- Implement linear regression.
- Calculate trend slopes.
- Calculate rates of change.
- Implement Mann-Kendall testing.
- Implement appropriate confidence intervals.
- Add statistical result reporting.

**Expected result:** Users can identify increasing and decreasing trends and assess their statistical significance.

## Phase 5 — Regional Comparison and Visualization

- Implement multiple-region analysis.
- Compare regional trend directions.
- Display trend magnitudes.
- Visualize statistical significance.
- Build regional comparison maps.
- Integrate the results into a unified interface.

**Expected result:** Users can investigate how the same environmental variable changes differently across geographical regions.

## Phase 6 — Scientific Interpretation and Demonstration

- Add variable explanations.
- Add analysis summaries.
- Add demonstration scenarios.
- Validate statistical calculations.
- Document data sources.
- Test reproducibility.
- Prepare the final demonstration.

**Expected result:** A complete Earth Systems Trend Detective workflow.

# 13. Demonstration Scenarios

The final demonstration should focus on the challenge's central scientific concept.

## Scenario A — Regional Temperature Trends

1. Select temperature.
2. Choose two geographical regions.
3. Retrieve the available data.
4. Generate time series.
5. Calculate linear trends.
6. Test statistical significance.
7. Compare regional results.
8. Visualize increasing and decreasing trends.

## Scenario B — Precipitation Trends

1. Select precipitation.
2. Choose a region.
3. Select a sufficiently long time range.
4. Generate monthly time series.
5. Calculate the trend.
6. Perform significance testing.
7. Visualize the result.

## Scenario C — Environmental Variable Exploration

1. Open the variable catalog.
2. Explore available Earth science variables.
3. Inspect their scientific descriptions and data availability.
4. Select a variable.
5. Select a region.
6. Start the analysis workflow.

These scenarios should use actual available datasets and should not assume that a particular region necessarily has a statistically significant trend.

# 14. Engineering Principles

Earth Twin Engine should follow these principles throughout development.

1. **Modular ownership:** Each subsystem owns its internal implementation and state.
2. **Explicit interfaces:** Modules communicate through stable contracts.
3. **Actor-oriented communication:** Cross-module operations use commands, events, and responses.
4. **Separation of concerns:** Data retrieval, processing, analysis, and visualization remain independent.
5. **Scientific reproducibility:** Results must be traceable to their data and analysis parameters.
6. **Regional-first analysis:** Regional trends must not be hidden by global aggregation.
7. **Statistical transparency:** Every significance result must identify its method and assumptions.
8. **Data provenance:** Every dataset must retain its source information.
9. **Replaceable implementations:** Data providers and analytical methods should be independently replaceable.
10. **Extensible runtime:** Additional variables, data sources, and statistical methods should be integrated through defined interfaces.

# 15. Scope and Boundaries

The initial implementation focuses on the requirements of the NASA Earth Systems Trend Detective challenge.

The system should prioritize:

- Variable discovery.
- Regional data acquisition.
- Time-series generation.
- Linear trend detection.
- Rate-of-change calculation.
- Statistical significance testing.
- Regional comparisons.
- Scientific visualization.

The project does not initially require a complete physical Earth simulation, atmospheric fluid dynamics engine, or predictive climate model.

More advanced capabilities such as nonlinear trend detection, seasonal decomposition, multivariable correlation, causal inference, and environmental forecasting may be considered as future extensions.

The initial goal is to provide a scientifically transparent and reproducible tool that fulfills the complete challenge workflow.

## Run the current prototype API

The current frontend can send its clearly labeled simulated values to the existing Python
`TrendAnalyzer` through a local FastAPI service. This connects the interface to the statistical
model; it does not fetch NASA data and is not a trained machine-learning model.

From the repository root, install the optional API and development dependencies, then start the
backend:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[api,dev]"
.\.venv\Scripts\python.exe -m uvicorn earth_twin_engine.api:app --app-dir src --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm ci
npm run dev
```

The frontend uses `VITE_API_BASE_URL` (default `http://localhost:8000`). Check API availability at
`/api/v1/health`; API docs are available at `/docs`. See [frontend/README.md](frontend/README.md)
for test commands and deployment configuration.

# 16. Final Project Objective

Earth Twin Engine aims to make Earth science trend analysis accessible through a unified, modular, and scientifically reproducible platform.

It connects Earth science data discovery, geographical selection, temporal analysis, statistical testing, and visualization into one coordinated environment.

Users should be able to investigate what is changing, where it is changing, how much it is changing, and whether the observed change is statistically significant.

**The central objective is to turn large-scale Earth science datasets into understandable, region-aware, and statistically supported environmental insights.**
