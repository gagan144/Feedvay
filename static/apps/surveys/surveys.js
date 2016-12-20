'use strict';

angular.module('feedvay.surveys', [])

// ---------- Services ----------
.service('ServiceSurveyResponses', function($http){
    this.get = function(survey_uid){
        return $http.get('/console/surveys/api/survey_responses/?format=json', {
            params: {
                survey_uid: survey_uid
            }
        }).then(function (response) {
            return response.data;
        });
    }
})
// ---------- /Services ----------