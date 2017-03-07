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

        return $http.get('/console/storeroom/api/import_records_org/?format=json', {
            params: params
        }).then(function (response) {
            return response.data;
        });
    };

    this.remove_uploads = function(c, list_ids){
        if(!list_ids.length){
            alert("Improper usage.");
            return;
        }

        return $http.post(
            '/console/bsp/bulk-upload/remove/',
            $.param({
                'c': c,
                'list_ids': list_ids
            })
        ).then(function (response) {
            return response.data;
        });
    };
});
// ---------- /Services ----------
