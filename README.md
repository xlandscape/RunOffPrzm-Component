## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Inputs](#inputs)
  * [Outputs](#outputs)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
RunOffPrzm is a Landscape Model component for simulating run-off processes with the
[Pesticide Root Zone Model (PRZM)](https://esdac.jrc.ec.europa.eu/projects/przmsw). The component encapsulates a
module that extends standard PRZM runs for each application within the simulated landscape by a spatial explicit
surface flow model. `RunOffPrzm` outputs run-off deposition at a square-meter resolution, but the flow model may
have an arbitrarily coarser resolution. `RunOffPrzm` simulates filtering between square-meter cells either using
the FOCUS curve number technique or a
[vegetative filter strip model](https://abe.ufl.edu/faculty/carpena/vfsmod/index.shtml) (VfsMOD).  
This is an automatically generated documentation based on the available code and in-line documentation. The current
version of this document is from 2021-09-08.  

### Built with
* Landscape Model core version 1.6.2
* PRZM_Runoff version 1.45 (see `Release 1.4\Changelog.txt` for details)


## Getting Started
The component can be used in any Landscape Model based on core version 1.6.2 or newer. See the Landscape Model
core's `README` for general tips on how to add a component to a Landscape Model.

### Prerequisites
A model developer that wants to add the `RunOffPrzm` component to a Landscape Model needs to set up the general 
structure for a Landscape Model first. See the Landscape Model core's `README` for details on how to do so.

### Installation
1. Copy the `RunOffPrzm` component into the `model\variant` sub-folder.
2. Make use of the component by including it into the model composition using `module=RunOffPrzm` and 
   `class=RunOffPrzm`. 


## Usage
The following gives a sample configuration of the `RunOffPrzm` component. See [inputs](#inputs) and 
[outputs](#outputs) for further details on the component's interface.
```xml
<RunOffPrzm module="RunOffPrzm" class="RunOffPrzm" enabled="$(SimulateRunOffExposure)">
<ProcessingPath>$(_MCS_BASE_DIR_)\$(_MC_NAME_)\processing\runoff</ProcessingPath>
<Model_AdsorptionMethod>aged</Model_AdsorptionMethod>
  <Model_SoilTemperatureSimulation
type="bool">true</Model_SoilTemperatureSimulation>
  <SubstanceName>$(Substance)</SubstanceName>
<Substance_PlantUptakeFactor type="float" unit="1/d">0</Substance_PlantUptakeFactor>
<Substance_PesticideDissipationRateOfFoliage type="float" unit="1/d">
    10
</Substance_PesticideDissipationRateOfFoliage>
  <Substance_FoliarWashOffCoefficient type="float"
unit="1/cm">0.5</Substance_FoliarWashOffCoefficient>
  <Substance_HenryConstant type="float"
unit="1">0.03</Substance_HenryConstant>
  <Substance_VapourPressure type="float"
unit="mPa">0.0001</Substance_VapourPressure>
  <Substance_MolecularWeight type="float"
unit="g/mol">304</Substance_MolecularWeight>
  <Substance_WaterSolubility type="float"
unit="mg/L">60</Substance_WaterSolubility>
  <Substance_TemperatureAtWhichMeasured type="float"
unit="K">293</Substance_TemperatureAtWhichMeasured>
  <Substance_FreundlichExponent type="float"
unit="1">$(FreundlichExponent)</Substance_FreundlichExponent>
  <Substance_ReferenceMoistureForDT50Soil type="float"
unit="%">100</Substance_ReferenceMoistureForDT50Soil>
  <Substance_SoilDT50 type="float"
unit="d">$(DT50)</Substance_SoilDT50>
  <Substance_KocSoil type="float" unit="cm&#179;/g">$(KocSoil)</Substance_KocSoil>
<SprayApplication_PrzmApplicationMethod>foliar</SprayApplication_PrzmApplicationMethod>
<SprayApplication_IncorporationDepth type="float" unit="cm">5</SprayApplication_IncorporationDepth>
  <Options_StartDate
type="date">2006-01-01</Options_StartDate>
  <Options_EndDate type="date">2015-12-31</Options_EndDate>
<Options_TemporaryOutputPath>$(RunOffTempDir)\$(_MC_NAME_)</Options_TemporaryOutputPath>
  <Options_DeleteTemporaryGrids
type="bool">true</Options_DeleteTemporaryGrids>
  <Options_TimeoutSecPrzm type="int"
unit="s">100</Options_TimeoutSecPrzm>
  <Options_ReportingThreshold type="float"
unit="mg">$(ReportingThreshold)</Options_ReportingThreshold>
  <Options_DeleteAllInterimResults
type="bool">true</Options_DeleteAllInterimResults>
  <Options_ShowExtendedErrorInformation
type="bool">true</Options_ShowExtendedErrorInformation>
  <Weather_Precipitation>
    <FromOutput component="Weather"
output="PRECIPITATION" />
    <Extension module="extend" class="CoordinateTransform">
<Transformation_type>date</Transformation_type>
      <Offset>1975-01-01</Offset>
    </Extension>
</Weather_Precipitation>
  <Weather_ET0>
    <FromOutput component="Weather" output="ET0" />
    <Extension
module="extend" class="CoordinateTransform">
      <Transformation_type>date</Transformation_type>
<Offset>1975-01-01</Offset>
    </Extension>
  </Weather_ET0>
  <Weather_Temperature>
    <FromOutput
component="Weather" output="TEMPERATURE_AVG" />
    <Extension module="extend" class="CoordinateTransform">
<Transformation_type>date</Transformation_type>
      <Offset>1975-01-01</Offset>
    </Extension>
</Weather_Temperature>
  <Weather_WindSpeed>
    <FromOutput component="Weather" output="WINDSPEED" />
    <Extension
module="extend" class="CoordinateTransform">
      <Transformation_type>date</Transformation_type>
<Offset>1975-01-01</Offset>
    </Extension>
  </Weather_WindSpeed>
  <Weather_SolarRadiation>
    <FromOutput
component="Weather" output="RADIATION" />
    <Extension module="extend" class="CoordinateTransform">
<Transformation_type>date</Transformation_type>
      <Offset>1975-01-01</Offset>
    </Extension>
</Weather_SolarRadiation>
  <Fields_Slope type="float" unit="%">3</Fields_Slope>
  <Fields_SoilHorizonThicknesses
type="list[float]" scales="other/soil_horizon" unit="cm">
    30 30 40
  </Fields_SoilHorizonThicknesses>
<Fields_SoilHorizonBulkDensities type="list[float]" scales="other/soil_horizon" unit="g/cm&#179;">
    1.35 1.45 1.48
</Fields_SoilHorizonBulkDensities>
  <Fields_SoilHorizonOrganicMaterialContents type="list[float]"
scales="other/soil_horizon" unit="%">
    1.2 0.3 0.1
  </Fields_SoilHorizonOrganicMaterialContents>
<Fields_SoilHorizonSandFractions type="list[float]" scales="other/soil_horizon" unit="%">
    5 6 5
</Fields_SoilHorizonSandFractions>
  <Fields_SoilHorizonSiltFractions type="list[float]" scales="other/soil_horizon"
unit="%">
    82 83 84
  </Fields_SoilHorizonSiltFractions>
  <Fields_Geometries>
    <FromOutput
component="LandscapeScenario" output="Geometries" />
  </Fields_Geometries>
  <Fields_Ids>
    <FromOutput
component="LandscapeScenario" output="FeatureIds" />
  </Fields_Ids>
  <Fields_Crs>
    <FromOutput
component="LandscapeScenario" output="Crs" />
  </Fields_Crs>
  <Fields_Extent>
    <FromOutput
component="LandscapeScenario" output="Extent" />
  </Fields_Extent>
  <Fields_FlowGrid>
    <FromOutput
component="LandscapeScenario" output="flow_grid" />
  </Fields_FlowGrid>
  <Fields_InFieldMargin type="float"
unit="m">$(InFieldMargin)</Fields_InFieldMargin>
  <Ppm_AppliedFields>
    <FromOutput component="PPM"
output="AppliedFields" />
  </Ppm_AppliedFields>
  <Ppm_ApplicationDates>
    <FromOutput component="PPM"
output="ApplicationDates" />
  </Ppm_ApplicationDates>
  <Ppm_ApplicationRates>
    <FromOutput component="PPM"
output="ApplicationRates" />
  </Ppm_ApplicationRates>
  <Ppm_AppliedAreas>
    <FromOutput component="PPM"
output="AppliedAreas" />
  </Ppm_AppliedAreas>
<Options_MethodOfRunoffGeneration>PRZM</Options_MethodOfRunoffGeneration>
  <Options_UsePreSimulatedPrzmResults
type="bool">true</Options_UsePreSimulatedPrzmResults>
  <Options_UseOnePrzmModelPerGridCell
type="bool">false</Options_UseOnePrzmModelPerGridCell>
  <Options_UseVfsMod type="bool">false</Options_UseVfsMod>
<CropParameters_VfsModLookupTables type="list[str]" scales="other/crop">
    none|$(:VfsMod_lookup_table)
</CropParameters_VfsModLookupTables>
  <CropParameters_PanEvaporationFactors type="list[float]" scales="other/crop"
unit="1">
    0.84 0.84
  </CropParameters_PanEvaporationFactors>
  <CropParameters_CanopyInterceptions
type="list[float]" scales="other/crop" unit="cm">
    0.15 0.15
  </CropParameters_CanopyInterceptions>
<CropParameters_MaximumCoverages type="list[int]" scales="other/crop" unit="%">
    90 90
</CropParameters_MaximumCoverages>
  <CropParameters_MaximumHeights type="list[int]" scales="other/crop" unit="cm">
110 110
  </CropParameters_MaximumHeights>
  <CropParameters_MaximumRootingDepths type="list[int]" scales="other/crop"
unit="cm">
    130 130
  </CropParameters_MaximumRootingDepths>
  <CropParameters_Fallows type="list[float]"
scales="other/crop" unit="1">
    0.9 0.9
  </CropParameters_Fallows>
  <CropParameters_Cropping type="list[float]"
scales="other/crop" unit="1">
    0.2 0.2
  </CropParameters_Cropping>
  <CropParameters_Residues type="list[float]"
scales="other/crop" unit="1">
    0.4 0.4
  </CropParameters_Residues>
  <CropParameters_EmergenceDates type="list[str]"
scales="other/crop">
    12-11|12-11
  </CropParameters_EmergenceDates>
  <CropParameters_MaturationDates
type="list[str]" scales="other/crop">
    10-06|10-06
  </CropParameters_MaturationDates>
  <CropParameters_HarvestDates
type="list[str]" scales="other/crop">
    31-07|31-07
  </CropParameters_HarvestDates>
  <CropParameters_FallowDates
type="list[str]" scales="other/crop">
    01-11|01-11
  </CropParameters_FallowDates>
  <CropParameters_WaterMitigations
type="list[float]" scales="other/crop" unit="1">
    0 -0.086
  </CropParameters_WaterMitigations>
<CropParameters_SedimentMitigations type="list[float]" scales="other/crop" unit="1">
    0 -0.153
</CropParameters_SedimentMitigations>
  <CropParameters_Crops type="list[str]"
scales="other/crop">Cereals,Winter|OffCrop</CropParameters_Crops>
</RunOffPrzm>
```

### Inputs
#### ProcessingPath
The working directory for the module. It is used for all files prepared as module inputs
or generated as module outputs. This excludes the files of the actual PRZM run whose path. See the 
[Options_TemporaryOutputPath](#Options_TemporaryOutputPath) input for the according parameterization. 
the `ProcessingPath` are considered temporary and can be safely deleted after a successful simulation 
run. Make sure that the `ProcessingPath` is configured in such a way that it does not collide with
other simulation runs (of different experiments or Monte Carlo runs).  
`ProcessingPath` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `ProcessingPath` input may not have a physical unit.

#### Model_AdsorptionMethod
Specifies how PRZM simulates adsorption. Three methods are available: `linear` 
calculates adsorption based on a linear regression, `Freundlich` based on a normalized Freundlich 
equation and `aged` uses an aged adsorption function.  
`Model_AdsorptionMethod` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `Model_AdsorptionMethod` input may not have a physical unit.
Allowed values are: `linear`, `Freundlich`, `aged`.

#### Model_SoilTemperatureSimulation
Specifies whether to simulate soil temperature or not. Enabled soil temperature 
simulation does not consider nitrogen transport.  
`Model_SoilTemperatureSimulation` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Model_SoilTemperatureSimulation` input may not have a physical unit.

#### SubstanceName
Substances differ in their properties and, thus, for every substance simulated a 
different set of values has to be specified. The current `RunOffPrzm` component does, however, allow to 
simulate a single substance only. This might change in the future, as the module is conceptually and 
technically prepared to handle multiple substances simultaneously. The `SubstanceName` has currently
no technical relevance.  
`SubstanceName` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `SubstanceName` input may not have a physical unit.

#### Substance_PlantUptakeFactor
The substance-specific PRZM plant uptake factor.  
`Substance_PlantUptakeFactor` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_PlantUptakeFactor` input values is `1/d`.

#### Substance_PesticideDissipationRateOfFoliage
The substance-specific PRZM pesticide dissipation rate on foliage.  
`Substance_PesticideDissipationRateOfFoliage` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_PesticideDissipationRateOfFoliage` input values is `1/d`.

#### Substance_FoliarWashOffCoefficient
The substance-specific PRZM foliar wash-off coefficient.  
`Substance_FoliarWashOffCoefficient` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_FoliarWashOffCoefficient` input values is `1/cm`.

#### Substance_HenryConstant
The substance-specific Henry constant. You can also set this input to the special value
of `nan` to let the module derive the Henry constant from the input values of
[Substance_VapourPressure](#Substance_VapourPressure),
[Substance_MolecularWeight](#Substance_MolecularWeight), 
[Substance_WaterSolubility](#Substance_WaterSolubility) and 
[Substance_TemperatureAtWhichMeasured](#Substance_TemperatureAtWhichMeasured).  
`Substance_HenryConstant` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_HenryConstant` input values is `1`.

#### Substance_VapourPressure
The substance-specific vapor pressure.  
`Substance_VapourPressure` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_VapourPressure` input values is `mPa`.

#### Substance_MolecularWeight
The substance-specific molecular weight.  
`Substance_MolecularWeight` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_MolecularWeight` input values is `g/mol`.

#### Substance_WaterSolubility
The substance-specific water solubility.  
`Substance_WaterSolubility` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_WaterSolubility` input values is `mg/L`.

#### Substance_TemperatureAtWhichMeasured
The reference temperature for the physical and chemical properties of the substance.  
`Substance_TemperatureAtWhichMeasured` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_TemperatureAtWhichMeasured` input values is `K`.

#### Substance_FreundlichExponent
The substance-specific Freundlich exponent.  
`Substance_FreundlichExponent` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_FreundlichExponent` input values is `1`.

#### Substance_ReferenceMoistureForDT50Soil
The substance-specific reference moisture for the soil DT50 in percent of field capacity.  
`Substance_ReferenceMoistureForDT50Soil` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_ReferenceMoistureForDT50Soil` input values is `%`.

#### Substance_SoilDT50
The substance-specific soil half-life time.  
`Substance_SoilDT50` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_SoilDT50` input values is `d`.

#### Substance_KocSoil
The substance-specific KOC in soil.  
`Substance_KocSoil` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Substance_KocSoil` input values is `cm³/g`.

#### SprayApplication_PrzmApplicationMethod
The PRZM chemical application method that is assumed for all spray applications. `soil`
indicates direct spraying of the soil surface, `canopy` of the crop canopy and `foliar` a foliar
application.  
`SprayApplication_PrzmApplicationMethod` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `SprayApplication_PrzmApplicationMethod` input may not have a physical unit.
Allowed values are: `soil`, `canopy`, `foliar`.

#### SprayApplication_IncorporationDepth
The PRZM incorporation depth of spray applications.  
`SprayApplication_IncorporationDepth` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `SprayApplication_IncorporationDepth` input values is `cm`.

#### Options_StartDate
The first simulated date. All temporal input parameters must start at this date.  
`Options_StartDate` expects its values to be of type `date`.
Values have to refer to the `global` scale.
Values of the `Options_StartDate` input may not have a physical unit.

#### Options_EndDate
The last simulated date. All temporal input parameters must end at this date.  
`Options_EndDate` expects its values to be of type `date`.
Values have to refer to the `global` scale.
Values of the `Options_EndDate` input may not have a physical unit.

#### Options_TemporaryOutputPath
PRZM cannot run in paths with long names. The [ProcessingPath](#ProcessingPath), due to 
its requirement to be unique for each simulation run, is normally too long to be used here. Instead, 
PRZM simulations run in the directory specified by the `Options_TemporaryOutputPath` input.  
`Options_TemporaryOutputPath` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `Options_TemporaryOutputPath` input may not have a physical unit.

#### Options_DeleteTemporaryGrids
`RunOffPrzm` creates an output grid for each field in the landscape before it merges 
them. If the temporary output of each field should be deleted as early as possible, set this option to `
true`. `False` is the right option if you need to keep the temporary grids, e.g., for debugging.  
`Options_DeleteTemporaryGrids` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_DeleteTemporaryGrids` input may not have a physical unit.

#### Options_TimeoutSecPrzm
The time after which an idle PRZM instance timeouts. Tweak this option to prevent locks
in some rare circumstances.  
`Options_TimeoutSecPrzm` expects its values to be of type `int`.
Values have to refer to the `global` scale.
The physical unit of the `Options_TimeoutSecPrzm` input values is `s`.

#### Options_ReportingThreshold
The minimum mass that is required to trigger continuation of the water and substance 
flow simulation. Smaller masses remain at the current cell and are not further transported. Set this
option to a sensible value that allows to capture all relevant depositions while reducing the processing
time.  
`Options_ReportingThreshold` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Options_ReportingThreshold` input values is `mg`.

#### Options_DeleteAllInterimResults
Specifies whether to delete all intermediary files after a successful simulation run.
Enable this option to save disk space (intermediary files may accumulate to a considerable amount) or
disable it if you need to keep intermediary files, e.g., for debugging.  
`Options_DeleteAllInterimResults` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_DeleteAllInterimResults` input may not have a physical unit.

#### Weather_Precipitation
A series of daily precipitation values. The series must cover the entire range between
[Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order.  
`Weather_Precipitation` expects its values to be of type `ndarray`.
Values have to refer to the `time/day` scale.
The physical unit of the `Weather_Precipitation` input values is `mm/d`.

#### Weather_ET0
A series of daily evapotranspiration values. The series must cover the entire range 
between [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive
order.  
`Weather_ET0` expects its values to be of type `ndarray`.
Values have to refer to the `time/day` scale.
The physical unit of the `Weather_ET0` input values is `mm/d`.

#### Weather_Temperature
A series of daily temperature values. The series must cover the entire range between
[Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order.  
`Weather_Temperature` expects its values to be of type `ndarray`.
Values have to refer to the `time/day` scale.
The physical unit of the `Weather_Temperature` input values is `°C`.

#### Weather_WindSpeed
A series of daily wind speed values. The series must cover the entire range between
[Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order.  
`Weather_WindSpeed` expects its values to be of type `ndarray`.
Values have to refer to the `time/day` scale.
The physical unit of the `Weather_WindSpeed` input values is `m/s`.

#### Weather_SolarRadiation
A series of daily solar radiation values. The series must cover the entire range between
[Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order.  
`Weather_SolarRadiation` expects its values to be of type `ndarray`.
Values have to refer to the `time/day` scale.
The physical unit of the `Weather_SolarRadiation` input values is `kJ/(m²*d)`.

#### Fields_Slope
The average slope of all fields in the landscape. This slope is feeds PRZM run-off
calculations and is independent of the slopes underlying the [Fields_FlowGrid](#Fields_FlowGrid). 
Please make sure that representation of slopes is somewhat consistent between landscape scenario and 
`RunOffPrzm` parameterization. A later version may allow specifying slopes on a per-field basis instead
of globally.  
`Fields_Slope` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Fields_Slope` input values is `%`.

#### Fields_SoilHorizonThicknesses
A sequence of soil horizon depths from top to bottom. This sequence defines how many
soil horizons there are and how they are distributed along the z-axis.  
`Fields_SoilHorizonThicknesses` expects its values to be of type `list[float]`.
Values have to refer to the `other/soil_horizon` scale.
The physical unit of the `Fields_SoilHorizonThicknesses` input values is `cm`.

#### Fields_SoilHorizonBulkDensities
A sequence of soil horizon bulk densities from top to bottom. This sequence must have the
same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
Elements refer to the same soil horizon (in the same order) as the soil horizons specified there.  
`Fields_SoilHorizonBulkDensities` expects its values to be of type `list[float]`.
Values have to refer to the `other/soil_horizon` scale.
The physical unit of the `Fields_SoilHorizonBulkDensities` input values is `g/cm³`.

#### Fields_SoilHorizonOrganicMaterialContents
A sequence of soil horizon organic material contents from top to bottom. This sequence 
must have the same number of elements as the 
[Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence. Elements refer to the same 
soil horizon (in the same order) as the soil horizons specified there.  
`Fields_SoilHorizonOrganicMaterialContents` expects its values to be of type `list[float]`.
Values have to refer to the `other/soil_horizon` scale.
The physical unit of the `Fields_SoilHorizonOrganicMaterialContents` input values is `%`.

#### Fields_SoilHorizonSandFractions
A sequence of soil horizon sand fractions from top to bottom. This sequence must have the
same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
Elements refer to the same soil horizon (in the same order) as the soil horizons specified there.  
`Fields_SoilHorizonSandFractions` expects its values to be of type `list[float]`.
Values have to refer to the `other/soil_horizon` scale.
The physical unit of the `Fields_SoilHorizonSandFractions` input values is `%`.

#### Fields_SoilHorizonSiltFractions
A sequence of soil horizon silk fractions from top to bottom. This sequence must have the
same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
Elements refer to the same soil horizon (in the same order) as the soil horizons specified there.  
`Fields_SoilHorizonSiltFractions` expects its values to be of type `list[float]`.
Values have to refer to the `other/soil_horizon` scale.
The physical unit of the `Fields_SoilHorizonSiltFractions` input values is `%`.

#### Fields_Geometries
The geometries of in-field areas in WKB representation. Each element refers to a field
with its according identifier from the list of [Fields_Ids](#Fields_Ids).  
`Fields_Geometries` expects its values to be of type `list[bytes]`.
Values have to refer to the `space/base_geometry` scale.
Values of the `Fields_Geometries` input may not have a physical unit.

#### Fields_Ids
The simulation-wide unique identifiers of fields within the landscape. These identifiers
stem from the landscape scenario and are shared among components.  
`Fields_Ids` expects its values to be of type `list[int]`.
Values have to refer to the `space/base_geometry` scale.
Values of the `Fields_Ids` input may not have a physical unit.

#### Fields_Crs
The coordinate reference system in which the [Fields_Geometries](#Fields_Geometries) 
are projected. The coordinate reference system needs to be in Proj4 notation.  
`Fields_Crs` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `Fields_Crs` input may not have a physical unit.

#### Fields_Extent
The extent of the simulated landscape. This value has to be consistent with the 
[Fields_Geometries](#Fields_Geometries) and the [Fields_FlowGrid](#Fields_FlowGrid) and is projected
in the [Fields_Crs](#Fields_Crs). The landscape scenario normally takes care of that.  
`Fields_Extent` expects its values to be of type `tuple[float]`.
Values have to refer to the `space/extent` scale.
The physical unit of the `Fields_Extent` input values is `metre`.

#### Fields_FlowGrid
The file path to a raster file that contains information about the flow direction 
between individual raster cells. Flow directions follow the [ESRI standard](
https://desktop.arcgis.com/de/arcmap/10.3/tools/spatial-analyst-toolbox/flow-direction.htm) encoding 
for flow directions.  
`Fields_FlowGrid` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `Fields_FlowGrid` input may not have a physical unit.

#### Fields_InFieldMargin
A width of an inner margin along field boundaries that is not covered with crop but with
other herbaceous vegetation. This value applies to all fields in the landscape and does not change over
time, but a future version of the component may allow for spatio-temporal variation.  
`Fields_InFieldMargin` expects its values to be of type `float`.
Values have to refer to the `global` scale.
The physical unit of the `Fields_InFieldMargin` input values is `m`.

#### Ppm_AppliedFields
The identifiers of applied fields (according to the [Fields_Ids](#Fields_Ids)) per 
application. The number of elements defines how many applications there are in total, and the values
link applications to individual fields.  
`Ppm_AppliedFields` expects its values to be of type `ndarray`.
Values have to refer to the `other/application` scale.
Values of the `Ppm_AppliedFields` input may not have a physical unit.

#### Ppm_ApplicationDates
The dates of application. This specifies for each application indicated by the 
[Ppm_AppliedFields](#Ppm_AppliedFields), on which day the application took place.  
`Ppm_ApplicationDates` expects its values to be of type `ndarray`.
Values have to refer to the `other/application` scale.
Values of the `Ppm_ApplicationDates` input may not have a physical unit.

#### Ppm_ApplicationRates
This indicates for each application indicated by the 
[Ppm_AppliedFields](#Ppm_AppliedFields) at which rate the substance with the name of 
[SubstanceName](#SubstanceName) was applied.  
`Ppm_ApplicationRates` expects its values to be of type `ndarray`.
Values have to refer to the `other/application` scale.
The physical unit of the `Ppm_ApplicationRates` input values is `g/ha`.

#### Ppm_AppliedAreas
For each application indicated by the [Ppm_AppliedFields](#Ppm_AppliedFields), this gives
the geometry of the actual applied area in WKB representation. This geometry might be equal to or 
smaller and located within the field geometry given by the [Fields_Geometries](#Fields_Geometries). Only
the area indicated by the `Ppm_AppliedAreas` is actually applied, allowing to leave in-crop buffers or
depict spatial variation of the application relative to the field geometry.  
`Ppm_AppliedAreas` expects its values to be of type `list[bytes]`.
Values have to refer to the `other/application` scale.
Values of the `Ppm_AppliedAreas` input may not have a physical unit.

#### Options_ShowExtendedErrorInformation
Specifies whether the module prompts extended information on errors or not.  
`Options_ShowExtendedErrorInformation` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_ShowExtendedErrorInformation` input may not have a physical unit.

#### Options_MethodOfRunoffGeneration
Specifies the method used to simulate the amount of run-off. `PRZM` specifies to use PRZM
runs for run-off generation, `FOCUS` to use FOCUS Step2 run-off simulations.  
`Options_MethodOfRunoffGeneration` expects its values to be of type `str`.
Values have to refer to the `global` scale.
Values of the `Options_MethodOfRunoffGeneration` input may not have a physical unit.
Allowed values are: `PRZM`, `FOCUS`.

#### Options_UsePreSimulatedPrzmResults
Specifies using pre-simulated PRZM runs for run-off simulation instead of new PRZM 
runs.  
`Options_UsePreSimulatedPrzmResults` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_UsePreSimulatedPrzmResults` input may not have a physical unit.

#### Options_UseOnePrzmModelPerGridCell
Specifies to start an individual PRZM run for every cell to calculate run-off. Enabling 
this parameter results in many PRZM runs, resulting in considerably longer simulation runs. Usage of 
PRZM for the purpose of run-off generation in off-crop cells should also be seen as experimental.  
`Options_UseOnePrzmModelPerGridCell` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_UseOnePrzmModelPerGridCell` input may not have a physical unit.

#### Options_UseVfsMod
Specifies whether to use crop-specific VfsMOD lookup tables to simulate run-off 
filtering. The [CropParameters_VfsModLookupTables](#CropParameters_VfsModLookupTables) input 
parameterizes which lookup table to use for which crop.  
`Options_UseVfsMod` expects its values to be of type `bool`.
Values have to refer to the `global` scale.
Values of the `Options_UseVfsMod` input may not have a physical unit.

#### CropParameters_Crops
A list of crop names. Each crop has its own set of crop-specific parameters. One 'crop'
that should normally be specified is 'OffCrop'. Parameters for 'OffCrop' apply to all areas outside 
fields as they are specified by the [Fields_Geometries](#Fields_Geometries).  
`CropParameters_Crops` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_Crops` input may not have a physical unit.

#### CropParameters_PanEvaporationFactors
The PAN evaporation factor of a crop. Each element of the list refers to the crop at the
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_PanEvaporationFactors` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_PanEvaporationFactors` input values is `1`.

#### CropParameters_CanopyInterceptions
The canopy intersection of a crop. Each element of the list refers to the crop at the
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_CanopyInterceptions` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_CanopyInterceptions` input values is `cm`.

#### CropParameters_MaximumCoverages
The maximum soil coverage of a crop. Each element of the list refers to the crop at the
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_MaximumCoverages` expects its values to be of type `list[int]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_MaximumCoverages` input values is `%`.

#### CropParameters_MaximumHeights
The maximum height of a crop. Each element of the list refers to the crop at the same 
position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_MaximumHeights` expects its values to be of type `list[int]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_MaximumHeights` input values is `cm`.

#### CropParameters_MaximumRootingDepths
The maximum rooting depth of a crop. Each element of the list refers to the crop at the
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_MaximumRootingDepths` expects its values to be of type `list[int]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_MaximumRootingDepths` input values is `cm`.

#### CropParameters_Fallows
The fallow parameter of a crop. Each element of the list refers to the crop at the same 
position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_Fallows` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_Fallows` input values is `1`.

#### CropParameters_Cropping
The cropping parameter of a crop. Each element of the list refers to the crop at the 
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_Cropping` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_Cropping` input values is `1`.

#### CropParameters_Residues
The residues of a crop. Each element of the list refers to the crop at the same position
in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_Residues` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_Residues` input values is `1`.

#### CropParameters_EmergenceDates
The date of a year when a crop emerges. Each element of the list refers to the crop at 
the same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_EmergenceDates` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_EmergenceDates` input may not have a physical unit.

#### CropParameters_MaturationDates
The date of a year when a crop matures. Each element of the list refers to the crop at 
the same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_MaturationDates` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_MaturationDates` input may not have a physical unit.

#### CropParameters_HarvestDates
The date of a year of crop harvest. Each element of the list refers to the crop at the 
same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_HarvestDates` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_HarvestDates` input may not have a physical unit.

#### CropParameters_FallowDates
The date of a year when a crop fallows. Each element of the list refers to the crop at 
the same position in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_FallowDates` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_FallowDates` input may not have a physical unit.

#### CropParameters_WaterMitigations
Specifies the rate of water mitigation per crop. This factor feeds an exponential 
decay function to calculate the run-off reduction from cell to cell. Hence, they should be calibrated to
the cell size of the output grid. Each element of the list refers to the crop at the same position in 
the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_WaterMitigations` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_WaterMitigations` input values is `1`.

#### CropParameters_SedimentMitigations
Specifies the rate of sediment mitigation per crop. This factor feeds an exponential 
decay function to calculate the run-off reduction from cell to cell. Hence, they should be calibrated 
to the cell size of the output grid. Each element of the list refers to the crop at the same position 
in the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_SedimentMitigations` expects its values to be of type `list[float]`.
Values have to refer to the `other/crop` scale.
The physical unit of the `CropParameters_SedimentMitigations` input values is `1`.

#### CropParameters_VfsModLookupTables
The file path to a VfsMOD lookup table. Specify `none` if you want to disable the use of 
a lookup table for a specific crop. Each element of the list refers to the crop at the same position in 
the [CropParameters_Crops](#CropParameters_Crops) input.  
`CropParameters_VfsModLookupTables` expects its values to be of type `list[str]`.
Values have to refer to the `other/crop` scale.
Values of the `CropParameters_VfsModLookupTables` input may not have a physical unit.

### Outputs
#### Exposure
Details run-off deposition as generated by PRZM runs per application of a field and after combining
the spatially distributed run-off from all applications at the same day.  
Values are expectedly of type `ndarray`.
Value representation is in a 3-dimensional array.
Dimension 1 spans the number of days covered by [Options_StartDate](#Options_StartDate) and 
                        [Options_EndDate](#Options_EndDate).
Dimension 2 spans the number of meters covered by the [Fields_Extent](#Fields_Extent) in x-direction.
Dimension 3 spans the number of meters covered by the [Fields_Extent](#Fields_Extent) in y-direction.
Chunking of the array is for fast retrieval of spatial patterns.
Individual array elements have a type of `float32`.
The values apply to the following scale: `time/day, space_x/1sqm, space_y/1sqm`.
The physical unit of the values is `g/ha`.


## Roadmap
The following changes will be part of future `RunOffPrzm` versions:
* Documentation of the component needs to be checked and improved
([#1](https://gitlab.bayer.com/aqrisk-landscape/runoffprzm-component/-/issues/1))
* PRZM GUI should be started in the background
([#7](https://gitlab.bayer.com/aqrisk-landscape/runoffprzm-component/-/issues/7))


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)). Also consult the `CONTRIBUTING` 
document for more information.


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
Sascha Bub - sascha.bub@gmx.de  
Joachim Kleinmann - joachim.kleinmann@wsc-regexperts.com  
Thorsten Schad - thorsten.schad@bayer.com  


## Acknowledgements
* [GDAL](https://pypi.org/project/GDAL)  
* [PRZM](https://esdac.jrc.ec.europa.eu/projects/przmsw)  
