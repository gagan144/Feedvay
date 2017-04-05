# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

class VisualReports:
    """
    Enum class to define various visual graphs & charts reports.

    **Guidelines to add new visual**:

        - Determine dimension (1D, 2D, 3D, nD) and create ENUM accordingly with the prefix
        - Add to ``choices_all`
        - Add to ``formfield_choice_mapping`` accordingly

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


