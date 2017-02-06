'use strict';

angular.module('feedvay.clients', [] )

// ---------- Services ----------
.service('ServiceOrgExistence', function($http){
    this.find = function(text){
        if(text==null || text==''){
            return [];
        }

        return $http.get('/clients/api/search_existence/?format=json', {
            params: {
                q: text
            }
        }).then(function (response) {
            return response.data.objects;
        });
    }
});