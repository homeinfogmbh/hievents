/*
  hievents.js - HOMEINFO Events API JavaScript library.

  (C) 2017 HOMEINFO - Digitale Informationssysteme GmbH

  This library is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this library.  If not, see <http://www.gnu.org/licenses/>.

  Maintainer: Richard Neumann <r dot neumann at homeinfo period de>

  Requires:
    * jquery.js
*/
"use strict";

var hievents = hievents || {};


hievents.BASE_URL = 'https://backend.homeinfo.de/hievents';


hievents.getUrl = function (endpoint, args) {
  return his.getUrl(hievents.BASE_URL + endpoint, args);
}


hievents.event = hievents.event || {};


hievents.event.getUrl = function (endpoint, args) {
  return hievents.getUrl('/event/' + endpoint, args);
}


hievents.event.list = function (handlers, args) {
  his.query('GET', hievents.event.getUrl('list', args), handlers, args);
}


hievents.event.list = function (handlers, args) {
  his.query('GET', hievents.event.getUrl('list', args), handlers, args);
}
