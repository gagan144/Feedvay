'use strict';

angular.module('feedvay.reports.graphs', [])

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
            config: "=config"
        },
        controller: function ($scope, $rootScope, ServiceGraph) {
            $scope.ST_AJAX = ST_AJAX;

            // $scope.config already defined
            var org_uid = $scope.config['c'];
            var graph_uid = $scope.config['graph_uid'];

            $scope.filters = {};

            $scope.flags = {
                status: null,
                error_msg: null
            };
            $scope.flags.status = ST_AJAX.LOADING;

            $scope.data = null;
            $scope.get_data = function(){
                $scope.flags.status = ST_AJAX.LOADING;

                ServiceGraph.get_data(org_uid, graph_uid, $scope.filters).then(
                    function(response_data){
                        $scope.flags.status = ST_AJAX.COMPLETED;
                        $scope.data = response_data.data;
                    },
                    function(response_data){

                    }

                );
            };
            $scope.get_data();






            //console.info("enter directive controller");
            //console.log($scope.config);
            //
            //$scope.set = function(){
            //    $scope.data.name = 'deep';
            //};
            //
            //$scope.data = {
            //    "name": "gagan",
            //    "config": $scope.config
            //};

            //$http({method: 'GET', url: $scope.src}).then(function (result) {
            //    console.log(result);
            //}, function (result) {
            //    alert("Error: No data returned");
            //});
        }
    }

});
// ---------- /Directives ----------
