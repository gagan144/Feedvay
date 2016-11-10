'use strict';

// ---------- Directives ----------
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
                    title = toState.data.pageTitle + ' - Feedvay';
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
.directive("compareTo", compareTo)
.directive('remodelDatetime', remodelDatetime)

.directive('pageTitle', pageTitle);

