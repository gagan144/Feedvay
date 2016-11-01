'use strict'

angular.module('feedvay.watchdog', ['ui.bootstrap', 'summernote'] )
.run(function($rootScope, $uibModal){
    $rootScope.Mod_watchdog = {


        // ----- Error Reporting -----
        report_problem: function (curr_url) {
            // Opens a form to report a problem.
            var modalInstance = $uibModal.open({
                animation: true,
                templateUrl: '/static/apps/watchdog/templates/report_problem.html',
                controller: 'ReportErrorCtrl',
                //size: 'lg',
                backdrop: 'static',
                // windowClass: "animated fadeIn",
                resolve: {
                    curr_url: function () {
                        return curr_url;
                    }
                }
            });
        }
        // ----- Error Reporting -----

    }
})

// ---------- Services ----------
.service('ReportedProblemService', function($http){
    this.post = function(data){
        return $http.post(
            "/watchdog/report-problem/new/",
            $.param(data)
        ).then(function (response) {
            return response;
        });
    }
})
// ---------- /Services ----------

// ---------- Controllers ----------
.controller('ReportErrorCtrl', function($scope, $uibModalInstance, ReportedProblemService, curr_url){
    // Controller for report problem form
    $scope.data = {
        url: curr_url,
        current_page: 'yes',
        platform: 'portal'
    };

    $scope.summernote_config = {
        height: 150,
        //airMode: true,
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            //['font', ['strikethrough', 'superscript', 'subscript']],
            ['fontsize', ['fontsize']],
            ['color', ['color']],
            ['alignment', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link']],
        ]
    };
    $scope.flags = {
        submitting: false,
        error : false,
        submitted: false
    }

    $scope.save = function (form_obj) {
        if(form_obj.$invalid){
            return false;
        }

        $scope.flags.error = false;
        $scope.flags.submitting = true;

        // Post the form to server
        ReportedProblemService.post(angular.copy($scope.data)).then(
            function successCallback(response) {
                //console.log(response);

                $scope.flags.submitting = false;
                $scope.flags.submitted = true;
                //$uibModalInstance.close();
            },
            function errorCallback(response) {
                console.log(response);

                if(response.status != -1){
                    $scope.flags.submitting = false;
                    $scope.flags.error = true;
                }else{
                    $scope.flags.submitting = false;
                    $.growl.error({
                        title: '<i class="fa fa-signal"></i> Network error!',
                        message: "Please check your internet connection."
                    });
                }
            }
        );


    };

    $scope.close = function () {
        $uibModalInstance.dismiss('cancel');
    };
});
// ---------- /Controllers ----------