'use strict';

// ---------- Filters ----------
function unhtml() {
    return function(html) {
        var content_text = html.replace(/(<([^>]+)>)/ig,"");
        return content_text;
    };
}

function dictlength() {
    return function(dict) {
        return dict?Object.keys(dict).length:null;
    };
}

function range() {
    return function (input, total) {
        total = parseInt(total);

        for (var i = 0; i < total; i++) {
            input.push(i);
        }

        return input;
    };
}

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

function valVariableName() {
    // DOM usage: val-variable-name
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, ngModel) {
            var regex = /^[a-zA-Z_$][a-zA-Z_$0-9]*$/i;

            function validate_variable_name(value){
                if(value != null){
                    var valid = regex.test(value);
                    ngModel.$setValidity('val-variable-name', valid);
                }

                return value;
            }

            ngModel.$parsers.push(validate_variable_name);      // For DOM -> model validation
            ngModel.$formatters.push(validate_variable_name);   // For model -> DOM validation
        }
    };
}

function lowerThan() {
    var link = function ($scope, $element, $attrs, ctrl) {

        var validate = function (viewValue) {
            var comparisonModel = $attrs.lowerThan;

            if (!viewValue || !comparisonModel) {
                // It's valid because we have nothing to compare against
                ctrl.$setValidity('lowerThan', true);
            }else {
                // It's valid if model is lower than the model we're comparing against
                ctrl.$setValidity('lowerThan', parseInt(viewValue, 10) < parseInt(comparisonModel, 10));
            }

            return viewValue;
        };

        ctrl.$parsers.unshift(validate);
        ctrl.$formatters.push(validate);

        $attrs.$observe('lowerThan', function (comparisonModel) {
            // Whenever the comparison model changes we'll re-validate
            return validate(ctrl.$viewValue);
        });

    };

    return {
        require: 'ngModel',
        link: link
    };

}

function greaterThanEq() {
    var link = function ($scope, $element, $attrs, ctrl) {

        var validate = function (viewValue) {
            var comparisonModel = $attrs.greaterThanEq;

            if (!viewValue || !comparisonModel) {
                // It's valid because we have nothing to compare against
                ctrl.$setValidity('greaterThanEq', true);
            }else {
                // It's valid if model is lower than the model we're comparing against
                ctrl.$setValidity('greaterThanEq', parseInt(viewValue, 10) >= parseInt(comparisonModel, 10));
            }

            return viewValue;
        };

        ctrl.$parsers.unshift(validate);
        ctrl.$formatters.push(validate);

        $attrs.$observe('greaterThanEq', function (comparisonModel) {
            // Whenever the comparison model changes we'll re-validate
            return validate(ctrl.$viewValue);
        });

    };

    return {
        require: 'ngModel',
        link: link
    };

}

function tolist() {
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, ngModel) {

            function dom_to_model(value){
                value = value==""?null:value.split(",");
                return value;
            }

            function model_to_dom(value){
                return value;
            }

            ngModel.$parsers.push(dom_to_model);      // For DOM -> model validation
            ngModel.$formatters.push(model_to_dom);   // For model -> DOM validation
        }
    };
}

function autoTypeCast() {
    // Automatically convert type of a string content. If string contains a pure number or decimal,
    // it will be type cased to appropriate type. Any value other than string is bypassed and not
    // checked for casting.
    // Currently only number & decimal are type casted from string.
    // DOM usage: auto-type-cast
    return {
        require: 'ngModel',
        link: function (scope, elem, attr, ngModel) {
            function auto_type_cast(value){
                var new_value = value;
                if(typeof value == "string"){
                    if(!isNaN(value)){
                        // If value is a number or decimal
                        new_value = parseFloat(value);
                    }
                }

                return new_value;
            }

            ngModel.$parsers.push(auto_type_cast);      // For DOM -> model validation
            //ngModel.$formatters.push(auto_type_cast);   // For model -> DOM validation
        }
    };
}

function bootstrapRating($timeout){
    // DOM usage: bootstrap-rating
    return {
        restrict: 'A',
        link: function(scope, element) {
            $timeout(function(){
                element.rating();
            });
        }
    };
}

function select2($timeout){
    // DOM usage: select2
    return {
        restrict: 'A',
        scope: {
            configs: "=select2"
        },
        link: function($scope, element, attrs) {
            var configs = $scope.configs;
            if (configs == null){
                configs = {};
            }

            $timeout(function(){
                element.select2(configs);
            });
        }
    };
}

function scrollToItem() {
    return {
        restrict: 'A',
        scope: {
            speed: "=scrollToItem",
            scrollTo: "@"
        },
        link: function($scope, $elm, attr) {
            $elm.on('click', function() {
                $('html,body').animate({scrollTop: $($scope.scrollTo).offset().top }, $scope.speed);
            });
        }
    };
}

// ---------- /Directives ----------

angular.module('feedvay.common',[])
.run(function($rootScope){
    $rootScope.sentencify = sentencify;
})
.filter('unhtml', unhtml)
.filter('dictlength', dictlength)
.filter('range', range)

.directive("compareTo", compareTo)
.directive('validateFile', validateFile)
.directive('validateHexColor', validateHexColor)
.directive('valVariableName', valVariableName)
.directive('lowerThan', lowerThan)
.directive('greaterThanEq', greaterThanEq)

.directive('tolist', tolist)
.directive('autoTypeCast', autoTypeCast)
.directive('remodelDatetime', remodelDatetime)

.directive('staticInclude', staticInclude)

.directive('fileModel', ['$parse', fileModel])
.directive('previewImage', previewImage)
.directive('bootstrapRating', bootstrapRating)
.directive('select2', select2)
.directive('scrollToItem', scrollToItem)



