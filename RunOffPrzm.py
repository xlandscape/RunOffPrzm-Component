"""
Class definition for the RunOffPrzm component.
"""
from osgeo import gdal, ogr, osr
import datetime
import glob
import numpy as np
import os
import shutil
import attrib
import base
import xml.etree.ElementTree


class RunOffPrzm(base.Component):
    """
    Encapsulates the RunOffPRZM module in a Landscape Model component.
    """
    # RELEASES
    VERSION = base.VersionCollection(
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
    VERSION.fixed("1.3.33", "components.RunOffPrzm parameterization adapted to newest version (spelling error)")
    VERSION.fixed("1.3.35", "components.RunOffPrzm module updated to PRZM Runoff v1.44")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.changed("2.0.1", "Module updated to PRZM Runoff v1.45")
    VERSION.changed("2.0.2", "Updated data type access")
    VERSION.changed("2.0.3", "Crop parameterization added to component configuration")

    def __init__(self, name, observer, store):
        super(RunOffPrzm, self).__init__(name, observer, store)
        self._module = base.Module("PRZM_Runoff", "1.45")
        self._inputs = base.InputContainer(self, [
            base.Input(
                "ProcessingPath",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Model_AdsorptionMethod",
                (
                    attrib.Class(str),
                    attrib.Scales("global"),
                    attrib.Unit(None),
                    attrib.InList(("linear", "Freundlich", "aged"))
                ),
                self.default_observer
            ),
            base.Input(
                "Model_SoilTemperatureSimulation",
                (attrib.Class(int), attrib.Scales("global"), attrib.Unit(None), attrib.InList((0, 1, 2))),
                self.default_observer
            ),
            base.Input(
                "SubstanceName",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Substance_PlantUptakeFactor",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1")),
                self.default_observer
            ),
            base.Input(
                "Substance_PesticideDissipationRateOfFoliage",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "Substance_FoliarWashOffCoefficient",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "Substance_HenryConstant",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "Substance_VapourPressure",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("mPa")),
                self.default_observer
            ),
            base.Input(
                "Substance_MolecularWeight",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("g/mol")),
                self.default_observer
            ),
            base.Input(
                "Substance_WaterSolubility",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("mg/L")),
                self.default_observer
            ),
            base.Input(
                "Substance_TemperatureAtWhichMeasured",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("K")),
                self.default_observer
            ),
            base.Input(
                "Substance_FreundlichExponent",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("1")),
                self.default_observer
            ),
            base.Input(
                "Substance_ReferenceMoistureForDT50Soil",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("%")),
                self.default_observer
            ),
            base.Input(
                "Substance_SoilDT50",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("d")),
                self.default_observer
            ),
            base.Input(
                "Substance_KocSoil",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "SprayApplication_PrzmApplicationMethod",
                (attrib.Class(str), attrib.Scales("global"), attrib.InList(("soil", "canopy", "foliar"))),
                self.default_observer
            ),
            base.Input(
                "SprayApplication_IncorporationDepth",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("cm")),
                self.default_observer
            ),
            base.Input(
                "Options_StartDate",
                (attrib.Class(datetime.date, 1), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_EndDate",
                (attrib.Class(datetime.date, 1), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_TemporaryOutputPath",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_DeleteTemporaryGrids",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_TimeoutSecPrzm",
                (attrib.Class(int), attrib.Scales("global"), attrib.Unit("s")),
                self.default_observer
            ),
            base.Input(
                "Options_ReportingThreshold",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "Options_DeleteAllInterimResults",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Weather_Precipitation",
                (attrib.Transformable(1), attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("mm/d")),
                self.default_observer
            ),
            base.Input(
                "Weather_ET0",
                (attrib.Transformable(1), attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("mm/d")),
                self.default_observer
            ),
            base.Input(
                "Weather_Temperature",
                (attrib.Transformable(1), attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("°C")),
                self.default_observer
            ),
            base.Input(
                "Weather_WindSpeed",
                (attrib.Transformable(1), attrib.Class(np.ndarray), attrib.Scales("time/day"), attrib.Unit("m/s")),
                self.default_observer
            ),
            base.Input(
                "Weather_SolarRadiation",
                (
                    attrib.Transformable(1),
                    attrib.Class(np.ndarray),
                    attrib.Scales("time/day"),
                    attrib.Unit("kJ/(m²*d)")
                ),
                self.default_observer
            ),
            base.Input(
                "Fields_Slope",
                (attrib.Class(float), attrib.Scales("global")),
                self.default_observer
            ),
            base.Input(
                "Fields_SoilHorizonThicknesses",
                (attrib.Class("list[float]", 1), attrib.Scales("other/soil_horizon")),
                self.default_observer
            ),
            base.Input(
                "Fields_SoilHorizonBulkDensities",
                (attrib.Class("list[float]", 1), attrib.Scales("other/soil_horizon")),
                self.default_observer
            ),
            base.Input(
                "Fields_SoilHorizonOrganicMaterialContents",
                (attrib.Class("list[float]", 1), attrib.Scales("other/soil_horizon")),
                self.default_observer
            ),
            base.Input(
                "Fields_SoilHorizonSandFractions",
                (attrib.Class("list[float]", 1), attrib.Scales("other/soil_horizon")),
                self.default_observer
            ),
            base.Input(
                "Fields_SoilHorizonSiltFractions",
                (attrib.Class("list[float]", 1), attrib.Scales("other/soil_horizon")),
                self.default_observer
            ),
            base.Input(
                "Fields_Geometries",
                (attrib.Class("list[bytes]"), attrib.Scales("space/base_geometry"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Fields_Ids",
                (attrib.Class("list[int]"), attrib.Scales("space/base_geometry"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Fields_Crs",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Fields_Extent",
                (attrib.Class("tuple[float]"), attrib.Scales("space/extent"), attrib.Unit("metre")),
                self.default_observer
            ),
            base.Input(
                "Fields_FlowGrid",
                (attrib.Class(str), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Fields_InFieldMargin",
                (attrib.Class(float), attrib.Scales("global"), attrib.Unit("m")),
                self.default_observer
            ),
            base.Input(
                "Ppm_AppliedFields",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Ppm_ApplicationDates",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Ppm_ApplicationRates",
                (attrib.Class(np.ndarray), attrib.Scales("other/application"), attrib.Unit("g/ha")),
                self.default_observer
            ),
            base.Input(
                "Ppm_AppliedAreas",
                (attrib.Class("list[bytes]"), attrib.Scales("other/application"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_ShowExtendedErrorInformation",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_MethodOfRunoffGeneration",
                (attrib.Class(int), attrib.Scales("global"), attrib.Unit(None), attrib.Equals(1)),
                self.default_observer
            ),
            base.Input(
                "Options_UsePreSimulatedPrzmResults",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_UseOnePrzmModelPerGridCell",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "Options_UseVfsMod",
                (attrib.Class(bool), attrib.Scales("global"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_Crops",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_PanEvaporationFactors",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_CanopyInterceptions",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_MaximumCoverages",
                (attrib.Class("list[int]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_MaximumHeights",
                (attrib.Class("list[int]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_MaximumRootingDepths",
                (attrib.Class("list[int]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_Fallows",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_Cropping",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_Residues",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_EmergenceDates",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_MaturationDates",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_HarvestDates",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_FallowDates",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            ),
            base.Input(
                "CropParameters_WaterMitigations",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_SedimentMitigations",
                (attrib.Class("list[float]"), attrib.Scales("other/crop")),
                self.default_observer
            ),
            base.Input(
                "CropParameters_VfsModLookupTables",
                (attrib.Class("list[str]"), attrib.Scales("other/crop"), attrib.Unit(None)),
                self.default_observer
            )
        ])
        self._outputs = base.OutputContainer(self, [base.Output("Exposure", store, self)])
        return

    def convert_to_przm_date(self, date, max_date):
        """
        Converts a date to a PRZM date.
        :param date: The actual date.
        :param max_date: The latest date of the simulated date range.
        :return: The date mapped as PRZM date.
        """
        return datetime.datetime(self.convert_to_przm_year(date.year, max_date.year), date.month, date.day).date()

    @staticmethod
    def convert_to_przm_year(year, max_year):
        """
        Converts a year to a PRZM year.
        :param year: The actual year.
        :param max_year: The latest year of the simulated date range.
        :return: The year mapped as PRZM year.
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
        :return: Nothing.
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
        base.run_process((exe, "-ifile", przm_config, przm_folder), None, self.default_observer)
        # noinspection SpellCheckingInspection
        base.run_process((exe2, "-ifile", przm_config, przm_folder), None, self.default_observer)
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
            shape=(simulation_length, raster_cols, raster_rows),
            data_type=np.float32,
            chunks=base.chunk_size((1, None, None), (simulation_length, raster_cols, raster_rows)),
            scales="time/day, space_x/1sqm, space_y/1sqm",
            unit="g/ha"
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
            exposure = np.zeros((1, raster_cols, raster_rows))
            data_slice = (slice(runoff_day, runoff_day + 1), slice(0, raster_cols), slice(0, raster_rows))
            for raster in raster_inputs:
                exposure_raster = gdal.Open(raster, gdal.GA_ReadOnly)
                exposure_raster_band = exposure_raster.GetRasterBand(1)
                exposure_array = exposure_raster_band.ReadAsArray()
                del exposure_raster
                exposure_array = np.flipud(exposure_array).clip(0)
                exposure += np.transpose(exposure_array)
            self.outputs["Exposure"].set_values(exposure, slices=data_slice, create=False, calculate_max=True)
        return

    def write_configuration_xml(self, ppp_repository, cropping_calendar, ppm_calendar, crop_parameterization,
                                field_discrete, field_parameters, flow_grid, przm_weather, output_file):
        """
        Writes the input parameterization for the module.
        :param ppp_repository: The file path of the PPP repository.
        :param cropping_calendar: The file path of the cropping calendar.
        :param ppm_calendar: The file path of the PPM calendar.
        :param crop_parameterization: The file path of the crop parameterization.
        :param field_discrete: The file path of the fields.
        :param field_parameters: The file path of the field parameters.
        :param flow_grid: The file path of the flow grid.
        :param przm_weather: The file path of the weather.
        :param output_file: The file path of the module output.
        :return: Nothing.
        """
        parameters = xml.etree.ElementTree.Element("parameters")
        model = xml.etree.ElementTree.SubElement(parameters, "model")
        xml.etree.ElementTree.SubElement(model, "adsorption_method").text = {
            "linear": "1", "Freundlich": "2", "aged": "3"}[self.inputs["Model_AdsorptionMethod"].read().values]
        xml.etree.ElementTree.SubElement(model, "soil_temperature_simulation").text = str(self.inputs[
            "Model_SoilTemperatureSimulation"].read().values)
        substances = xml.etree.ElementTree.SubElement(parameters, "substances")
        substance = xml.etree.ElementTree.SubElement(
            substances, "substance", {"name": self.inputs["SubstanceName"].read().values})
        xml.etree.ElementTree.SubElement(substance, "plant_uptake_factor").text = str(self.inputs[
            "Substance_PlantUptakeFactor"].read().values)
        xml.etree.ElementTree.SubElement(substance, "pesticide_dissipation_rate_of_foliage").text = str(self.inputs[
            "Substance_PesticideDissipationRateOfFoliage"].read().values)
        xml.etree.ElementTree.SubElement(substance, "foliar_wash_off_coefficient").text = str(self.inputs[
            "Substance_FoliarWashOffCoefficient"].read().values)
        xml.etree.ElementTree.SubElement(substance, "henry_constant").text = str(self.inputs[
            "Substance_HenryConstant"].read().values)
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
        xml.etree.ElementTree.SubElement(options, "method_of_runoff_generation").text = str(self.inputs[
            "Options_MethodOfRunoffGeneration"].read().values)
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
        return

    def write_przm_weather_file(self, output_file):
        """
        Prepares the weather input.
        :param output_file: The file path of the weather input.
        :return: Nothing.
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
                precipitation.values[precipitation.extension.t(date)] / 10,
                et0.values[et0.extension.t(date)] / 10,
                temperature.values[temperature.extension.t(date)],
                wind_speed.values[wind_speed.extension.t(date)] * 100,
                radiation.values[radiation.extension.t(date)] / 41.84))
        weather_file.close()
        return

    def write_field_parameters_file(self, output_file):
        """
        Prepares the field parameters.
        :param output_file: Te file path of the field parameters.
        :return: Nothing.
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
        return

    def write_field_raster(self, output_file):
        """
        Prepares the field raster.
        :param output_file: The file path of the field raster.
        :return: Nothing.
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
        raster_data_set = raster_driver.Create(output_file,
                                               raster_cols,
                                               raster_rows,
                                               1,
                                               gdal.GDT_UInt16,
                                               ["COMPRESS=LZW"])
        raster_data_set.SetGeoTransform((extent[0], 1, 0, extent[3], 0, -1))
        raster_band = raster_data_set.GetRasterBand(1)
        raster_band.SetNoDataValue(65535)
        raster_data_set.SetProjection(crs.values)
        gdal.RasterizeLayer(raster_data_set, [1], ogr_layer, burn_values=[0], options=["ATTRIBUTE=Id"])
        del raster_data_set
        return

    def write_cropping_statistics(self, output_file):
        """
        Prepares the cropping statistic.
        :param output_file: The file path of the cropping statistic.
        :return: Nothing.
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
        return

    def write_ppp_repository(self, output_file):
        """
        Prepares the PPP repository.
        :param output_file: The file path of the PPP repository.
        :return: Nothing.
        """
        ppp_repository = xml.etree.ElementTree.Element("PppRepository")
        ppp = xml.etree.ElementTree.SubElement(ppp_repository, "PPP")
        xml.etree.ElementTree.SubElement(ppp, "Name").text = "PPP"
        active_ingredients = xml.etree.ElementTree.SubElement(ppp, "ActiveIngredients")
        active_ingredient = xml.etree.ElementTree.SubElement(active_ingredients, "ActiveIngredient")
        xml.etree.ElementTree.SubElement(active_ingredient, "Name").text = self.inputs["SubstanceName"].read().values
        xml.etree.ElementTree.SubElement(active_ingredient, "MassFraction").text = "1"
        xml.etree.ElementTree.ElementTree(ppp_repository).write(output_file, encoding="utf-8", xml_declaration=True)
        return

    def write_ppm_calendar(self, output_file, applied_areas_path, spatial_ids):
        """
        Prepares the PPM Calendar.
        :param output_file: The file path of the PPM calendar.
        :param applied_areas_path: The file path to the applied geometries.
        :param spatial_ids: Spatial identifiers of unique spatial extents of applications.
        :return: Nothing.
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
        return

    def write_crop_parameters(self, output_file):
        """
        Prepares the crop parameters.
        :param output_file: The file path of the crop parameters.
        :return: Nothing.
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
        return

    def write_applied_area_raster(self, output_path, named_geometries):
        """
        Prepares the applied areas.
        :param output_path: The file path of the applied area raster.
        :param named_geometries: A dictionary of named geometries to write as raster.
        :return: Nothing.
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
            raster_data_set = raster_driver.Create(os.path.join(output_path, str(i).replace("-", "a") + ".tif"),
                                                   raster_cols, raster_rows,
                                                   1,
                                                   gdal.GDT_Byte,
                                                   ["COMPRESS=LZW"])
            raster_data_set.SetGeoTransform((extent[0], 1, 0, extent[3], 0, -1))
            raster_band = raster_data_set.GetRasterBand(1)
            raster_band.SetNoDataValue(0)
            raster_data_set.SetProjection(crs.values)
            gdal.RasterizeLayer(raster_data_set, [1], ogr_layer, burn_values=[1])
            del raster_data_set
        return

    def collect_spatial_application_info(self):
        """
        Collects information about the spatial extents of applied areas.
        :return: A tuple containing a hash for each base geometry and a dictionary with the geometry per hash.
        """
        applied_geometries = self.inputs["Ppm_AppliedAreas"].read().values
        hashes = [0] * len(applied_geometries)
        unique_geometries = {}
        for i, applied_geometry in enumerate(applied_geometries):
            hash_code = hash(applied_geometry)
            hashes[i] = hash_code
            unique_geometries[hash_code] = applied_geometry
        return hashes, unique_geometries
