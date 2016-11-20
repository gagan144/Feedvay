'use strict';

// ---------- Directives ----------
function staticInclude($http, $templateCache, $compile) {
    return function (scope, element, attrs) {
        var templatePath = attrs.staticInclude;
        $http.get(templatePath, {cache: $templateCache}).success(function (response) {
            var contents = element.html(response).contents();
            $compile(contents)(scope);
        });
    };
};

function compareTo() {
    return {
        require: "ngModel",
        scope: {
            otherModelValue: "=compareTo"
        },
        link: function(scope, element, attributes, ngModel) {

            ngModel.$validators.compareTo = function(modelValue) {
                return modelValue == scope.otherModelValue;
            };

            scope.$watch("otherModelValue", function() {
                ngModel.$validate();
            });
        }
    };
}

function remodelDatetime($filter) {
    // DOM usage: remodel-datetime="[date|time|datetime]"
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, ngModel) {
            var TYPE = attr.remodelDatetime;
            var FORMAT = null;
            switch (TYPE){
                case 'date': FORMAT="yyyy-MM-dd"; break;
                case 'time': FORMAT="HH:mm:ss"; break;
                case 'datetime': FORMAT="yyyy-MM-ddTHH:mm:ss"; break;
                default: throw "Invalid remodel-datetime option '" + TYPE +"'.";
            }

            function dom_to_model(value){
                if(value){
                    value = $filter('date')(value, FORMAT);
                }
                return value;
            }

            function model_to_dom(value){
                if(value){
                    var FORMAT_MOMENT = FORMAT.replace('yyyy','YYYY').replace('dd','DD');
                    value = moment(value, FORMAT_MOMENT).toDate();
                }
                return value;
            }

            ngModel.$parsers.push(dom_to_model);      // For DOM -> model validation
            ngModel.$formatters.push(model_to_dom);   // For model -> DOM validation
        }
    };
}

function validateFile() {
    // DOM usage: validate-file
    return {
        require: 'ngModel',
        link: function (scope, el, attrs, ngModel) {
            //change event is fired when file is selected
            el.bind('change', function () {
                scope.$apply(function () {
                    ngModel.$setViewValue(el.val());
                    ngModel.$render();
                })
            })
        }
    }
}

function previewImage() {
    // DOM usage: preview-image
    return {
        require: 'ngModel',
        scope: {
            preview_id: "=previewImage"
        },
        link: function (scope, elem, attrs, ngModel) {
            //change event is fired when file is selected
            elem.bind('change', function () {
                var $img_preview = angular.element("#"+scope.preview_id);

                if (elem[0].files && elem[0].files[0]) {
                    var reader = new FileReader();
                    reader.onload = function (e) {
                        $img_preview.attr('src', e.target.result);
                    }
                    reader.readAsDataURL(elem[0].files[0]);
                }
                else {
                    $img_preview.attr('src', '');
                }


            })
        }
    }
}

function fileModel($parse) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;

            element.bind('change', function(){
                scope.$apply(function(){
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
}


function validateHexColor() {
    // DOM usage: validate-hex-color
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, ngModel) {
            var regex = /^#[0-9A-F]{6}$/i;

            function validate_hex_color(value){
                if(value == null){
                    ngModel.$setValidity('validate-hex-color', true);
                }
                else{
                    var valid = regex.test(value);
                    ngModel.$setValidity('validate-hex-color', valid);
                }
                return value;
            }

            ngModel.$parsers.push(validate_hex_color);      // For DOM -> model validation
            ngModel.$formatters.push(validate_hex_color);   // For model -> DOM validation
        }
    };
}



/* ----- UI Theme ----- */
/**
 * pageTitle - Directive for set Page title - mata title
 */
function pageTitle($rootScope, $timeout) {
    return {
        link: function(scope, element) {
            var listener = function(event, toState, toParams, fromState, fromParams) {
                // Default title
                var title = 'Feedvay Management Console';
                // Create your own title pattern
                if (toState.data && toState.data.pageTitle){
                    title = toState.data.pageTitle;
                }
                $timeout(function() {
                    element.text(title);
                });
            };
            $rootScope.$on('$stateChangeStart', listener);
        }
    }
}

// ---------- /Directives ----------

angular.module('feedvay.common',[])
.directive('staticInclude', staticInclude)
.directive("compareTo", compareTo)
.directive('remodelDatetime', remodelDatetime)
.directive('validateFile', validateFile)
.directive('previewImage', previewImage)
.directive('validateHexColor', validateHexColor)
.directive('fileModel', ['$parse', fileModel])

.directive('pageTitle', pageTitle);

