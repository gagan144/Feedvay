'use strict'

angular.module('feedvay.watchdog', ['ui.bootstrap', 'summernote'] )
.run(function($rootScope, $uibModal){
    $rootScope.Mod_watchdog = {

        // ----- Error Reporting -----
        report_problem: function (curr_url) {
            // Opens a form to report a problem.
            var modalInstance = $uibModal.open({
                animation: true,
                templateUrl: '/static/apps/watchdog/templates/report_problem_form.html',
                controller: 'ReportErrorFormCtrl',
                //size: 'lg',
                backdrop: 'static',
                windowClass: "animated bounceInDown",
                resolve: {
                    curr_url: function () {
                        return curr_url;
                    }
                }
            });
        },
        // ----- Error Reporting -----

        // ----- Suggestion -----
        make_suggestion: function (curr_url) {
            // Opens a form to report a problem.
            var modalInstance = $uibModal.open({
                animation: true,
                templateUrl: '/static/apps/watchdog/templates/suggestion_form.html',
                controller: 'SuggestionFormCtrl',
                //size: 'lg',
                backdrop: 'static',
                windowClass: "animated bounceInDown",
                resolve: {
                    curr_url: function () {
                        return curr_url;
                    }
                }
            });
        }
        // ----- Suggestion -----

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
.service('SuggestionService', function($http){
    this.post = function(data){
        return $http.post(
            "/watchdog/suggestion/new/",
            $.param(data)
        ).then(function (response) {
            return response;
        });
    }
})
// ---------- /Services ----------

// ---------- Controllers ----------
.controller('ReportErrorFormCtrl', function($scope, $uibModalInstance, ReportedProblemService, curr_url){
    // Controller for report problem form
    $scope.data = {
        url: curr_url,
        current_page: 'yes',
        platform: 'portal'
    };

    $scope.summernote_config = {
        height: 150,
        disableResizeEditoroption: true,
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

    $scope.submit = function (form_obj) {
        if(form_obj.$invalid){
            return false;
        }

        $scope.flags.error = false;
        $scope.flags.submitting = true;

        // Post the form to the server
        ReportedProblemService.post(angular.copy($scope.data)).then(
            function successCallback(response) {
                //console.log(response);
                if(response.data.status == 'success'){
                    $scope.flags.submitting = false;
                    $scope.flags.submitted = true;
                }else{
                    $scope.flags.submitting = false;
                    $scope.flags.error = true;
                }
                //$uibModalInstance.close();
            },
            function errorCallback(response) {
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
})

.controller('SuggestionFormCtrl', function($scope, $uibModalInstance, SuggestionService, curr_url){
    // Controller for suggestion form.
    $scope.data = {
        url: curr_url,
        current_page: 'yes',
        platform: 'portal'
    };

    $scope.summernote_config = {
        height: 150,
        disableResizeEditoroption: true,
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

    $scope.submit = function (form_obj) {
        if(form_obj.$invalid){
            return false;
        }

        $scope.flags.error = false;
        $scope.flags.submitting = true;

        // Post the form to the server
        SuggestionService.post(angular.copy($scope.data)).then(
            function successCallback(response) {
                if(response.data.status == 'success'){
                    $scope.flags.submitting = false;
                    $scope.flags.submitted = true;
                }else{
                    $scope.flags.submitting = false;
                    $scope.flags.error = true;
                }
            },
            function errorCallback(response) {
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