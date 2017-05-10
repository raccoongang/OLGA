(function() {
var d3 = Plotly.d3;

var WIDTH_IN_PERCENT_OF_PARENT = 80,
    HEIGHT_IN_PERCENT_OF_PARENT = 46;

var gd3 = d3.select('#instances')
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
        'margin-top': (40 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
    });

var gd = gd3.node();

instances_layout = {
  xaxis: {
    title: 'Instances'
  }
};

Plotly.plot(gd, [
  {
    x: ['2018-05-07 12:16:00', '2018-05-08 12:16:00', '2018-05-09 12:16:00', '2018-05-10 12:16:00', '2018-05-11 12:16:00', '2018-05-12 12:16:00',
        '2018-05-13 12:16:00', '2018-05-14 12:16:00', '2018-05-15 12:16:00', '2018-05-16 12:16:00', '2018-05-17 12:16:00', '2018-05-18 12:16:00',
        '2018-05-18 12:16:00', '2018-05-19 12:16:00', '2018-05-20 12:16:00', '2018-05-21 12:16:00', '2018-05-22 12:16:00', '2018-05-22 12:16:00'
    ],
    y: [500, 389, 890, 654, 499,
        487, 234, 874, 345, 543,
        293, 942, 237, 214, 124],
    type: 'scatter'
  }
], instances_layout, {displayModeBar: false});

window.onresize = function() {
    Plotly.Plots.resize(gd);
};

})();
