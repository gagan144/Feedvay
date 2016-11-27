'use strict'

angular.module('feedvay.brands', [] )

// ---------- Services ----------
.service('ServiceBrandExistence', function($http){
    this.find = function(text){
        if(text==null || text==''){
            return [];
        }

        return $http.get('/brands/api/search_existence/?format=json', {
            params: {
                q: text
            }
        }).then(function (response) {
            return response.data.objects;
        });
    }
})
.service('ServiceBrandChangeRequests', function($http){
    this.get = function(brand_uid){
        return $http.get('/console/b/'+brand_uid+'/brands/api/brand_change_requests/?format=json')
        .then(function (response) {
            return response.data;
        });
    }
})
.service('ServiceBrandToggleActive', function($http){
    this.post = function(brand_uid, active){
        return $http.post(
            "/console/b/"+brand_uid+"/brands/toggle-active/",
            $.param({"active": active})
        ).then(function (response) {
            return response;
        });
    }
})
// ---------- /Services ----------
