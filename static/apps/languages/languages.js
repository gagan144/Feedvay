'use strict'

angular.module('feedvay.languages', ['ui.bootstrap'] )
.run(function($rootScope, $q, $uibModal){
    $rootScope.ModLanguage = {
        edit_translation: function (old_translation, type, language_codes) {
            // if 'old_translation' is null, it means create new translation
            var translation = angular.copy(old_translation);

            var options = {
                "type": type,
                "languages": language_codes
            };

            var modalInstance = $uibModal.open({
                animation: true,
                templateUrl: '/static/partials/translations/modal_edit_translation.html',
                controller: 'EditTranslationController',
                size: 'lg',
                backdrop: 'static',
                // windowClass: "animated fadeIn",
                resolve: {
                    translation: function () {
                        var trans = angular.copy(translation);
                        return trans;
                    },
                    options: function () {
                        return options;
                    }
                }
            });

            var defer = $q.defer();
            modalInstance.result.then(
                function (trans) {
                    var id = trans["id"];
                    if (id == null) {
                        // New Translation; add new id
                        id = "NEW" + (new Date()).getTime();
                        trans["id"] = id;
                    }

                    // Set list_language_codes
                    if(trans.translations) {
                        trans['list_language_codes'] = Object.keys(trans.translations);
                    }

                    defer.resolve(trans);
                },
                function () {
                    // Modal Closed
                    defer.reject();
                }
            );

            return defer.promise;
        }
    }
})

// ---------- Services ----------
.service('ServiceTranslations', function($http){
    this.search = function(text){
        return $http.get('/languages/api/translation_search/?format=json', {
            params: {
                q: text
            }
        }).then(function (response) {
            return response.data.objects;
            //return response.data.results.map(function(item){
            //    return item.formatted_address;
            //  });
        });
    }
})
// ---------- /Services ----------

// ---------- Controllers ----------
.controller('EditTranslationController', function($scope, $uibModalInstance, ServiceTranslations, translation, options){
    // if 'translation' is null, it means new translation.
    $scope.ServiceTranslations = ServiceTranslations;
    $scope.options = options;
    $scope.translation = translation?translation:{};

    var is_paragraph = null;
    switch (options.type){
        case 'paragraph': is_paragraph = true; break;
        default: {
            is_paragraph = false;

            $scope.$watch('translation.sentence', function (newValue, oldValue) {
                if(typeof newValue == "object"){
                    $scope.translation.sentence = newValue.sentence;

                    // Set translations
                    for(var i in $scope.options.languages){
                        var lang_code = $scope.options.languages[i];
                        var trans_text = newValue.translations[lang_code];

                        if(trans_text){
                            if($scope.translation.translations == null){
                                $scope.translation.translations = {};
                            }
                            $scope.translation.translations[lang_code] = trans_text;
                        }
                    }
                }
            });
        } break;
    }

    $scope.translation.is_paragraph = is_paragraph;

    $scope.save = function (form_obj) {
        if(form_obj.$invalid){
            return false;
        }

        var final_trans = angular.copy($scope.translation);

        // Check for empty translations
        for(var key in  final_trans.translations){
            var val =  final_trans.translations[key];
            if(val==null || val==''){
                delete final_trans.translations[key];
            }
        }

        $uibModalInstance.close(final_trans);
        //$uibModalInstance.close();
    };

    $scope.close = function () {
        $uibModalInstance.dismiss('cancel');
    };
});
// ---------- /Controllers ----------