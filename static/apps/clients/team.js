'use strict';

angular.module('feedvay.team', [] )

// ---------- Services ----------
.service('ServiceOrgRoles', function($http){
    this.get = function(c){
        return $http.get('/console/team/api/organization_roles/?format=json', {
            params: {
                c: c
            }
        }).then(function (response) {
            return response.data.objects;
        });
    }
})

.service('ServiceOrgTeam', function($http){
    this.get_members = function(c){
        return $http.get('/console/team/api/organization_members/?format=json', {
            params: {
                c: c
            }
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------
