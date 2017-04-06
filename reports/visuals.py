# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from jsonobject import *

class GraphCharts:
    """
    Enum class to define various graphs & charts.

    **Guidelines to add new visual**:

        - Determine dimension (1D, 2D, 3D, nD) and create ENUM accordingly with the prefix.
        - Add to ``choices_all`.
        - Add to ``formfield_choice_mapping`` accordingly.
        - Add graph configuration schema class.
        - Add newly create schema class to ``GRAPH_SCHEMA_MAPPING``.

    **Authors**: Gagandeep Singh
    """
    # --- 1-D Graphs ---
    D1_STATS_NUM = '1d_stats_number'
    D1_HISTOGRAM = '1d_histogram'
    D1_STATS_DT = '1d_stats_datetime'

    D1_PIE = '1d_pie'
    D1_DONUT = '1d_donut'
    D1_GAUGE = '1d_gauge'

    D1_BAR_GRAPH = '1d_bar_graph'

    D1_RATING = '1d_rating'

    # --- 2-D Graphs ---
    D2_LINE_AREA_GRAPH = '2d_line_area_graph'
    D2_SCATTER = '2d_scatter'

    # --- 3-D Graphs ---
    D3_DOT_CLOUD = '3d_dot_cloud'
    D3_WIREFRAME_SURFACE = '3d_wireframe_surface'

    # --- n-D Graphs ---
    DN_POLAR_AREA = 'nd_polar_area'
    DN_RADAR_CHART = 'nd_radar_chart'


    # ----- Choices -----
    choices_all = (
        (D1_STATS_NUM, D1_STATS_NUM),
        (D1_HISTOGRAM, D1_HISTOGRAM),
        (D1_STATS_DT, D1_STATS_DT),
        (D1_PIE, D1_PIE),
        (D1_DONUT, D1_DONUT),
        (D1_GAUGE, D1_GAUGE),
        (D1_BAR_GRAPH, D1_BAR_GRAPH),
        (D1_RATING, D1_RATING),
        (D2_LINE_AREA_GRAPH, D2_LINE_AREA_GRAPH),
        (D2_SCATTER, D2_SCATTER),
        (D3_DOT_CLOUD, D3_DOT_CLOUD),
        (D3_WIREFRAME_SURFACE, D3_WIREFRAME_SURFACE),
        (DN_POLAR_AREA, DN_POLAR_AREA),
        (DN_RADAR_CHART, DN_RADAR_CHART)
    )

    formfield_choice_mapping = {
        "NumberFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_HISTOGRAM, "title": "Histogram" }
        ],
        "DecimalFormField" :[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_HISTOGRAM, "title": "Histogram" }
        ],
        "DateFormField": [
            { "id": D1_STATS_DT, "title": "Statistics" },
        ],
        "TimeFormField": [
            { "id": D1_STATS_DT, "title": "Statistics" },
        ],
        "DateTimeFormField": [
            { "id": D1_STATS_DT, "title": "Statistics" },
        ],
        "BinaryFormField": [
            { "id": D1_PIE, "title": "Pie Chart" },
            { "id": D1_DONUT, "title": "Donut Chart" },
            { "id": D1_GAUGE, "title": "Gauge Chart" },
        ],
        "MCSSFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_PIE, "title": "Pie Chart" },
            { "id": D1_DONUT, "title": "Donut Chart" },
            { "id": D1_GAUGE, "title": "Gauge Chart" },
            { "id": D1_BAR_GRAPH, "title": "Bar Graph" },
        ],
        "MCMSFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_PIE, "title": "Pie Chart" },
            { "id": D1_DONUT, "title": "Donut Chart" },
            { "id": D1_GAUGE, "title": "Gauge Chart" },
            { "id": D1_BAR_GRAPH, "title": "Bar Graph" },
        ],
        "RatingFormField":[
            { "id": D1_RATING, "title": "Rating" },
        ]
    }

    choices_2d = (
        (D2_LINE_AREA_GRAPH, 'Line or Area Graph'),
        (D2_SCATTER, 'Scatter Diagram')
    )

    choices_3d = (
        (D3_DOT_CLOUD, 'Dot Cloud Diagram'),
        (D3_WIREFRAME_SURFACE, 'Wireframe Surface Diagram')
    )

    choices_nd = (
        (DN_POLAR_AREA, 'Polar Area Diagram'),
        (DN_RADAR_CHART, 'Radar Chart'),
    )


