"""Class definition for the RunOffPrzm component."""
from osgeo import gdal, ogr, osr
import datetime
import glob
import numpy as np
import os
import shutil
import attrib
import base
import xml.etree.ElementTree
import math


class RunOffPrzm(base.Component):
    """
    RunOffPrzm is a Landscape Model component for simulating run-off processes with the
    [Pesticide Root Zone Model (PRZM)](https://esdac.jrc.ec.europa.eu/projects/przmsw). The component encapsulates a
    module that extends standard PRZM runs for each application within the simulated landscape by a spatial explicit
    surface flow model. `RunOffPrzm` outputs run-off deposition at a square-meter resolution, but the flow model may
    have an arbitrarily coarser resolution. `RunOffPrzm` simulates filtering between square-meter cells either using
    the FOCUS curve number technique or a
    [vegetative filter strip model](https://abe.ufl.edu/faculty/carpena/vfsmod/index.shtml) (VfsMOD).
    """
    # RELEASES
    VERSION = base.VersionCollection(
        base.VersionInfo("2.0.13", "2021-12-30"),
        base.VersionInfo("2.0.12", "2021-10-22"),
        base.VersionInfo("2.0.11", "2021-10-15"),
        base.VersionInfo("2.0.10", "2021-09-08"),
        base.VersionInfo("2.0.9", "2021-07-14"),
        base.VersionInfo("2.0.8", "2021-07-08"),
        base.VersionInfo("2.0.7", "2021-07-05"),
        base.VersionInfo("2.0.6", "2021-06-30"),
        base.VersionInfo("2.0.5", "2021-06-30"),
        base.VersionInfo("2.0.4", "2021-06-29"),
        base.VersionInfo("2.0.3", "2021-06-28"),
        base.VersionInfo("2.0.2", "2021-06-24"),
        base.VersionInfo("2.0.1", "2020-12-09"),
        base.VersionInfo("2.0.0", "2020-10-22"),
        base.VersionInfo("1.3.35", "2020-08-12"),
        base.VersionInfo("1.3.33", "2020-07-30"),
        base.VersionInfo("1.3.27", "2020-05-20"),
        base.VersionInfo("1.3.25", "2020-04-06"),
        base.VersionInfo("1.3.24", "2020-04-02"),
        base.VersionInfo("1.3.18", "2020-03-12"),
        base.VersionInfo("1.3.1", None),
        base.VersionInfo("1.3.0", None),
        base.VersionInfo("1.2.36", None),
        base.VersionInfo("1.2.24", None),
        base.VersionInfo("1.2.23", None),
        base.VersionInfo("1.2.22", None),
        base.VersionInfo("1.2.21", None),
        base.VersionInfo("1.2.20", None),
        base.VersionInfo("1.2.13", None),
        base.VersionInfo("1.2.9", None),
        base.VersionInfo("1.2.5", None),
        base.VersionInfo("1.2.2", None),
        base.VersionInfo("1.1.6", None),
        base.VersionInfo("1.1.5", None),
        base.VersionInfo("1.1.2", None),
        base.VersionInfo("1.1.1", None)
    )

    # AUTHORS
    VERSION.authors.extend((
        "Sascha Bub - sascha.bub@gmx.de",
        "Joachim Kleinmann - joachim.kleinmann@wsc-regexperts.com",
        "Thorsten Schad - thorsten.schad@bayer.com"
    ))

    # ACKNOWLEDGEMENTS
    VERSION.acknowledgements.extend((
        "[GDAL](https://pypi.org/project/GDAL)",
        "[PRZM](https://esdac.jrc.ec.europa.eu/projects/przmsw)"
    ))

    # ROADMAP
    VERSION.roadmap.extend((
        """Documentation of the component needs to be checked and improved
        ([#1](https://gitlab.bayer.com/aqrisk-landscape/runoffprzm-component/-/issues/1))""",
        """PRZM GUI should be started in the background
        ([#7](https://gitlab.bayer.com/aqrisk-landscape/runoffprzm-component/-/issues/7))""",
    ))

    # CHANGELOG
    VERSION.added("1.1.1", "components.RunOffPrzm component")
    VERSION.changed("1.1.2", "components.RunOffPrzm module updated to PRZM Runoff v1.22")
    VERSION.changed("1.1.5", "components.RunOffPrzm stores metadata of PEC")
    VERSION.changed("1.1.6", "components.RunOffPrzm input Fields_InFieldMargin must be 0")
    VERSION.changed("1.1.6", "components.RunOffPrzm in-Crop-Buffer input must be 0")
    VERSION.changed("1.2.2", "components.RunOffPrzm module updated to PRZM Runoff v1.23")
    VERSION.changed("1.2.5", "components.RunOffPrzm module updated to PRZM Runoff v1.24")
    VERSION.changed("1.2.9", "components.RunOffPrzm module updated to PRZM Runoff v1.25")
    VERSION.changed("1.2.9", "components.RunOffPrzm now uses inclusive simulation time boundaries")
    VERSION.changed("1.2.13", "components.RunOffPrzm module updated to PRZM Runoff v1.26")
    VERSION.changed("1.2.20", "components.RunOffPrzm module updated to PRZM Runoff v1.3")
    VERSION.changed("1.2.21", "components.RunOffPrzm clips input arrays to handle null values as zero exposure")
    VERSION.changed("1.2.21", "components.RunOffPrzm module updated to PRZM Runoff v1.31")
    VERSION.changed("1.2.21", "components.RunOffPrzm acknowledges delete_all_interim_results parameter")
    VERSION.changed("1.2.22", "components.RunOffPrzm processes in-field-margin")
    VERSION.changed("1.2.23", "components.RunOffPrzm input controlling intermediary file deletion")
    VERSION.changed("1.2.24", "components.RunOffPrzm module updated to PRZM Runoff v1.32")
    VERSION.changed("1.2.36", "components.RunOffPrzm module updated to PRZM Runoff v1.33")
    VERSION.changed("1.3.0", "components.RunOffPrzm module updated to PRZM Runoff v1.33b")
    VERSION.changed("1.3.0", "components.RunOffPrzm module updated to PRZM Runoff v1.33c")
    VERSION.changed("1.3.18", "components.RunOffPrzm module updated to PRZM Runoff v1.4")
    VERSION.changed("1.3.24", "components.RunOffPrzm uses base function to call module")
    VERSION.changed("1.3.25", "Added missing use_vfs_mod parameter in components.RunOffPrzm")
    VERSION.changed("1.3.27", "components.RunOffPrzm module updated to PRZM Runoff v1.42")
    VERSION.fixed("1.3.33", "components.RunOffPrzm parameterization adapted to the newest version (spelling error)")
    VERSION.fixed("1.3.35", "components.RunOffPrzm module updated to PRZM Runoff v1.44")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.changed("2.0.1", "Module updated to PRZM Runoff v1.45")
    VERSION.changed("2.0.2", "Updated data type access")
    VERSION.changed("2.0.3", "Crop parameterization added to component configuration")
    VERSION.changed("2.0.4", "Added semantic descriptions of input parameters")
    VERSION.changed("2.0.5", "Added further unit attributes to the component's inputs")
    VERSION.changed("2.0.6", "Minor changes in input descriptions")
    VERSION.changed("2.0.7", "No longer transforms date coordinates")
    VERSION.changed("2.0.8", "Added documentation of inputs and outputs")
    VERSION.fixed("2.0.9", "Error in changelog title")
    VERSION.changed("2.0.10", "Renamed LICENSE.txt to LICENSE")
    VERSION.changed("2.0.11", "Switched to Google-style docstrings")
    VERSION.changed("2.0.11", "Updated `attrib.Class` definitions to generic types")
    VERSION.changed("2.0.12", "Replaced GDAL constants by numerical values")
    VERSION.changed("2.0.13", "Output scale order (y,x,t instead of t,x,y)")

    def __init__(self, name, observer, store):
        """
        Initializes a RunOffPrzm component.

        Args:
            name: The name of the component.
            observer: The default observer of the component.
            store: The default store of the component.
        """
        super(RunOffPrzm, self).__init__(name, observer, store)
        self._module = base.Module("PRZM_Runoff", "1.47", "Release 1.4\\Changelog.txt")
        self._inputs = base.InputContainer(self, (
            base.Input(
                "ProcessingPath",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""The working directory for the module. It is used for all files prepared as module inputs
                or generated as module outputs. This excludes the files of the actual PRZM run whose path. See the 
                [Options_TemporaryOutputPath](#Options_TemporaryOutputPath) input for the according parameterization. 
                the `ProcessingPath` are considered temporary and can be safely deleted after a successful simulation 
                run. Make sure that the `ProcessingPath` is configured in such a way that it does not collide with
                other simulation runs (of different experiments or Monte Carlo runs)."""
            ),
            base.Input(
                "Model_AdsorptionMethod",
                (
                    attrib.Class(str),
                    attrib.Scales("global"),
                    attrib.Unit(None),
                    attrib.InList(("linear", "Freundlich", "aged"))
                ),
                self.default_observer,
                description="""Specifies how PRZM simulates adsorption. Three methods are available: `linear` 
                calculates adsorption based on a linear regression, `Freundlich` based on a normalized Freundlich 
                equation and `aged` uses an aged adsorption function."""
            ),
            base.Input(
                "Model_SoilTemperatureSimulation",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Specifies whether to simulate soil temperature or not. Enabled soil temperature 
                simulation does not consider nitrogen transport."""
            ),
            base.Input(
                "SubstanceName",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Substances differ in their properties and, thus, for every substance simulated a 
                different set of values has to be specified. The current `RunOffPrzm` component does, however, allow to 
                simulate a single substance only. This might change in the future, as the module is conceptually and 
                technically prepared to handle multiple substances simultaneously. The `SubstanceName` has currently
                no technical relevance."""
            ),
            base.Input(
                "Substance_PlantUptakeFactor",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1/d")),
                self.default_observer,
                description="The substance-specific PRZM plant uptake factor."
            ),
            base.Input(
                "Substance_PesticideDissipationRateOfFoliage",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1/d")),
                self.default_observer,
                description="The substance-specific PRZM pesticide dissipation rate on foliage."
            ),
            base.Input(
                "Substance_FoliarWashOffCoefficient",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1/cm")),
                self.default_observer,
                description="The substance-specific PRZM foliar wash-off coefficient."
            ),
            base.Input(
                "Substance_HenryConstant",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1")),
                self.default_observer,
                description="""The substance-specific Henry constant. You can also set this input to the special value
                of `nan` to let the module derive the Henry constant from the input values of
                [Substance_VapourPressure](#Substance_VapourPressure),
                [Substance_MolecularWeight](#Substance_MolecularWeight), 
                [Substance_WaterSolubility](#Substance_WaterSolubility) and 
                [Substance_TemperatureAtWhichMeasured](#Substance_TemperatureAtWhichMeasured)."""
            ),
            base.Input(
                "Substance_VapourPressure",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("mPa")),
                self.default_observer,
                description="The substance-specific vapor pressure."
            ),
            base.Input(
                "Substance_MolecularWeight",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("g/mol")),
                self.default_observer,
                description="The substance-specific molecular weight."
            ),
            base.Input(
                "Substance_WaterSolubility",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("mg/L")),
                self.default_observer,
                description="The substance-specific water solubility."
            ),
            base.Input(
                "Substance_TemperatureAtWhichMeasured",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("K")),
                self.default_observer,
                description="The reference temperature for the physical and chemical properties of the substance."
            ),
            base.Input(
                "Substance_FreundlichExponent",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1")),
                self.default_observer,
                description="The substance-specific Freundlich exponent."
            ),
            base.Input(
                "Substance_ReferenceMoistureForDT50Soil",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("%")),
                self.default_observer,
                description="The substance-specific reference moisture for the soil DT50 in percent of field capacity."
            ),
            base.Input(
                "Substance_SoilDT50",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("d")),
                self.default_observer,
                description="The substance-specific soil half-life time."
            ),
            base.Input(
                "Substance_KocSoil",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("cm³/g")),
                self.default_observer,
                description="The substance-specific KOC in soil."
            ),
            base.Input(
                "SprayApplication_PrzmApplicationMethod",
                (
                    attrib.Class(str),
                    attrib.Scales("global"),
                    attrib.Unit(None),
                    attrib.InList(("soil", "canopy", "foliar"))
                ),
                self.default_observer,
                description="""The PRZM chemical application method that is assumed for all spray applications. `soil`
                indicates direct spraying of the soil surface, `canopy` of the crop canopy and `foliar` a foliar
                application."""
            ),
            base.Input(
                "SprayApplication_IncorporationDepth",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("cm")),
                self.default_observer,
                description="The PRZM incorporation depth of spray applications."
            ),
            base.Input(
                "Options_StartDate",
                (attrib.Class(datetime.date, 1), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="The first simulated date. All temporal input parameters must start at this date."
            ),
            base.Input(
                "Options_EndDate",
                (attrib.Class(datetime.date, 1), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="The last simulated date. All temporal input parameters must end at this date."
            ),
            base.Input(
                "Options_TemporaryOutputPath",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""PRZM cannot run in paths with long names. The [ProcessingPath](#ProcessingPath), due to 
                its requirement to be unique for each simulation run, is normally too long to be used here. Instead, 
                PRZM simulations run in the directory specified by the `Options_TemporaryOutputPath` input."""
            ),
            base.Input(
                "Options_DeleteTemporaryGrids",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""`RunOffPrzm` creates an output grid for each field in the landscape before it merges 
                them. If the temporary output of each field should be deleted as early as possible, set this option to `
                true`. `False` is the right option if you need to keep the temporary grids, e.g., for debugging."""
            ),
            base.Input(
                "Options_TimeoutSecPrzm",
                (attrib.Class(int), attrib.Scales("global"), attrib.Unit("s")),
                self.default_observer,
                description="""The time after which an idle PRZM instance timeouts. Tweak this option to prevent locks
                            in some rare circumstances."""
            ),
            base.Input(
                "Options_ReportingThreshold",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("mg")),
                self.default_observer,
                description="""The minimum mass that is required to trigger continuation of the water and substance 
                flow simulation. Smaller masses remain at the current cell and are not further transported. Set this
                option to a sensible value that allows to capture all relevant depositions while reducing the processing
                time."""
            ),
            base.Input(
                "Options_DeleteAllInterimResults",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Specifies whether to delete all intermediary files after a successful simulation run.
                Enable this option to save disk space (intermediary files may accumulate to a considerable amount) or
                disable it if you need to keep intermediary files, e.g., for debugging."""
            ),
            base.Input(
                "Weather_Precipitation",
                (attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("mm/d")),
                self.default_observer,
                description="""A series of daily precipitation values. The series must cover the entire range between
                [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order."""
            ),
            base.Input(
                "Weather_ET0",
                (attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("mm/d")),
                self.default_observer,
                description="""A series of daily evapotranspiration values. The series must cover the entire range 
                between [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive
                order."""
            ),
            base.Input(
                "Weather_Temperature",
                (attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("°C")),
                self.default_observer,
                description="""A series of daily temperature values. The series must cover the entire range between
                [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order."""
            ),
            base.Input(
                "Weather_WindSpeed",
                (attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("m/s")),
                self.default_observer,
                description="""A series of daily wind speed values. The series must cover the entire range between
                [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order."""
            ),
            base.Input(
                "Weather_SolarRadiation",
                (attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("kJ/(m²*d)")),
                self.default_observer,
                description="""A series of daily solar radiation values. The series must cover the entire range between
                [Options_StartDate](#Options_StartDate) and [Options_EndDate](#Options_EndDate) in consecutive order."""
            ),
            base.Input(
                "Fields_Slope",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("%")),
                self.default_observer,
                description="""The average slope of all fields in the landscape. This slope is feeds PRZM run-off
                calculations and is independent of the slopes underlying the [Fields_FlowGrid](#Fields_FlowGrid). 
                Please make sure that representation of slopes is somewhat consistent between landscape scenario and 
                `RunOffPrzm` parameterization. A later version may allow specifying slopes on a per-field basis instead
                of globally."""
            ),
            base.Input(
                "Fields_SoilHorizonThicknesses",
                (attrib.Class(list[float], 1), attrib.Scales("other/soil_horizon"), attrib.Unit("cm")),
                self.default_observer,
                description="""A sequence of soil horizon depths from top to bottom. This sequence defines how many
                soil horizons there are and how they are distributed along the z-axis."""
            ),
            base.Input(
                "Fields_SoilHorizonBulkDensities",
                (attrib.Class(list[float], 1), attrib.Scales("other/soil_horizon"), attrib.Unit("g/cm³")),
                self.default_observer,
                description="""A sequence of soil horizon bulk densities from top to bottom. This sequence must have the
                same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
                Elements refer to the same soil horizon (in the same order) as the soil horizons specified there."""
            ),
            base.Input(
                "Fields_SoilHorizonOrganicMaterialContents",
                (attrib.Class(list[float], 1), attrib.Scales("other/soil_horizon"), attrib.Unit("%")),
                self.default_observer,
                description="""A sequence of soil horizon organic material contents from top to bottom. This sequence 
                must have the same number of elements as the 
                [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence. Elements refer to the same 
                soil horizon (in the same order) as the soil horizons specified there."""
            ),
            base.Input(
                "Fields_SoilHorizonSandFractions",
                (attrib.Class(list[float], 1), attrib.Scales("other/soil_horizon"), attrib.Unit("%")),
                self.default_observer,
                description="""A sequence of soil horizon sand fractions from top to bottom. This sequence must have the
                same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
                Elements refer to the same soil horizon (in the same order) as the soil horizons specified there."""
            ),
            base.Input(
                "Fields_SoilHorizonSiltFractions",
                (attrib.Class(list[float], 1), attrib.Scales("other/soil_horizon"), attrib.Unit("%")),
                self.default_observer,
                description="""A sequence of soil horizon silk fractions from top to bottom. This sequence must have the
                same number of elements as the [Fields_SoilHorizonThicknesses](#Fields_SoilHorizonThicknesses) sequence.
                Elements refer to the same soil horizon (in the same order) as the soil horizons specified there."""
            ),
            base.Input(
                "Fields_Geometries",
                (attrib.Class(list[bytes]), attrib.Scales("space/base_geometry"), attrib.Unit(None)),
                self.default_observer,
                description="""The geometries of in-field areas in WKB representation. Each element refers to a field
                with its according identifier from the list of [Fields_Ids](#Fields_Ids)."""
            ),
            base.Input(
                "Fields_Ids",
                (attrib.Class(list[int]), attrib.Scales("space/base_geometry"), attrib.Unit(None)),
                self.default_observer,
                description="""The simulation-wide unique identifiers of fields within the landscape. These identifiers
                stem from the landscape scenario and are shared among components."""
            ),
            base.Input(
                "Fields_Crs",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""The coordinate reference system in which the [Fields_Geometries](#Fields_Geometries) 
                are projected. The coordinate reference system needs to be in Proj4 notation."""
            ),
            base.Input(
                "Fields_Extent",
                (attrib.Class(tuple[float]), attrib.Scales("space/extent"), attrib.Unit("metre")),
                self.default_observer,
                description="""The extent of the simulated landscape. This value has to be consistent with the 
                [Fields_Geometries](#Fields_Geometries) and the [Fields_FlowGrid](#Fields_FlowGrid) and is projected
                in the [Fields_Crs](#Fields_Crs). The landscape scenario normally takes care of that."""
            ),
            base.Input(
                "Fields_FlowGrid",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""The file path to a raster file that contains information about the flow direction 
                between individual raster cells. Flow directions follow the [ESRI standard](
                https://desktop.arcgis.com/de/arcmap/10.3/tools/spatial-analyst-toolbox/flow-direction.htm) encoding 
                for flow directions."""
            ),
            base.Input(
                "Fields_InFieldMargin",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("m")),
                self.default_observer,
                description="""A width of an inner margin along field boundaries that is not covered with crop but with
                other herbaceous vegetation. This value applies to all fields in the landscape and does not change over
                time, but a future version of the component may allow for spatio-temporal variation."""
            ),
            base.Input(
                "Ppm_AppliedFields",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer,
                description="""The identifiers of applied fields (according to the [Fields_Ids](#Fields_Ids)) per 
                application. The number of elements defines how many applications there are in total, and the values
                link applications to individual fields."""
            ),
            base.Input(
                "Ppm_ApplicationDates",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer,
                description="""The dates of application. This specifies for each application indicated by the 
                [Ppm_AppliedFields](#Ppm_AppliedFields), on which day the application took place."""
            ),
            base.Input(
                "Ppm_ApplicationRates",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit("g/ha")),
                self.default_observer,
                description="""This indicates for each application indicated by the 
                [Ppm_AppliedFields](#Ppm_AppliedFields) at which rate the substance with the name of 
                [SubstanceName](#SubstanceName) was applied."""
            ),
            base.Input(
                "Ppm_AppliedAreas",
                (attrib.Class(list[bytes]), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer,
                description="""For each application indicated by the [Ppm_AppliedFields](#Ppm_AppliedFields), this gives
                the geometry of the actual applied area in WKB representation. This geometry might be equal to or 
                smaller and located within the field geometry given by the [Fields_Geometries](#Fields_Geometries). Only
                the area indicated by the `Ppm_AppliedAreas` is actually applied, allowing to leave in-crop buffers or
                depict spatial variation of the application relative to the field geometry."""
            ),
            base.Input(
                "Options_ShowExtendedErrorInformation",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="Specifies whether the module prompts extended information on errors or not."
            ),
            base.Input(
                "Options_MethodOfRunoffGeneration",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None), attrib.InList(("PRZM", "FOCUS"))),
                self.default_observer,
                description="""Specifies the method used to simulate the amount of run-off. `PRZM` specifies to use PRZM
                runs for run-off generation, `FOCUS` to use FOCUS Step2 run-off simulations."""
            ),
            base.Input(
                "Options_UsePreSimulatedPrzmResults",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Specifies using pre-simulated PRZM runs for run-off simulation instead of new PRZM 
                runs."""
            ),
            base.Input(
                "Options_UseOnePrzmModelPerGridCell",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Specifies to start an individual PRZM run for every cell to calculate run-off. Enabling 
                this parameter results in many PRZM runs, resulting in considerably longer simulation runs. Usage of 
                PRZM for the purpose of run-off generation in off-crop cells should also be seen as experimental."""
            ),
            base.Input(
                "Options_UseVfsMod",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer,
                description="""Specifies whether to use crop-specific VfsMOD lookup tables to simulate run-off 
                filtering. The [CropParameters_VfsModLookupTables](#CropParameters_VfsModLookupTables) input 
                parameterizes which lookup table to use for which crop."""
            ),
            base.Input(
                "CropParameters_Crops",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""A list of crop names. Each crop has its own set of crop-specific parameters. One 'crop'
                that should normally be specified is 'OffCrop'. Parameters for 'OffCrop' apply to all areas outside 
                fields as they are specified by the [Fields_Geometries](#Fields_Geometries)."""
            ),
            base.Input(
                "CropParameters_PanEvaporationFactors",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""The PAN evaporation factor of a crop. Each element of the list refers to the crop at the
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_CanopyInterceptions",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("cm")),
                self.default_observer,
                description="""The canopy intersection of a crop. Each element of the list refers to the crop at the
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_MaximumCoverages",
                (attrib.Class(list[int]), attrib.Scales("other/crop"), attrib.Unit("%")),
                self.default_observer,
                description="""The maximum soil coverage of a crop. Each element of the list refers to the crop at the
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_MaximumHeights",
                (attrib.Class(list[int]), attrib.Scales("other/crop"), attrib.Unit("cm")),
                self.default_observer,
                description="""The maximum height of a crop. Each element of the list refers to the crop at the same 
                position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_MaximumRootingDepths",
                (attrib.Class(list[int]), attrib.Scales("other/crop"), attrib.Unit("cm")),
                self.default_observer,
                description="""The maximum rooting depth of a crop. Each element of the list refers to the crop at the
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_Fallows",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""The fallow parameter of a crop. Each element of the list refers to the crop at the same 
                position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_Cropping",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""The cropping parameter of a crop. Each element of the list refers to the crop at the 
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_Residues",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""The residues of a crop. Each element of the list refers to the crop at the same position
                in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_EmergenceDates",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""The date of a year when a crop emerges. Each element of the list refers to the crop at 
                the same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_MaturationDates",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""The date of a year when a crop matures. Each element of the list refers to the crop at 
                the same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_HarvestDates",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""The date of a year of crop harvest. Each element of the list refers to the crop at the 
                same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_FallowDates",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""The date of a year when a crop fallows. Each element of the list refers to the crop at 
                the same position in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_WaterMitigations",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""Specifies the rate of water mitigation per crop. This factor feeds an exponential 
                decay function to calculate the run-off reduction from cell to cell. Hence, they should be calibrated to
                the cell size of the output grid. Each element of the list refers to the crop at the same position in 
                the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_SedimentMitigations",
                (attrib.Class(list[float]), attrib.Scales("other/crop"), attrib.Unit("1")),
                self.default_observer,
                description="""Specifies the rate of sediment mitigation per crop. This factor feeds an exponential 
                decay function to calculate the run-off reduction from cell to cell. Hence, they should be calibrated 
                to the cell size of the output grid. Each element of the list refers to the crop at the same position 
                in the [CropParameters_Crops](#CropParameters_Crops) input."""
            ),
            base.Input(
                "CropParameters_VfsModLookupTables",
                (attrib.Class(list[str]), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer,
                description="""The file path to a VfsMOD lookup table. Specify `none` if you want to disable the use of 
                a lookup table for a specific crop. Each element of the list refers to the crop at the same position in 
                the [CropParameters_Crops](#CropParameters_Crops) input."""
            )
        ))
        self._outputs = base.OutputContainer(self, (
            base.Output(
                "Exposure",
                store,
                self,
                {"data_type": np.float32, "scales": "space_y/1sqm, space_x/1sqm, time/day", "unit": "g/ha"},
                """Details run-off deposition as generated by PRZM runs per application of a field and after combining
                the spatially distributed run-off from all applications at the same day.""",
                {
                    "type": np.ndarray,
                    "shape": (
                        """the number of days covered by [Options_StartDate](#Options_StartDate) and 
                        [Options_EndDate](#Options_EndDate)""",
                        "the number of meters covered by the [Fields_Extent](#Fields_Extent) in x-direction",
                        "the number of meters covered by the [Fields_Extent](#Fields_Extent) in y-direction"
                    ),
                    "chunks": "for fast retrieval of spatial patterns"
                }
            ),
        ))

    def convert_to_przm_date(self, date, max_date):
        """
        Converts a date to a PRZM date.

        Args:
            date: The actual date.
            max_date: The latest date of the simulated date range.

        Returns:
            The date mapped as PRZM date.
        """
        return datetime.datetime(self.convert_to_przm_year(date.year, max_date.year), date.month, date.day).date()

    @staticmethod
    def convert_to_przm_year(year, max_year):
        """
        Converts a year to a PRZM year.

        Args:
            year: The actual year.
            max_year: The latest year of the simulated date range.

        Returns:
            The year mapped as PRZM year.
        """
        if max_year <= 1999:
            return year
        correct_year = max_year - 1999
        if correct_year % 4 != 0:
            correct_year += 4 - (correct_year % 4)
        return year - correct_year

    def run(self):
        """
        Runs the component.

        Returns:
            Nothing.
        """
        exe = os.path.join(os.path.dirname(__file__), "Release 1.4", "PRZM_Runoff.exe")
        exe2 = os.path.join(os.path.dirname(__file__), "Release 1.4", "HydroFilter_Runoff.exe")
        processing_path = self.inputs["ProcessingPath"].read().values
        source_flow_grid = self._inputs["Fields_FlowGrid"].read().values
        przm_folder = os.path.join(processing_path, "przm")
        przm_config = os.path.join(processing_path, "parameters.xml")
        ppp_repository = os.path.join(processing_path, "PPP.xml")
        cropping_statistic_przm = os.path.join(processing_path, "CroppingStatistics_PRZM.xml")
        ppm_calendar_przm = os.path.join(processing_path, "PPM_CALENDAR_PRZM.xml")
        crop_parameterization = os.path.join(processing_path, "CropParameters.xml")
        run_off_field_discrete = os.path.join(processing_path, "Fields.tif")
        run_off_field_parameters = os.path.join(processing_path, "field_parameterization.xml")
        flow_grid = os.path.join(processing_path, "flow.tif")
        # noinspection SpellCheckingInspection
        przm_weather = os.path.join(processing_path, "focusprzm_weather.met")
        # noinspection SpellCheckingInspection
        applied_areas_path = os.path.join(processing_path, "appl")
        try:
            os.makedirs(przm_folder)
        except FileExistsError:
            raise FileExistsError("Cannot run PRZM in a path that already exists: " + processing_path)
        shutil.copyfile(source_flow_grid, flow_grid)
        self.write_configuration_xml(ppp_repository,
                                     cropping_statistic_przm,
                                     ppm_calendar_przm,
                                     crop_parameterization,
                                     run_off_field_discrete,
                                     run_off_field_parameters,
                                     flow_grid,
                                     przm_weather,
                                     przm_config)
        self.write_przm_weather_file(przm_weather)
        self.write_field_parameters_file(run_off_field_parameters)
        self.write_field_raster(run_off_field_discrete)
        self.write_cropping_statistics(cropping_statistic_przm)
        self.write_ppp_repository(ppp_repository)
        spatial_info = self.collect_spatial_application_info()
        self.write_ppm_calendar(ppm_calendar_przm, applied_areas_path, spatial_info[0])
        self.write_applied_area_raster(applied_areas_path, spatial_info[1])
        self.write_crop_parameters(crop_parameterization)
        # noinspection SpellCheckingInspection
        base.run_process((exe, "-ifile", przm_config, przm_folder), processing_path, self.default_observer)
        # noinspection SpellCheckingInspection
        base.run_process((exe2, "-ifile", przm_config, przm_folder), processing_path, self.default_observer)
        if not os.path.exists(os.path.join(przm_folder, "successful.txt")):
            raise Exception("Run-off run was not successful")
        simulation_start = self.inputs["Options_StartDate"].read().values
        simulation_end = self.inputs["Options_EndDate"].read().values
        simulation_length = (simulation_end - simulation_start).days + 1
        extent = self.inputs["Fields_Extent"].read().values
        raster_cols = int(round(extent[1] - extent[0]))
        raster_rows = int(round(extent[3] - extent[2]))
        self.outputs["Exposure"].set_values(
            np.ndarray,
            shape=(raster_rows, raster_cols, simulation_length),
            chunks=base.chunk_size((None, None, 1), (raster_rows, raster_cols, simulation_length)),
            offset=(extent[2], extent[0], simulation_start)
        )
        input_raster = {}
        for raster in glob.iglob(przm_folder + "/**/output/*.tif", recursive=True):
            day_string = os.path.basename(raster)[-9:-4]
            if day_string != "f_grd":
                if day_string in input_raster:
                    input_raster[day_string] += [raster]
                else:
                    input_raster[day_string] = [raster]
        for day, raster_inputs in input_raster.items():
            runoff_day = int(day)
            exposure = np.zeros((raster_rows, raster_cols, 1))
            data_slice = (slice(0, raster_rows), slice(0, raster_cols), slice(runoff_day, runoff_day + 1))
            for raster in raster_inputs:
                exposure_raster = gdal.Open(raster, 0)
                exposure_raster_band = exposure_raster.GetRasterBand(1)
                exposure_array = exposure_raster_band.ReadAsArray().clip(0)
                del exposure_raster
                exposure_array.shape += (1,)
                exposure += exposure_array
            self.outputs["Exposure"].set_values(exposure, slices=data_slice, create=False, calculate_max=True)

    def write_configuration_xml(self, ppp_repository, cropping_calendar, ppm_calendar, crop_parameterization,
                                field_discrete, field_parameters, flow_grid, przm_weather, output_file):
        """
        Writes the input parameterization for the module.

        Args:
            ppp_repository: The file path of the PPP repository.
            cropping_calendar: The file path of the cropping calendar.
            ppm_calendar: The file path of the PPM calendar.
            crop_parameterization: The file path of the crop parameterization.
            field_discrete: The file path of the fields.
            field_parameters: The file path of the field parameters.
            flow_grid: The file path of the flow grid.
            przm_weather: The file path of the weather.
            output_file: The file path of the module output.

        Returns:
            Nothing.
        """
        parameters = xml.etree.ElementTree.Element("parameters")
        model = xml.etree.ElementTree.SubElement(parameters, "model")
        henry_constant = self.inputs["Substance_HenryConstant"].read().values
        xml.etree.ElementTree.SubElement(model, "adsorption_method").text = {
            "linear": "1", "Freundlich": "2", "aged": "3"}[self.inputs["Model_AdsorptionMethod"].read().values]
        xml.etree.ElementTree.SubElement(model, "soil_temperature_simulation").text = "2" if self.inputs[
            "Model_SoilTemperatureSimulation"].read().values else "0"
        substances = xml.etree.ElementTree.SubElement(parameters, "substances")
        substance = xml.etree.ElementTree.SubElement(
            substances, "substance", {"name": self.inputs["SubstanceName"].read().values})
        xml.etree.ElementTree.SubElement(substance, "plant_uptake_factor").text = str(self.inputs[
            "Substance_PlantUptakeFactor"].read().values)
        xml.etree.ElementTree.SubElement(substance, "pesticide_dissipation_rate_of_foliage").text = str(self.inputs[
            "Substance_PesticideDissipationRateOfFoliage"].read().values)
        xml.etree.ElementTree.SubElement(substance, "foliar_wash_off_coefficient").text = str(self.inputs[
            "Substance_FoliarWashOffCoefficient"].read().values)
        if not math.isnan(henry_constant):
            xml.etree.ElementTree.SubElement(substance, "henry_constant").text = str(henry_constant)
        xml.etree.ElementTree.SubElement(substance, "vapour_pressure").text = str(self.inputs[
            "Substance_VapourPressure"].read().values)
        xml.etree.ElementTree.SubElement(substance, "molecular_weight").text = str(self.inputs[
            "Substance_MolecularWeight"].read().values)
        xml.etree.ElementTree.SubElement(substance, "water_solubility").text = str(self.inputs[
            "Substance_WaterSolubility"].read().values)
        xml.etree.ElementTree.SubElement(substance, "temperature_at_which_measured").text = str(self.inputs[
            "Substance_TemperatureAtWhichMeasured"].read().values)
        xml.etree.ElementTree.SubElement(substance, "freundlich_exponent").text = str(self.inputs[
            "Substance_FreundlichExponent"].read().values)
        xml.etree.ElementTree.SubElement(substance, "reference_moisture_for_dt50_soil").text = str(self.inputs[
            "Substance_ReferenceMoistureForDT50Soil"].read().values)
        xml.etree.ElementTree.SubElement(substance, "soil_dt50").text = str(
            self.inputs["Substance_SoilDT50"].read().values)
        xml.etree.ElementTree.SubElement(substance, "koc_soil").text = str(
            self.inputs["Substance_KocSoil"].read().values)
        ppp = xml.etree.ElementTree.SubElement(parameters, "ppp")
        xml.etree.ElementTree.SubElement(ppp, "ppp_repository").text = ppp_repository
        cropping = xml.etree.ElementTree.SubElement(parameters, "cropping")
        xml.etree.ElementTree.SubElement(cropping, "cropping_calendar").text = cropping_calendar
        xml.etree.ElementTree.SubElement(cropping, "ppm_calendar").text = ppm_calendar
        chemical_application_methods = xml.etree.ElementTree.SubElement(cropping, "chemical_application_methods")
        chemical_application_method_spray_application = xml.etree.ElementTree.SubElement(
            chemical_application_methods, "chemical_application_method", {"name": "SprayApplication"})
        xml.etree.ElementTree.SubElement(
            chemical_application_method_spray_application, "przm_application_method").text = {
            "soil": "0",
            "canopy": "1",
            "foliar": "2"}[
            self.inputs["SprayApplication_PrzmApplicationMethod"].read().values]
        xml.etree.ElementTree.SubElement(
            chemical_application_method_spray_application, "incorporation_depth").text = str(
            self.inputs["SprayApplication_IncorporationDepth"].read().values)
        # noinspection SpellCheckingInspection
        xml.etree.ElementTree.SubElement(cropping, "crop_parameterisation").text = crop_parameterization
        landscape = xml.etree.ElementTree.SubElement(parameters, "landscape")
        # noinspection SpellCheckingInspection
        xml.etree.ElementTree.SubElement(landscape, "field_discretisation").text = field_discrete
        xml.etree.ElementTree.SubElement(landscape, "parameters_as_xml").text = field_parameters
        xml.etree.ElementTree.SubElement(landscape, "flow").text = flow_grid
        weather = xml.etree.ElementTree.SubElement(parameters, "weather")
        xml.etree.ElementTree.SubElement(weather, "przm_weather_file").text = przm_weather
        options = xml.etree.ElementTree.SubElement(parameters, "options")
        simulation_end = self.inputs["Options_EndDate"].read().values
        xml.etree.ElementTree.SubElement(options, "start_date").text = str(
            self.convert_to_przm_date(self.inputs["Options_StartDate"].read().values, simulation_end))
        xml.etree.ElementTree.SubElement(options, "end_date").text = str(
            self.convert_to_przm_date(simulation_end, simulation_end))
        xml.etree.ElementTree.SubElement(options, "temporary_output_path").text = self.inputs[
            "Options_TemporaryOutputPath"].read().values
        xml.etree.ElementTree.SubElement(options, "delete_temporary_grids").text = "1" if self.inputs[
            "Options_DeleteTemporaryGrids"].read().values else "0"
        xml.etree.ElementTree.SubElement(options, "TimeoutSecPRZM").text = str(
            self.inputs["Options_TimeoutSecPrzm"].read().values)
        # noinspection SpellCheckingInspection
        xml.etree.ElementTree.SubElement(options, "reporting_threashold").text = str(
            self.inputs["Options_ReportingThreshold"].read().values)
        xml.etree.ElementTree.SubElement(options, "method_of_runoff_generation").text = {
            "PRZM": "1", "FOCUS": "0"}[self.inputs["Options_MethodOfRunoffGeneration"].read().values]
        xml.etree.ElementTree.SubElement(options, "delete_all_interim_results").text = "1" if self.inputs[
            "Options_DeleteAllInterimResults"].read().values else "0"
        # noinspection SpellCheckingInspection
        xml.etree.ElementTree.SubElement(options, "show_extended_error_infos").text = "1" if self.inputs[
            "Options_ShowExtendedErrorInformation"].read().values else "0"
        # noinspection SpellCheckingInspection
        xml.etree.ElementTree.SubElement(options, "use_presimulated_przm_results").text = "1" if self.inputs[
            "Options_UsePreSimulatedPrzmResults"].read().values else "0"
        xml.etree.ElementTree.SubElement(options, "use_one_przm_model_per_grid_cell").text = "1" if self.inputs[
            "Options_UseOnePrzmModelPerGridCell"].read().values else "0"
        xml.etree.ElementTree.SubElement(options, "use_vfs_mod").text = "1" if self.inputs[
            "Options_UseVfsMod"].read().values else "0"
        xml.etree.ElementTree.ElementTree(parameters).write(output_file, encoding="utf-8", xml_declaration=True)

    def write_przm_weather_file(self, output_file):
        """
        Prepares the weather input.

        Args:
            output_file: The file path of the weather input.

        Returns:
            Nothing.
        """
        start_date = self.inputs["Options_StartDate"].read().values
        end_date = self.inputs["Options_EndDate"].read().values
        precipitation = self._inputs["Weather_Precipitation"].read()
        et0 = self._inputs["Weather_ET0"].read()
        temperature = self._inputs["Weather_Temperature"].read()
        wind_speed = self._inputs["Weather_WindSpeed"].read()
        radiation = self._inputs["Weather_SolarRadiation"].read()
        weather_file = open(output_file, "w")
        for i in range((end_date - start_date).days + 1):
            date = start_date + datetime.timedelta(i)
            mapped_date = self.convert_to_przm_date(date, end_date)
            weather_file.write(" {:02d}{:02d}{:02d}{:>10.4f}{:>10.4f}{:>10.4f}{:>10.4f}{:>10.4f}\n".format(
                mapped_date.month,
                mapped_date.day,
                mapped_date.year - 1900,
                precipitation.values[i] / 10,
                et0.values[i] / 10,
                temperature.values[i],
                wind_speed.values[i] * 100,
                radiation.values[i] / 41.84))
        weather_file.close()

    def write_field_parameters_file(self, output_file):
        """
        Prepares the field parameters.

        Args:
            output_file: Te file path of the field parameters.

        Returns:
            Nothing.
        """
        applied_fields = self.inputs["Ppm_AppliedFields"].read().values
        slope = self.inputs["Fields_Slope"].read()
        soil_horizon_thicknesses = self.inputs["Fields_SoilHorizonThicknesses"].read()
        soil_horizon_bulk_densities = self.inputs["Fields_SoilHorizonBulkDensities"].read()
        soil_horizon_organic_material_contents = self.inputs["Fields_SoilHorizonOrganicMaterialContents"].read()
        soil_horizon_sand_fractions = self.inputs["Fields_SoilHorizonSandFractions"].read()
        soil_horizon_silt_fractions = self.inputs["Fields_SoilHorizonSiltFractions"].read()
        fields = xml.etree.ElementTree.Element("fields")
        field_ids = set(applied_fields)
        for fieldId in field_ids:
            field = xml.etree.ElementTree.SubElement(fields, "field", {"id": str(fieldId)})
            xml.etree.ElementTree.SubElement(field, "slope").text = str(slope.values)
            soil_horizons = xml.etree.ElementTree.SubElement(field, "soil_horizons")
            for soilHorizonId in range(len(soil_horizon_thicknesses.values)):
                soil_horizon = xml.etree.ElementTree.SubElement(soil_horizons,
                                                                "soil_horizon",
                                                                {"id": str(soilHorizonId + 1)})
                xml.etree.ElementTree.SubElement(soil_horizon, "thickness").text = str(
                    soil_horizon_thicknesses.values[soilHorizonId])
                xml.etree.ElementTree.SubElement(soil_horizon, "BD").text = str(
                    soil_horizon_bulk_densities.values[soilHorizonId])
                xml.etree.ElementTree.SubElement(soil_horizon, "omc").text = str(
                    soil_horizon_organic_material_contents.values[soilHorizonId])
                xml.etree.ElementTree.SubElement(soil_horizon, "sand").text = str(
                    soil_horizon_sand_fractions.values[soilHorizonId])
                xml.etree.ElementTree.SubElement(soil_horizon, "silt").text = str(
                    soil_horizon_silt_fractions.values[soilHorizonId])
        xml.etree.ElementTree.ElementTree(fields).write(output_file, encoding="utf-8", xml_declaration=True)

    def write_field_raster(self, output_file):
        """
        Prepares the field raster.

        Args:
            output_file: The file path of the field raster.

        Returns:
            Nothing.
        """
        applied_fields = self.inputs["Ppm_AppliedFields"].read().values
        field_geometries = self.inputs["Fields_Geometries"].read()
        feature_ids = self.inputs["Fields_Ids"].read()
        extent = self.inputs["Fields_Extent"].read().values
        crs = self.inputs["Fields_Crs"].read()
        in_field_margin = self.inputs["Fields_InFieldMargin"].read().values
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(crs.values)
        applied_fields = set(applied_fields)
        ogr_driver = ogr.GetDriverByName("MEMORY")
        ogr_data_set = ogr_driver.CreateDataSource("memory")
        ogr_layer = ogr_data_set.CreateLayer("filtered", spatial_reference, ogr.wkbPolygon)
        ogr_layer.CreateField(ogr.FieldDefn("Id", ogr.OFTInteger))
        ogr_layer_definition = ogr_layer.GetLayerDefn()
        for i in range(len(feature_ids.values)):
            if feature_ids.values[i] in applied_fields:
                applied_field = ogr.Feature(ogr_layer_definition)
                applied_field.SetGeometry(ogr.CreateGeometryFromWkb(field_geometries.values[i]).Buffer(
                    -in_field_margin))
                applied_field.SetField("Id", feature_ids.values[i])
                ogr_layer.CreateFeature(applied_field)
        raster_cols = int(round(extent[1] - extent[0]))
        raster_rows = int(round(extent[3] - extent[2]))
        raster_driver = gdal.GetDriverByName("GTiff")
        raster_data_set = raster_driver.Create(output_file, raster_cols, raster_rows, 1, 2, ["COMPRESS=LZW"])
        raster_data_set.SetGeoTransform((extent[0], 1, 0, extent[3], 0, -1))
        raster_band = raster_data_set.GetRasterBand(1)
        raster_band.SetNoDataValue(65535)
        raster_data_set.SetProjection(crs.values)
        gdal.RasterizeLayer(raster_data_set, [1], ogr_layer, burn_values=[0], options=["ATTRIBUTE=Id"])
        del raster_data_set

    def write_cropping_statistics(self, output_file):
        """
        Prepares the cropping statistic.

        Args:
            output_file: The file path of the cropping statistic.

        Returns:
            Nothing.
        """
        applied_fields_input = self.inputs["Ppm_AppliedFields"].read().values
        cropping_statistics = xml.etree.ElementTree.Element("CroppingStatistic")
        applied_fields = set(applied_fields_input)
        for appliedField in applied_fields:
            cropping = xml.etree.ElementTree.SubElement(cropping_statistics, "Cropping")
            xml.etree.ElementTree.SubElement(cropping, "Field").text = str(appliedField)
            xml.etree.ElementTree.SubElement(cropping, "DateFrom").text = "1900-01-01"
            xml.etree.ElementTree.SubElement(cropping, "DateTo").text = "1999-12-31"
            xml.etree.ElementTree.SubElement(cropping, "Crop").text = "Cereals,Winter"
        xml.etree.ElementTree.ElementTree(cropping_statistics).write(output_file,
                                                                     encoding="utf-8",
                                                                     xml_declaration=True)

    def write_ppp_repository(self, output_file):
        """
        Prepares the PPP repository.

        Args:
            output_file: The file path of the PPP repository.

        Returns:
            Nothing.
        """
        ppp_repository = xml.etree.ElementTree.Element("PppRepository")
        ppp = xml.etree.ElementTree.SubElement(ppp_repository, "PPP")
        xml.etree.ElementTree.SubElement(ppp, "Name").text = "PPP"
        active_ingredients = xml.etree.ElementTree.SubElement(ppp, "ActiveIngredients")
        active_ingredient = xml.etree.ElementTree.SubElement(active_ingredients, "ActiveIngredient")
        xml.etree.ElementTree.SubElement(active_ingredient, "Name").text = self.inputs["SubstanceName"].read().values
        xml.etree.ElementTree.SubElement(active_ingredient, "MassFraction").text = "1"
        xml.etree.ElementTree.ElementTree(ppp_repository).write(output_file, encoding="utf-8", xml_declaration=True)

    def write_ppm_calendar(self, output_file, applied_areas_path, spatial_ids):
        """
        Prepares the PPM Calendar.

        Args:
            output_file: The file path of the PPM calendar.
            applied_areas_path: The file path to the applied geometries.
            spatial_ids: Spatial identifiers of unique spatial extents of applications.

        Returns:
            Nothing.
        """
        applied_fields = self.inputs["Ppm_AppliedFields"].read().values
        application_dates = self.inputs["Ppm_ApplicationDates"].read().values
        application_rates = self.inputs["Ppm_ApplicationRates"].read().values
        simulation_end = self.inputs["Options_EndDate"].read().values
        ppm_calendar = xml.etree.ElementTree.Element("PpmCalendar")
        for i in range(len(applied_fields)):
            spray_application_element = xml.etree.ElementTree.SubElement(ppm_calendar, "SprayApplication")
            xml.etree.ElementTree.SubElement(spray_application_element, "Date").text = str(
                self.convert_to_przm_date(datetime.date.fromordinal(application_dates[i]), simulation_end))
            xml.etree.ElementTree.SubElement(spray_application_element, "Field").text = str(applied_fields[i])
            xml.etree.ElementTree.SubElement(spray_application_element, "PPP").text = "PPP"
            xml.etree.ElementTree.SubElement(spray_application_element,
                                             "ApplicationRate").text = str(application_rates[i])
            xml.etree.ElementTree.SubElement(spray_application_element, "ApplicationExtent").text = os.path.join(
                applied_areas_path, str(spatial_ids[i]).replace("-", "a") + ".tif")
        xml.etree.ElementTree.ElementTree(ppm_calendar).write(output_file, encoding="utf-8", xml_declaration=True)

    def write_crop_parameters(self, output_file):
        """
        Prepares the crop parameters.

        Args:
            output_file: The file path of the crop parameters.

        Returns:
            Nothing.
        """
        crops = xml.etree.ElementTree.Element("crops")
        pan_evaporation_factors = self.inputs["CropParameters_PanEvaporationFactors"].read().values
        canopy_interceptions = self.inputs["CropParameters_CanopyInterceptions"].read().values
        maximum_coverages = self.inputs["CropParameters_MaximumCoverages"].read().values
        maximum_heights = self.inputs["CropParameters_MaximumHeights"].read().values
        maximum_rooting_depths = self.inputs["CropParameters_MaximumRootingDepths"].read().values
        fallows = self.inputs["CropParameters_Fallows"].read().values
        cropping = self.inputs["CropParameters_Cropping"].read().values
        residues = self.inputs["CropParameters_Residues"].read().values
        emerging_dates = self.inputs["CropParameters_EmergenceDates"].read().values
        maturation_dates = self.inputs["CropParameters_MaturationDates"].read().values
        harvest_dates = self.inputs["CropParameters_HarvestDates"].read().values
        fallow_dates = self.inputs["CropParameters_FallowDates"].read().values
        water_mitigations = self.inputs["CropParameters_WaterMitigations"].read().values
        sediment_mitigations = self.inputs["CropParameters_SedimentMitigations"].read().values
        vfs_mod_lookup_tables = self.inputs["CropParameters_VfsModLookupTables"].read().values
        for i, crop_name in enumerate(self.inputs["CropParameters_Crops"].read().values):
            crop = xml.etree.ElementTree.SubElement(crops, "crop", {"name": crop_name})
            # noinspection SpellCheckingInspection
            xml.etree.ElementTree.SubElement(crop, "pan_evap_factor").text = str(pan_evaporation_factors[i])
            xml.etree.ElementTree.SubElement(crop, "canopy_interception").text = str(canopy_interceptions[i])
            xml.etree.ElementTree.SubElement(crop, "maximum_coverage").text = str(maximum_coverages[i])
            xml.etree.ElementTree.SubElement(crop, "maximum_height").text = str(maximum_heights[i])
            xml.etree.ElementTree.SubElement(crop, "maximum_rooting_depth").text = str(maximum_rooting_depths[i])
            xml.etree.ElementTree.SubElement(crop, "USLEC_fallow").text = str(fallows[i])
            xml.etree.ElementTree.SubElement(crop, "USLEC_cropping").text = str(cropping[i])
            xml.etree.ElementTree.SubElement(crop, "USLEC_residue").text = str(residues[i])
            xml.etree.ElementTree.SubElement(crop, "emergence_date").text = emerging_dates[i]
            xml.etree.ElementTree.SubElement(crop, "maturation_date").text = maturation_dates[i]
            xml.etree.ElementTree.SubElement(crop, "harvest_date").text = harvest_dates[i]
            xml.etree.ElementTree.SubElement(crop, "fallow_date").text = fallow_dates[i]
            xml.etree.ElementTree.SubElement(crop, "water_mitigation").text = str(water_mitigations[i])
            xml.etree.ElementTree.SubElement(crop, "sediment_mitigation").text = str(sediment_mitigations[i])
            xml.etree.ElementTree.SubElement(crop, "VFS_Mod_lookup_table").text = vfs_mod_lookup_tables[i]
        xml.etree.ElementTree.ElementTree(crops).write(output_file, encoding="utf-8", xml_declaration=True)

    def write_applied_area_raster(self, output_path, named_geometries):
        """
        Prepares the applied areas.

        Args:
            output_path: The file path of the applied area raster.
            named_geometries: A dictionary of named geometries to write as raster.

        Returns:
            Nothing.
        """
        os.makedirs(output_path)
        extent = self.inputs["Fields_Extent"].read().values
        crs = self.inputs["Fields_Crs"].read()
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(crs.values)
        ogr_driver = ogr.GetDriverByName("MEMORY")
        raster_cols = int(round(extent[1] - extent[0]))
        raster_rows = int(round(extent[3] - extent[2]))
        raster_driver = gdal.GetDriverByName("GTiff")
        for i, applied_geometry in named_geometries.items():
            ogr_data_set = ogr_driver.CreateDataSource("memory")
            ogr_layer = ogr_data_set.CreateLayer("filtered", spatial_reference, ogr.wkbPolygon)
            ogr_layer_definition = ogr_layer.GetLayerDefn()
            applied_field = ogr.Feature(ogr_layer_definition)
            applied_field.SetGeometry(ogr.CreateGeometryFromWkb(applied_geometry))
            ogr_layer.CreateFeature(applied_field)
            raster_data_set = raster_driver.Create(
                os.path.join(output_path, str(i).replace("-", "a") + ".tif"),
                raster_cols, raster_rows,
                1,
                1,
                ["COMPRESS=LZW"]
            )
            raster_data_set.SetGeoTransform((extent[0], 1, 0, extent[3], 0, -1))
            raster_band = raster_data_set.GetRasterBand(1)
            raster_band.SetNoDataValue(0)
            raster_data_set.SetProjection(crs.values)
            gdal.RasterizeLayer(raster_data_set, [1], ogr_layer, burn_values=[1])
            del raster_data_set

    def collect_spatial_application_info(self):
        """
        Collects information about the spatial extents of applied areas.

        Returns:
            A tuple containing a hash for each base geometry and a dictionary with the geometry per hash.
        """
        applied_geometries = self.inputs["Ppm_AppliedAreas"].read().values
        hashes = [0] * len(applied_geometries)
        unique_geometries = {}
        for i, applied_geometry in enumerate(applied_geometries):
            hash_code = hash(applied_geometry)
            hashes[i] = hash_code
            unique_geometries[hash_code] = applied_geometry
        return hashes, unique_geometries
