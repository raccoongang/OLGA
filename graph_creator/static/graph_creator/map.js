var mymap = L.map('map', {
    center: [30.0, -0.0],
    zoom: 1
    });

var accessToken = 'pk.eyJ1Ijoidm9sdHUiLCJhIjoiY2owbDM5ejd2MDJvNDMzcDJhdGpqYTFheiJ9.VpK2fUGFV4Vwwg1spz_pIA';

L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v10/tiles/256/{z}/{x}/{y}?access_token=' + accessToken, {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    minZoom: 3,
    id: 'your.mapbox.project.id',
    accessToken: accessToken
}).addTo(mymap);

edxData.forEach(function(data){
    L.marker([data.fields.latitude, data.fields.longitude])
        .bindPopup('<strong>Courses amount: </strong>' + '<strong>' + data.fields.courses_amount + '</strong>' + '<br>' +
            '<strong>Students amount: </strong>' + '<strong>' + data.fields.students_amount + '</strong>')
        .addTo(mymap);
});

