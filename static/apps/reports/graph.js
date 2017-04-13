'use strict';

angular.module('feedvay.reports.graphs', [
    'angular-flot'
])

// ---------- Services ----------
.service('ServiceGraph', function($http){
    this.get_data = function(org_uid, graph_uid, filters){
        var params = {};
        if(org_uid){
            params['c'] = org_uid;
        }
        for(var key in filters){
            params[key] = filters[key];
        }

        return $http.get('/reports/api/graph_data/' + graph_uid + '/', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
})
// ---------- /Services ----------

// ---------- Directives ----------
.directive('graphDiagram', function(){
    // DOM usage: graph-diagram
    return {
        restrict: 'E',
        //transclude: true,
        //replace: true,
        //templateUrl: '/static/partials/reports/graphs/testing.html',
        templateUrl: function (elem, attrs) {
            return '/static/partials/reports/graphs/' + attrs.type + '.html'
        },
        scope: {
            config: "=config",
            type: "@"
        },
        controller: function ($scope, $rootScope, $element, ServiceGraph) {
            $scope.ST_AJAX = ST_AJAX;
            var ENUMS = {
                DATE_RANGE: {
                    ALL: 'all',
                    TODAY: 'today',
                    SINCE_7_DAYS: 'since7days',
                    SINCE_30_DAYS: 'since30days',
                    SINCE_6_MNTHS: 'since6months',
                    SINCE_YEAR: 'sinceyear'
                }
            };
            $scope.ENUMS = ENUMS;

            // $scope.config already defined
            var org_uid = $scope.config['c'];
            var graph_uid = $scope.config['graph_uid'];

            // --- filters ---
            $scope.filters = {
                daterange: ENUMS.DATE_RANGE.ALL
            };
            $scope.set_filter_daterange = function(key){
                $scope.filters.daterange = key;

                $scope.get_data();
            };
            // --- filters ---

            $scope.flags = {
                status: null,
                error_msg: null
            };
            $scope.flags.status = ST_AJAX.LOADING;

            // --- Graph config & data ---
            $scope.data = null;

            switch($scope.type){
                case '1d_pie': {
                    $scope.configOptions = {
                        series: {
                            pie: {
                                show: true,
                                radius: 1,
                                label: {
                                    show: true,
                                    radius: 2 / 3,
                                    threshold: 0.1,
                                    formatter: function (label, series) {
                                        return '<div style="font-size:11px;text-align:center;color:white;">' + Math.round(series.percent) + '%<br/>(' + series.data[0][1] + ')</div>';
                                    }
                                },
                            }
                        },
                        grid: {
                            hoverable: true
                        },
                        tooltip: true,
                        tooltipOpts: {
                            content: "%s", // show percentages, rounding to 2 decimal places
                            shifts: {
                                x: 20,
                                y: 0
                            },
                            defaultTheme: false
                        }
                    };
                }break;
                case '1d_donut': {
                    $scope.configOptions = {
                        series: {
                            shadowSize: 0,
                            pie: {
                                show: true,
                                radius: 1,
                                innerRadius: 0.5,

                                label: {
                                    show: true,
                                    radius: 3 / 4,
                                    background: {opacity: 0},

                                    formatter: function (label, series) {
                                        return '<div style="font-size:11px;text-align:center;color:white;">' + Math.round(series.percent) + '%<br/>(' + series.data[0][1] + ')</div>';
                                    },
                                },

                            }
                        },
                        grid: {
                            hoverable: true
                        },
                        tooltip: true,
                        tooltipOpts: {
                            content: "%s", // show percentages, rounding to 2 decimal places
                            shifts: {
                                x: 20,
                                y: 0
                            },
                            defaultTheme: false
                        }
                    };
                }break;
            }

            // --- Graph config & data ---


            $scope.get_data = function(){
                $scope.flags.status = ST_AJAX.LOADING;

                // --- Set filters ---
                var final_filters = angular.copy($scope.filters);

                // Date-range
                switch(final_filters.daterange){
                    case ENUMS.DATE_RANGE.ALL: {}break;
                    case ENUMS.DATE_RANGE.TODAY: {
                        final_filters['start_date'] = moment().format('YYYY-MM-DD');
                        final_filters['end_date'] = moment().format('YYYY-MM-DD');
                    }break;
                    case ENUMS.DATE_RANGE.SINCE_7_DAYS: {
                        final_filters['start_date'] = moment().add('days', -7).format('YYYY-MM-DD');
                        final_filters['end_date'] = moment().format('YYYY-MM-DD');
                    }break;
                    case ENUMS.DATE_RANGE.SINCE_30_DAYS: {
                        final_filters['start_date'] = moment().add('days', -30).format('YYYY-MM-DD');
                        final_filters['end_date'] = moment().format('YYYY-MM-DD');
                    }break;
                    case ENUMS.DATE_RANGE.SINCE_6_MNTHS: {
                        final_filters['start_date'] = moment().add('months', -6).format('YYYY-MM-DD');
                        final_filters['end_date'] = moment().format('YYYY-MM-DD');
                    }break;
                    case ENUMS.DATE_RANGE.SINCE_YEAR: {
                        final_filters['start_date'] = moment().add('years', -1).format('YYYY-MM-DD');
                        final_filters['end_date'] = moment().format('YYYY-MM-DD');
                    }break;
                }
                delete final_filters['daterange'];
                // --- /Set filters ---

                ServiceGraph.get_data(org_uid, graph_uid, final_filters).then(
                    function(response_data){
                        $scope.flags.status = ST_AJAX.COMPLETED;

                        var final_data = null;
                        switch($scope.type){
                            case '1d_pie':{
                                final_data = [];
                                angular.forEach(response_data.data, function(row, key){
                                    final_data.push({
                                        "label": row["_id"]["answer"],
                                        "data": row["count"]
                                    })
                                });

                            }break;
                            default: {
                                final_data = response_data.data;
                            }
                        }

                        $scope.data = final_data;
                    },
                    function(response_data){

                    }

                );
            };
            $scope.get_data();

        }
    }

});
// ---------- /Directives ----------
