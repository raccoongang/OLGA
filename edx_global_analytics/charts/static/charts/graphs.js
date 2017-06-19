/**
 * @overview Makes three chart for instances, courses and students.
 * @module graph_creator/static/graph_creator/graph.js
 */

/**
 * Makes three chart for instances, courses and students based on back-end data as timeline (array of dates)
 * and corresponding counts (array of counts).
 */
(function() {
    var WIDTH_IN_PERCENT_OF_PARENT = 100,
        HEIGHT_IN_PERCENT_OF_PARENT = 60;

    /**
     * Calculates chart`s size by per id.
     * @param {String} id : id-name.
     */
    function calculateChartSize(id) {
        return Plotly.d3.select(id)
        .style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',

            height: HEIGHT_IN_PERCENT_OF_PARENT + 'vh',
            'margin-top': (35 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
        });
    }

    var instances_gd = calculateChartSize('#instances').node(),
        courses_gd = calculateChartSize('#courses').node(),
        students_gd = calculateChartSize('#students').node();

    /**
     * Appends data to chart
     * @param {Object} chart : Plotly object.
     * @param {Array} chart_data : Array of data to corresponding chart.
     * @param {String} chart_title : Char title.
     */
    function appendChartData(chart, chart_data, chart_title) {
        layout = {
          xaxis: {
            title: chart_title
          }
        };

        Plotly.plot(chart, [
          {
            x: timeline,
            y: chart_data,
            type: 'scatter'
          }
        ], layout, {displayModeBar: false});
    }

    appendChartData(instances_gd, instances, 'Active Instances');
    appendChartData(courses_gd, courses, 'Active Courses');
    appendChartData(students_gd, students, 'Active Students');

    window.onresize = function() {
        Plotly.Plots.resize(instances_gd);
        Plotly.Plots.resize(courses_gd);
        Plotly.Plots.resize(students_gd);
    };

}());
