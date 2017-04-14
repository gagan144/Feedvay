# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from jsonobject import *
from reports.exceptions import InvalidGraphDefinition

from form_builder.models import FormQuestion

class GraphCharts:
    """
    Enum class to define various graphs & charts.

    **Guidelines to add new visual**:

        - Determine dimension (1D, 2D, 3D, nD) and create ENUM accordingly with the prefix.
        - Add to ``choices_all`.
        - Add to ``formfield_choice_mapping`` accordingly.
        - Add graph definition class by inheriting BaseGraphChart.
        - Add newly created class to ``GRAPH_CLASS_MAPPING``.
        - UI:
            - Add switch case in '/static/apps/reports/graphs.js'.
            - Add partial in '/static/partials/reports/' directory.

    **Authors**: Gagandeep Singh
    """
    # --- 1-D Graphs ---
    D1_STATS_NUM = '1d_stats_number'
    # D1_HISTOGRAM = '1d_histogram'
    D1_STATS_DT = '1d_stats_datetime'

    D1_PIE = '1d_pie'
    D1_DONUT = '1d_donut'

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
        # (D1_HISTOGRAM, D1_HISTOGRAM),
        (D1_STATS_DT, D1_STATS_DT),
        (D1_PIE, D1_PIE),
        (D1_DONUT, D1_DONUT),
        (D1_BAR_GRAPH, D1_BAR_GRAPH),
        (D1_RATING, D1_RATING),
        (D2_LINE_AREA_GRAPH, D2_LINE_AREA_GRAPH),
        (D2_SCATTER, D2_SCATTER),
        (D3_DOT_CLOUD, D3_DOT_CLOUD),
        # (D3_WIREFRAME_SURFACE, D3_WIREFRAME_SURFACE),
        (DN_POLAR_AREA, DN_POLAR_AREA),
        (DN_RADAR_CHART, DN_RADAR_CHART)
    )

    formfield_choice_mapping = {
        "NumberFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            # { "id": D1_HISTOGRAM, "title": "Histogram" }
        ],
        "DecimalFormField" :[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            # { "id": D1_HISTOGRAM, "title": "Histogram" }
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
        ],
        "MCSSFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_PIE, "title": "Pie Chart" },
            { "id": D1_DONUT, "title": "Donut Chart" },
            { "id": D1_BAR_GRAPH, "title": "Bar Graph" },
        ],
        "MCMSFormField":[
            { "id": D1_STATS_NUM, "title": "Statistics" },
            { "id": D1_PIE, "title": "Pie Chart" },
            { "id": D1_DONUT, "title": "Donut Chart" },
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
        # (D3_WIREFRAME_SURFACE, 'Wireframe Surface Diagram')
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

# ----- Graph Definition classes -----
class BaseGraphChart(JsonObject):
    """
    Base graph class. Inherit this class to define new graph definition.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    _cls_base = StringProperty(default='BaseGraphChart', required=True)
    _cls = StringProperty(name='_cls', required=True)   # Name of this class

    def __init__(self, _obj=None, **kwargs):
        # (1) Check '_cls' in _obj or kwargs
        this_class = self.__class__.__name__
        obj_cls = None
        if _obj is not None:
            obj_cls = _obj.get('_cls',None)
        else:
            obj_cls = kwargs.get('_cls',None)

        if obj_cls:
            if obj_cls != this_class:
                raise InvalidGraphDefinition("Graph definition class mismatch. Using class '{}'".format(obj_cls))
        else:
            obj_cls = this_class

        # (2) Update Kwargs
        kwargs.update({
            "_cls": obj_cls
        })
        super(BaseGraphChart, self).__init__(_obj=_obj, **kwargs)

    def get_data(self, entityModel, match_filters, **kwargs):
        """
        Method to get data for the graph as per the configuration. This is an abstract method and every
        class inheriting this must override it.

        :param entityModel: Class of the  actual model from which data has to be extracted.
        :param match_filters: JSON dict for match filter
        :return: JSON data
        """
        raise NotImplementedError("'get_data()' is not implement for this inherited graph class.")


# --- 1D Graph Definitions ---
class StatsNumberGraph(BaseGraphChart):
    """
    Class for define numeric field statistics. The diagram shows
    basic aggregates such as Count, Max, Min, Avg, Sum across all
    values of a numeric/decimal field.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`

    def __init__(self, _obj=None, **kwargs):
        super(StatsNumberGraph, self).__init__(_obj=_obj, **kwargs)

    def get_data(self, entityModel, match_filters, **kwargs):
        """
        Method to get data for this graph on provided ``entityModel``.
        :param entityModel: Class of actual model from which data has to be extracted.
        :param match_filters: JSON dict for match filter
        :return: JSON data:

        **Format**:

            .. code-block:: json

                {
                    "count": 42369,
                    "min": 103,
                    "max": 1698,
                    "sum": 369756,
                    "avg": 561,
                    "std": 126
                }

        **Authors**: Gagandeep Singh
        """
        if not isinstance(match_filters, dict):
            raise ValueError("'match_filters' must be a dictionary.")

        question  = FormQuestion.objects.get(id=self.question_id)
        ques_label = question.label

        final_filters = {
            "list_answers.question_label": ques_label,
            "list_answers.answer": { "$type": "number" }
        }
        final_filters.update(match_filters)

        result_aggr = entityModel._get_collection().aggregate([
            {
                "$unwind":{
                    "path" : "$list_answers",
                    "preserveNullAndEmptyArrays" : False
                }
            },
            {
                "$match": final_filters
            },
            {
                "$group": {
                    "_id": None,
                    "count": { "$sum": 1},
                    "min": { "$min": "$list_answers.answer"},
                    "max": { "$max": "$list_answers.answer"},
                    "sum": { "$sum": "$list_answers.answer"},
                    "avg": { "$avg": "$list_answers.answer"},
                    "std": { "$stdDevSamp": "$list_answers.answer" }
                }
            }
        ])

        try:
            data = list(result_aggr)[0]
            del data["_id"]

            return data
        except IndexError:
            # No data
            return {}


class HistogramGraph(BaseGraphChart):
    """
    Class to define histogram on a numeric/decimal field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    bin_size    = IntegerProperty(required=True)    # Binning size of the histogram


class StatsDatetimeGraph(BaseGraphChart):
    """
    Class to define statistics for date/time/datetime fields. The diagram shows
    basic aggregates such as Count, Max, Min, across all values of a the field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`

    def get_data(self, entityModel, match_filters, **kwargs):
        """
        Method to get data for this graph on provided ``entityModel``.
        :param entityModel: Class of actual model from which data has to be extracted.
        :param match_filters: JSON dict for match filter
        :param use_string: (Optional) If True, fetches dates as string also.
        :return: JSON data:

        **Format**:

            .. code-block:: json

                {
                    "count": 42369,
                    "min": 103,
                    "max": 1698,
                }

        **Authors**: Gagandeep Singh
        """
        if not isinstance(match_filters, dict):
            raise ValueError("'match_filters' must be a dictionary.")

        question  = FormQuestion.objects.get(id=self.question_id)
        ques_label = question.label

        final_filters = {
            "list_answers.question_label": ques_label,
        }

        use_string = kwargs.get('use_string', None)
        if use_string:
            final_filters["$or"] = [
                { "list_answers.answer": { "$type": "date" } },
                { "list_answers.answer": { "$type": "string" } },
            ]
        else:
            final_filters["list_answers.answer"] = { "$type": "date" }


        final_filters.update(match_filters)

        result_aggr = entityModel._get_collection().aggregate([
            {
                "$unwind":{
                    "path" : "$list_answers",
                    "preserveNullAndEmptyArrays" : False
                }
            },
            {
                "$match": final_filters
            },
            {
                "$group": {
                    "_id": None,
                    "count": { "$sum": 1},
                    "min": { "$min": "$list_answers.answer"},
                    "max": { "$max": "$list_answers.answer"},
                }
            }
        ])

        try:
            data = list(result_aggr)[0]
            del data["_id"]

            return data
        except IndexError:
            # No data
            return {}


class PieGraph(BaseGraphChart):
    """
    Class to define pie chart on binary/multiple choice field (string/int).

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation

    def get_data(self, entityModel, match_filters, **kwargs):
        """
        Method to get data for this graph on provided ``entityModel``.
        :param entityModel: Class of actual model from which data has to be extracted.
        :param match_filters: JSON dict for match filter
        :return: JSON data:

        **Format**:

            .. code-block:: json

                [
                    {

                    },
                ]

        **Authors**: Gagandeep Singh
        """
        if not isinstance(match_filters, dict):
            raise ValueError("'match_filters' must be a dictionary.")

        question  = FormQuestion.objects.get(id=self.question_id)
        ques_label = question.label

        final_filters = {
            "list_answers.question_label": ques_label,
            # "list_answers.answer": { "$type": "string" },
            "list_answers.is_other": False
        }
        final_filters.update(match_filters)

        if self.aggregation == GraphAggregations.COUNT:
            exp_aggr = { "$sum": 1}
        elif self.aggregation == GraphAggregations.MIN:
            exp_aggr = { "$min": "$list_answers.answer"}
        elif self.aggregation == GraphAggregations.MAX:
            exp_aggr = { "$max": "$list_answers.answer"}
        elif self.aggregation == GraphAggregations.SUM:
            exp_aggr = { "$sum": "$list_answers.answer"}
        elif self.aggregation == GraphAggregations.AVG:
            exp_aggr = { "$avg": "$list_answers.answer"}
        else:
            raise InvalidGraphDefinition("Invalid aggregation '{}'.".format(self.aggregation))


        result_aggr = entityModel._get_collection().aggregate([
            {
                "$unwind":{
                    "path" : "$list_answers",
                    "preserveNullAndEmptyArrays" : False
                }
            },
            {
                "$match": final_filters
            },
            {
                "$group": {
                    "_id": {
                        "answer": "$list_answers.answer"
                    },
                    "count": exp_aggr,
                }
            }
        ])

        try:
            data = list(result_aggr)

            return data
        except IndexError:
            # No data
            return []


class DonutGraph(PieGraph):
    """
    Class to define donut chart on binary/multiple choice field (string/int).

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class BarGraph(PieGraph):
    """
    Class to define bar graph on binary/multiple choice field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`
    aggregation = StringProperty(required=True, choices=GraphAggregations.choices_basic, default=GraphAggregations.COUNT)   # Data aggregation


class RatingGraph(BaseGraphChart):
    """
    Class to define rating metric on rating field.

    **Authors**: Gagandeep Singh
    """
    question_id = IntegerProperty(required=True)    # Instance ID of :class:`form_builder.models.FormQuestion`

# --- 2D Graph Definitions ---
class LineAreaGraph(BaseGraphChart):
    """
    Class to define line/area graph between two fields.

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


class ScatterGraph(BaseGraphChart):
    """
    Class to define scatter chart between to fields.

    **Authors**: Gagandeep Singh
    """
    x_axis  = StringProperty(required=True) # X-Axis Dimension field
    y_axis  = StringProperty(required=True) # Y-Axis Dimension field


class DotCloudGraph(BaseGraphChart):
    """
    Class to define Dot Cloud graph between 3 fields. All dimensions
    must be number or decimal.

    **Authors**: Gagandeep Singh
    """
    class Enums:
        TYPE_DOT_COLOR = 'dot_color'
        TYPE_DOT_SIZE = 'dot_size'
        CH_TYPE = (
            (TYPE_DOT_COLOR, 'Dot Color'),
            (TYPE_DOT_SIZE, 'Dot Size')
        )

    type    = StringProperty(required=True, choices=Enums.CH_TYPE)  # Type of dot clud graph
    x_axis  = StringProperty(required=True) # X-Axis Dimension field
    y_axis  = StringProperty(required=True) # Y-Axis Dimension field
    z_axis  = StringProperty(required=True) # Z-Axis Dimension field


class PolarAreaGraph(BaseGraphChart):
    """
    Class to define Polar Area graph between multiple fields. This graph
    is applicable on only one response and not between responses.

    **Authors**: Gagandeep Singh
    """
    axis    = ListProperty(required=True)     # List of field dimensions


class RadarGraph(BaseGraphChart):
    """
    Class to define Radar Chart between multiple fields for a single response.

    **Authors**: Gagandeep Singh
    """
    pass


GRAPH_CLASS_MAPPING = {
    # --- 1D Graphs ---
    GraphCharts.D1_STATS_NUM: StatsNumberGraph,
    # GraphCharts.D1_HISTOGRAM: HistogramGraph,
    GraphCharts.D1_STATS_DT: StatsDatetimeGraph,

    GraphCharts.D1_PIE: PieGraph,
    GraphCharts.D1_DONUT: DonutGraph,

    GraphCharts.D1_BAR_GRAPH: BarGraph,

    GraphCharts.D1_RATING: RatingGraph,

    # --- 2D  ---
    GraphCharts.D2_LINE_AREA_GRAPH: LineAreaGraph,
    GraphCharts.D2_SCATTER: ScatterGraph,

    # --- 3D  ---
    GraphCharts.D3_DOT_CLOUD: DotCloudGraph,

    # --- nD  ---
    GraphCharts.DN_POLAR_AREA: PolarAreaGraph,
    GraphCharts.DN_RADAR_CHART: RadarGraph,

}
# ----- /Graph Definition classes -----

