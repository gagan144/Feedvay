'use strict';

angular.module('feedvay.surveys', [])

// ---------- Services ----------
.service('ServiceSurveyResponses', function($http){
    this.get = function(survey_uid, params){
        if(!params){
            params = {};
        }
        return $http.get('/console/surveys/api/survey_responses/?format=json&survey_uid='+survey_uid, {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
})
// ---------- /Services ----------