'use strict';

angular.module('feedvay.market.bsp', [] )

// ---------- Services ----------
.service('ServiceBsp', function($http){

    this.get_labels = function(bsp_type, include_common, org_uid){
        // include_common: int 0 or 1

        var params = {
            type: bsp_type,
            include_common: include_common
        };
        if(org_uid!=null) {
            params['c'] = org_uid;
        }

        return $http.get('/market/bsp/api/bsp_type_labels/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------
