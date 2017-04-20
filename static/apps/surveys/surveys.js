'use strict';

angular.module('feedvay.surveys', [])

// ---------- Services ----------
.service('ServiceSurvey', function($http) {

    this.get = function (org_uid) {
        var params = {};
        if(org_uid){
            params['c'] = org_uid;
        }

        return $http.get('/console/surveys/api/surveys/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    };
})

.service('ServiceSurveyResponses', function($http){
    this.get = function(org_uid, survey_uid, extra_params){
        // param org_uid: (Optional)

        var params = {};
        if(org_uid){ params['c'] = org_uid; }
        if(!extra_params){
            angular.extend(params, extra_params);
        }

        return $http.get('/console/surveys/api/survey_responses/?format=json&survey_uid='+survey_uid, {
            params: params
        }).then(function (response) {
            return response.data;
        });
    };

    this.response_suspicion_remove = function(org_uid, survey_uid, response_uid, reason_id){
        // param org_uid: (Optional)
        var params = {
            'survey_uid': survey_uid,
            'response_uid': response_uid,
            'reason_id': reason_id
        };
        if(org_uid){ params['c'] = org_uid; }

        return $http.post(
            '/console/surveys/response/suspicion/remove/',
            $.param(params)
        ).then(function (response) {
            return response.data;
        });
    };

    this.response_suspicion_add = function(org_uid, survey_uid, response_uid, text){
        // param org_uid: (Optional)
        var params = {
            'survey_uid': survey_uid,
            'response_uid': response_uid,
            'text': text
        };
        if(org_uid){ params['c'] = org_uid; }

        return $http.post(
            '/console/surveys/response/suspicion/add/',
            $.param(params)
        ).then(function (response) {
            return response.data;
        });
    }

})

.service('ServiceSurveyAPI', function($http){
    this.get_response_trend = function(org_uid, survey_uid, extra_params){
        // param org_uid: (Optional)

        var params = {};
        if(org_uid){ params['c'] = org_uid; }
        if(!extra_params){
            angular.extend(params, extra_params);
        }

        return $http.get('/console/surveys/api/survey_response_trend/?format=json&survey_uid='+survey_uid, {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------