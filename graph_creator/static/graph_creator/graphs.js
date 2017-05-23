(function() {
var d3 = Plotly.d3;

var WIDTH_IN_PERCENT_OF_PARENT = 100,
    HEIGHT_IN_PERCENT_OF_PARENT = 60;

// Instances
var instances_gd3 = d3.select('#instances')
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
        'margin-top': (35 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
    });

var instances_gd = instances_gd3.node();

instances_layout = {
  xaxis: {
    title: 'Active Instances'
  }
};

Plotly.plot(instances_gd, [
  {
    x: timeline,
    y: instances,
    type: 'scatter'
  }
], instances_layout, {displayModeBar: false});

// Courses
var courses_gd3 = d3.select('#courses')
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
        'margin-top': (35 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
    });

var courses_gd = courses_gd3.node();

courses_layout = {
  xaxis: {
    title: 'Active Courses'
  }
};

Plotly.plot(courses_gd, [
  {
    x: timeline,
    y: courses,
    type: 'scatter'
  }
], courses_layout, {displayModeBar: false});

// Students
var students_gd3 = d3.select('#students')
    .style({
        width: WIDTH_IN_PERCENT_OF_PARENT + '%',
        'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

        height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
        'margin-top': (35 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
    });

var students_gd = students_gd3.node();

students_layout = {
  xaxis: {
    title: 'Active Students'
  }
};

Plotly.plot(students_gd, [
  {
    x: timeline,
    y: students,
    type: 'scatter'
  }
], students_layout, {displayModeBar: false});

// Resize
window.onresize = function() {
    Plotly.Plots.resize(instances_gd);
    Plotly.Plots.resize(courses_gd);
    Plotly.Plots.resize(students_gd);
};

})();
