'use strict';

angular.module('feedvay.geography', [] )

// ---------- Services ----------
.service('ServiceGeoLocation', function($http){

    this.search_geolocation = function(text, type, hier_uid, limit){
        if(text==null || text==''){
            return [];
        }

        var params = {
            q: text,
            type: type
        };

        if(hier_uid){
            params['hier'] = hier_uid;
        }
        if(limit){
            params['limit'] = limit;
        }

        return $http.get('/geography/api/search-geolocation/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });

    };

});
// ---------- /Services ----------
