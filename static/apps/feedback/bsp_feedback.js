'use strict';

angular.module('feedvay.feedback.bsp', [] )

// ---------- Services ----------
.service('ServiceBspFeedback', function($http){

    this.get_questionnaires = function(org_uid){
        var params = {};
        params['c'] = org_uid;

        return $http.get('/console/feedback/api/bsp_feedback_forms/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    };
});
// ---------- /Services ----------
