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
};

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
.directive('pageTitle', pageTitle);