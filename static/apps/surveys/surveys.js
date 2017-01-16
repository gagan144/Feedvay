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

    this.response_suspicion_remove = function(survey_uid, response_uid, reason_id){
        return $http.post(
            '/console/surveys/response/suspicion/remove/',
            $.param({
                'survey_uid': survey_uid,
                'response_uid': response_uid,
                'reason_id': reason_id
            })
        ).then(function (response) {
            return response.data;
        });
    }

    this.response_suspicion_add = function(survey_uid, response_uid, text){
        return $http.post(
            '/console/surveys/response/suspicion/add/',
            $.param({
                'survey_uid': survey_uid,
                'response_uid': response_uid,
                'text': text
            })
        ).then(function (response) {
            return response.data;
        });
    }

})

.service('ServiceSurveyAPI', function($http){
    this.get_response_trend = function(survey_uid, params){
        if(!params){
            params = {};
        }
        return $http.get('/console/surveys/api/survey_response_trend/?format=json&survey_uid='+survey_uid, {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
})
// ---------- /Services ----------