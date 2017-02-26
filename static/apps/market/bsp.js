'use strict';

angular.module('feedvay.market.bsp', [] )

// ---------- Services ----------
.service('ServiceBsp', function($http){

    this.get_labels = function(bsp_type, include_common){
        return $http.get('/market/bsp/api/bsp_type_labels/?format=json', {
            params: {
                type: bsp_type,
                include_common: include_common
            }
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------