class GraphAggregations:
    COUNT = 'count'
    SUM = 'sum'
    MIN = 'min'
    MAX = 'max'
    AVG = 'avg'
    MOV_AVG = 'moving_avg'

    choices_basic = (
        (COUNT, 'Count'),
        (SUM, 'Sum'),
        (MIN, 'Minimum'),
        (MAX, 'Maximum'),
        (AVG, 'Average')
    )

    choices_all = (
        (COUNT, 'Count'),
        (SUM, 'Sum'),
        (MIN, 'Minimum'),
        (MAX, 'Maximum'),
        (AVG, 'Average'),
        (MOV_AVG, 'Moving Average')
    )

# ----- Graph Configuration Schema -----

class StatsNumericGraphSchema(JsonObject):
    """
    Schema for configuration of numeric field statistics. The diagram shows
    basic aggregates such as Count, Max, Min, Avg, Sum across all
    values of a numeric/decimal field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`


class HistogramGraphSchema(JsonObject):
    """
    Schema to configure histogram on a numeric/decimal field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    bin_size    = IntegerProperty(required=True)    # Binning size of the histogram


class StatsDatetimeGraphSchema(JsonObject):
    """
    Schema to configure statistics for date/time/datetime fields. The diagram shows
    basic aggregates such as Count, Max, Min, across all values of a the field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`


class PieGraphSchema(JsonObject):
    """
    Schema to configure pie chart on binary/multiple choice field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class DonutGraphSchema(JsonObject):
    """
    Schema to configure donut chart on binary/multiple choice field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class GaugeGraphSchema(JsonObject):
    """
    Schema to configure gauge chart on binary/multiple choice field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class BarGraphSchema(JsonObject):
    """
    Schema to configure bar graph on binary/multiple choice field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class RatingGraphScema(JsonObject):
    """
    Schema to configure rating metric on rating field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`


class LineAreaGraphSchema(JsonObject):
    """
    Schema to configure line/area graph between two fields.

        - **On X-Axis**: Date/Time/Datetime/Response date
        - **On Y-Axis**: Number/Decimal/Rating/Binary/MultipleChoice field
        - **Aggregation**: Count/Sum/Max/Min/Moving Average
        - **Type**: Line / Area / Bar (Side-by-Side/Stacked)
        - **Multiple Series** allowed.

    **Authors**: Gagandeep Singh
    """

    class Enums:
        RESPONSE_DATE = 'response_date'

        TYPE_LINE = 'line'
        TYPE_AREA = 'area'
        TYPE_BAR = 'bar'
        CH_TYPE = (
            (TYPE_LINE, 'Line Chart'),
            (TYPE_AREA, 'Area Chart'),
            (TYPE_BAR, 'Bar Graph')
        )

        BAR_SIDE_BY_SIDE = 'side_by_side'
        BAR_STACKED = 'stacked'
        CH_BAR_KIND = (
            (BAR_SIDE_BY_SIDE, 'Side-by-Side'),
            (BAR_STACKED, 'Stacked')
        )

    x_axis  = StringProperty(required=True)  # X-Axis Dimension field. This can be response_date as well. Use ``Enums.RESPONSE_DATE``.
    y_axis  = ListProperty(required=True)    # Y-Axis Dimension field(s). This can be multiple. For single, use list with one element only.
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_all, default=GraphAggregations.COUNT)   # Data aggregation
    type    = StringProperty(required=True, choices=Enums.CH_TYPE, default=Enums.TYPE_LINE) # Type of graph
    bar_kind = StringProperty(required=True, choices=Enums.CH_BAR_KIND, default=Enums.BAR_SIDE_BY_SIDE) # Only in case of type `bar`



GRAPH_SCHEMA_MAPPING = {
    GraphCharts.D1_STATS_NUM: StatsNumericGraphSchema,
    GraphCharts.D1_HISTOGRAM: HistogramGraphSchema,
    GraphCharts.D1_STATS_DT: StatsDatetimeGraphSchema,

    GraphCharts.D1_PIE: PieGraphSchema,
    GraphCharts.D1_DONUT: DonutGraphSchema,
    GraphCharts.D1_GAUGE: GaugeGraphSchema,

    GraphCharts.D1_BAR_GRAPH: BarGraphSchema,

    GraphCharts.D1_RATING: RatingGraphScema,


}
# ----- /Graph Configuration Schema -----

