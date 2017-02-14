'use strict';

angular.module('feedvay.iam', [] )

// ---------- Services ----------
.service('ServiceOrgRoles', function($http){
    this.get = function(c){
        return $http.get('/console/iam/api/organization_roles/?format=json', {
            params: {
                c: c
            }
        }).then(function (response) {
            return response.data.objects;
        });
    }
});
// ---------- /Services ----------
