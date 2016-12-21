angular.module('angular-jqgrid', ['ng']).directive('ngJqgrid', function ($window) {
    return {
        restrict: 'E',
        replace: true,
        scope: {
            config: '=',
            modeldata: '=',
            insert: '=?',
            api: '=?',
            addnew:"=",
            filtertoolbar: '='
        },
        link: function (scope, element, attrs) {
            var table, div;
            scope.$watch('config', function (value) {
                element.children().empty();
                table = angular.element('<table id="' + attrs.gridid + '"></table>');
                element.append(table);
                if (attrs.pagerid) {
                    value.pager = '#' + attrs.pagerid;
                    var pager = angular.element(value.pager);
                    if (pager.length == 0) {
                        div = angular.element('<div id="' + attrs.pagerid + '"></div>');
                        element.append(div);
                    }
                }
                table.jqGrid(value);

                table.jqGrid("inlineNav", '#'+attrs.pagerid, { addParams: { position: "last" } });
                $("#"+attrs.pagerid+" option[value='100000']").text('All');
                table.jqGrid('navGrid', '#'+attrs.pagerid, { edit: false, add: false, del: false });

                if(scope.filtertoolbar) {
                    table.jqGrid('filterToolbar', scope.filtertoolbar);
                }

                // Variadic API – usage:
                //   view:  <ng-jqgrid … vapi="apicall">
                //   ctrl:  $scope.apicall('method', 'arg1', …);
                scope.vapi = function () {
                    var args = Array.prototype.slice.call(arguments, 0);
                    return table.jqGrid.apply(table, args);
                };
                // allow to insert(), clear(), refresh() the grid from 
                // outside (e.g. from a controller). Usage:
                //   view:  <ng-jqgrid … api="gridapi">
                //   ctrl:  $scope.gridapi.clear();
                scope.api = {
                    insert: function (rows) {
                        if (rows) {
                            for (var i = 0; i < rows.length; i++) {
                                scope.modeldata.push(rows[i]);
                            }
                            table.jqGrid('setGridParam', { data: scope.modeldata })
                                 .trigger('reloadGrid');
                        }
                    },
                    clear: function () {
                        scope.modeldata.length = 0;
                        table.jqGrid('clearGridData', { data: scope.modeldata })
                            .trigger('reloadGrid');
                    },
                    refresh: function () {
                        table
                            .jqGrid('clearGridData')
                            .jqGrid('setGridParam', { data: scope.modeldata })
                            .trigger('reloadGrid');
                    }
                };
            });
            scope.$watch('data', function (value) {
                table.jqGrid('setGridParam', { data: value })
                     .trigger('reloadGrid')
                ;
            });
        }
    };
})
