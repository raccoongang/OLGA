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

    var timeline = JSON.parse('["2017-10-15", "2017-10-16", "2017-10-17", "2017-10-18", "2017-10-19", "2017-10-20", "2017-10-21", "2017-10-22", "2017-10-23", "2017-10-24", "2017-10-25", "2017-10-26", "2017-10-27", "2017-10-28", "2017-10-29", "2017-10-30", "2017-10-31", "2017-11-01", "2017-11-02", "2017-11-03", "2017-11-04", "2017-11-05", "2017-11-06", "2017-11-07", "2017-11-08", "2017-11-09", "2017-11-10", "2017-11-11", "2017-11-12", "2017-11-13", "2017-11-14", "2017-11-15", "2017-11-16", "2017-11-17", "2017-11-18", "2017-11-19", "2017-11-20", "2017-11-21", "2017-11-22", "2017-11-23", "2017-11-24", "2017-11-25", "2017-11-26", "2017-11-27", "2017-11-28", "2017-11-29", "2017-11-30", "2017-12-01", "2017-12-02", "2017-12-03", "2017-12-04", "2017-12-05", "2017-12-06", "2017-12-07", "2017-12-08", "2017-12-09", "2017-12-10", "2017-12-11", "2017-12-12", "2017-12-13", "2017-12-14", "2017-12-15", "2017-12-16", "2017-12-17", "2017-12-18", "2017-12-19", "2017-12-20", "2017-12-21", "2017-12-22", "2017-12-23", "2017-12-24", "2017-12-25", "2017-12-26", "2017-12-27", "2017-12-28", "2017-12-29", "2017-12-30", "2017-12-31", "2018-01-01", "2018-01-02", "2018-01-03", "2018-01-04", "2018-01-05", "2018-01-06", "2018-01-07", "2018-01-08", "2018-01-09", "2018-01-10", "2018-01-11", "2018-01-12", "2018-01-13", "2018-01-14", "2018-01-15", "2018-01-16", "2018-01-17", "2018-01-18", "2018-01-19", "2018-01-20", "2018-01-21", "2018-01-22", "2018-01-23", "2018-01-24", "2018-01-25", "2018-01-26", "2018-01-27", "2018-01-28", "2018-01-29", "2018-01-30", "2018-01-31", "2018-02-01", "2018-02-02", "2018-02-03", "2018-02-04", "2018-02-05", "2018-02-06", "2018-02-07", "2018-02-08", "2018-02-09", "2018-02-10", "2018-02-11", "2018-02-12", "2018-02-13", "2018-02-14", "2018-02-15", "2018-02-16", "2018-02-17", "2018-02-18", "2018-02-19", "2018-02-20", "2018-02-21", "2018-02-22", "2018-02-23", "2018-02-24", "2018-02-25", "2018-02-26", "2018-02-27", "2018-02-28", "2018-03-01", "2018-03-02", "2018-03-03", "2018-03-04", "2018-03-05", "2018-03-06", "2018-03-07", "2018-03-08", "2018-03-09", "2018-03-10", "2018-03-11", "2018-03-12", "2018-03-13", "2018-03-14", "2018-03-15", "2018-03-16", "2018-03-17", "2018-03-18", "2018-03-19", "2018-03-20", "2018-03-21", "2018-03-22", "2018-03-23", "2018-03-24", "2018-03-25", "2018-03-26", "2018-03-27", "2018-03-28", "2018-03-29", "2018-03-30", "2018-03-31", "2018-04-01", "2018-04-02", "2018-04-03", "2018-04-04", "2018-04-05", "2018-04-06", "2018-04-07", "2018-04-08", "2018-04-09", "2018-04-10", "2018-04-11", "2018-04-12", "2018-04-13", "2018-04-14", "2018-04-15", "2018-04-16", "2018-04-17", "2018-04-18", "2018-04-19", "2018-04-20", "2018-04-21", "2018-04-22", "2018-04-23", "2018-04-24", "2018-04-25", "2018-04-26"]');
    var students = JSON.parse('[7, 9, 3, 4, 1, 6, 10, 11, 9, 4, 11, 12, 9, 8, 10, 6, 6, 5, 7, 14, 27, 10, 6, 8, 4, 13, 17, 18, 13, 14, 6, 9, 22, 14, 14, 10, 18, 10, 8, 21, 29, 22, 17, 15, 8, 5, 16, 16, 14, 14, 11, 8, 14, 16, 14, 13, 14, 10, 7, 3, 10, 12, 16, 11, 8, 8, 5, 10, 5, 17, 6, 7, 5, 6, 3, 6, 15, 10, 10, 9, 4, 4, 16, 17, 13, 15, 6, 6, 7, 14, 15, 15, 26, 15, 5, 13, 18, 12, 23, 23, 6, 12, 18, 37, 19, 20, 15, 15, 26, 30, 28, 19, 20, 25, 18, 19, 31, 24, 19, 36, 73, 26, 23, 80, 55, 45, 93, 46, 23, 29, 55, 59, 58, 47, 63, 32, 23, 61, 69, 81, 131, 126, 24, 27, 140, 130, 133, 132, 124, 22, 16, 132, 193, 154, 141, 95, 15, 18, 137, 131, 157, 108, 89, 25, 23, 109, 117, 149, 165, 117, 20, 17, 33, 114, 133, 136, 105, 21, 21, 115, 140, 133, 115, 105, 11, 20, 105, 132, 99, 85, 98, 14, 13, 0]');
    var courses = JSON.parse('[482, 482, 482, 482, 482, 482, 482, 483, 484, 484, 484, 485, 485, 485, 486, 487, 487, 487, 487, 487, 490, 491, 491, 491, 491, 492, 492, 493, 493, 494, 494, 494, 494, 496, 496, 497, 494, 494, 494, 495, 495, 496, 496, 497, 497, 497, 498, 498, 498, 498, 498, 499, 499, 499, 499, 499, 499, 500, 500, 500, 500, 500, 502, 502, 503, 503, 503, 503, 503, 504, 504, 504, 504, 504, 504, 504, 504, 504, 504, 504, 504, 504, 506, 512, 556, 566, 566, 566, 566, 566, 566, 566, 566, 566, 566, 567, 567, 567, 676, 676, 653, 653, 653, 654, 654, 654, 654, 654, 654, 575, 575, 575, 531, 556, 497, 497, 447, 447, 449, 1027, 1109, 1109, 1109, 1111, 1117, 1117, 1123, 1124, 1124, 1124, 1126, 1126, 1128, 1129, 1134, 1134, 1134, 1134, 1134, 1135, 1143, 1143, 1143, 1143, 1141, 1142, 1154, 1156, 1157, 1158, 1158, 1158, 1162, 1171, 1187, 1206, 1232, 1233, 1241, 1256, 1256, 1256, 1256, 1256, 1256, 1257, 1257, 1258, 1274, 1275, 1281, 1282, 1282, 1290, 1290, 1294, 1295, 1307, 1307, 1308, 1315, 1315, 1316, 1310, 1310, 1310, 1310, 1311, 1313, 1314, 1316, 1316, 1316, 206]');
    var instances = JSON.parse('[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 6, 8, 8, 8, 8, 8, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 1]');

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
                title: chart_title,

            },
            yaxis: {
                nticks: 4,
                tickfont: {color: '#70A3FF'},
                showline: true
            },
            yaxis2: {
                nticks: 4,
                anchor: 'x',
                overlaying: 'y',
                side: 'right',
                tickfont: {color: '#8BB22A'},
                showline: true
            },
            yaxis4: {
                nticks: 4,
                anchor: 'x',
                overlaying: 'y',
                side: 'right',
                tickfont: {color: '#CC4630'}
            },
            legend: {
                x: 0,
                y: 100
            }
        };
        let traceInstance = {
            x: timeline,
            y: chart_data[0],
            mode: 'lines',
            name: 'Instance',
            line: {
                color: '#70A3FF',
                width: 2.3,
                smoothing: 1.25
            },
            hovermode:'closest',
            hoverdistance:1000,
            spikedistance:1000,
            type: 'scatter'
        };

        let traceCourses = {
            x: timeline,
            y: chart_data[1],
            mode: 'lines',
            name: 'Courses',
            line: {
                shape: 'hv',
                color: '#8BB22A',
            },
            yaxis: 'y2',
            type: 'scatter'
        };

        let traceStudents = {
            x: timeline,
            y: chart_data[2],
            mode: 'lines',
            name: 'Students',
            yaxis: 'y4',
            line: {
                shape: 'hv',
                color: '#CC4630',
            },
            type: 'scatter'
        };


        let data = [
            traceInstance,
            traceCourses,
            traceStudents
        ];

        Plotly.plot(chart, data, layout, {displayModeBar: false});
    }

    appendChartData(instances_gd, [instances,courses,students], 'Active Instances');
    // appendChartData(courses_gd, courses, 'Active Courses');
    // appendChartData(students_gd, students, 'Active Students');

    var debounceWindowResizePlotly = _.debounce(function() {
        window.onresize = function() {
            Plotly.Plots.resize(instances_gd);
            Plotly.Plots.resize(courses_gd);
            Plotly.Plots.resize(students_gd);
        }
    }, 300);

    window.addEventListener('resize', debounceWindowResizePlotly);

}());
