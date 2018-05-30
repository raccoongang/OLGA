/**
 * @overview Makes three chart for instances, courses and students.
 * @module graph_creator/static/graph_creator/graph.js
 */

/**
 * Makes three chart for instances, courses and students based on back-end data as timeline (array of dates)
 * and corresponding counts (array of counts).
 */
(function() {
    students = students.splice(175);
    timeline = timeline.splice(175);
    courses = courses.splice(175);
    instances = instances.splice(175);

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
            title: chart_title,
            xaxis: {
                domain: [0, 0.95]
            },
            yaxis: {
                nticks: 4,
                tickfont: {color: '#70A3FF'},
                showline: true,
            },
            yaxis2: {
                nticks: 3,
                anchor: 'free',
                position: 0.99,
                overlaying: 'y',
                side: 'right',
                tickfont: {color: '#8BB22A'},

            },
            yaxis4: {
                nticks: 5,
                anchor: 'x',
                overlaying: 'y',
                side: 'right',
                tickfont: {color: '#CC4630'},
                showline: true,
            },
            legend: {
                x: 0,
                y: 100,

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
                smoothing: 1.25,
            },
            hovermode:'closest',
            hoverdistance:1000,
            spikedistance:1000,
            type: 'scatter',
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
            type: 'scatter',
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
            type: 'scatter',
        };


        let data = [
            traceInstance,
            traceCourses,
            traceStudents,
        ];

        Plotly.plot(chart, data, layout, {displayModeBar: false});
    }

    function appendSecChart(chart, chart_data, chart_title) {
        let time = Object.keys(newData.monthly);
        let studNum = [];
        let certNum = [];
        let enthNum = [];
        for (let item in newData.monthly) {
            studNum.push(newData.monthly[item][0]);
            certNum.push(newData.monthly[item][1]);
            enthNum.push(newData.monthly[item][2]);
        }

        var trace1 = {
            x: time,
            y: studNum,
            name: 'Registered students',
            type: 'bar'
        };

        var trace2 = {
            x: time,
            y: certNum,
            name: 'Number of certificates',
            type: 'bar'
        };

        var trace3 = {
            x: time,
            y: enthNum,
            name: 'Enthusiastic students',
            type: 'bar'
        };

        var data = [trace1, trace2, trace3];

        var layout = {
            title: chart_title,
            barmode: 'group',
            showlegend: true,
            legend: {
                x: 0,
                y: 100,
            },
        };

        Plotly.newPlot(chart, data, layout, {displayModeBar: false});
    }

    appendChartData(instances_gd, [instances,courses,students], 'Instances, Courses, Students');
    appendSecChart(courses_gd, [], 'Students engagement');
    document.getElementById('js-total-cert').innerHTML = newData.total_generated_certificates;
    document.getElementById('js-total-stud').innerHTML = newData.total_registered_students;

    var debounceWindowResizePlotly = _.debounce(function() {
        window.onresize = function() {
            Plotly.Plots.resize(instances_gd);
            Plotly.Plots.resize(courses_gd);
            Plotly.Plots.resize(students_gd);
        }
    }, 300);

    window.addEventListener('resize', debounceWindowResizePlotly);
}());
