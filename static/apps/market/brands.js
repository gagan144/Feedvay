'use strict'

angular.module('feedvay.market.brands', [] )

// ---------- Services ----------
.service('ServiceBrandExistence', function($http){
    this.find = function(text){
        if(text==null || text==''){
            return [];
        }

        return $http.get('/market/brands/api/search_existence/?format=json', {
            params: {
                q: text
            }
        }).then(function (response) {
            return response.data.objects;
        });
    }
});
// ---------- /Services ----------
