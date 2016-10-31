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

//// ---------- Services ----------
//.service('ServiceTranslations', function($http){
//    this.search = function(text){
//        return $http.get('/languages/api/translation_search/?format=json', {
//            params: {
//                q: text
//            }
//        }).then(function (response) {
//            return response.data.objects;
//            //return response.data.results.map(function(item){
//            //    return item.formatted_address;
//            //  });
//        });
//    }
//})
//// ---------- /Services ----------

// ---------- Controllers ----------
.controller('ReportErrorCtrl', function($scope, $uibModalInstance, curr_url){
    // Controller for report problem form
    $scope.data = {
        url: curr_url,
        current_page: 'yes',
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

    $scope.save = function (form_obj) {
        if(form_obj.$invalid){
            return false;
        }

        alert("save()");

        //$uibModalInstance.close(final_trans);
        $uibModalInstance.close();
    };

    $scope.close = function () {
        $uibModalInstance.dismiss('cancel');
    };
});
// ---------- /Controllers ----------