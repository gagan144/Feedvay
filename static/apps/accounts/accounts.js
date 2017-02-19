'use strict';

angular.module('feedvay.accounts', [] )

// ---------- Services ----------
.service('ServiceAccounts', function($http){
    this.find_user = function(username){
        return $http.get('/accounts/api/get-user-details/', {
            params: {
                username: username
            }
        }).then(function (response) {
            return response.data;
        });
    }
});
// ---------- /Services ----------
