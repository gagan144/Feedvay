'use strict';

angular.module('feedvay.storeroom', [] )

// ---------- Services ----------
.service('ServiceStoreroom', function($http){
    this.get = function(c, context){
        var params = {
            c: c
        };
        if(context){
            params['context'] = context;
        }

        return $http.get('/console/storeroom/api/data_records_org/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------
