/**
 * @overview Creates statistics world map with data per country.
 * @module graph_creator/static/graph_creator/worldmap.js
 */

/**
 * Creates statistics world map with data per country based on back-end data as arrays of country-count accordance.
 * For creation a difference method uses shades of color.
 */
(function () {
    var dataset = {};

    // `countries_list` passed by Django-view. It`s double-array looks like [['FR', 2351], ['GR', 5321]].
    var onlyValues = countries_list.map(function(obj){ return obj[1]; });
    var minValue = Math.min.apply(null, onlyValues),
        maxValue = Math.max.apply(null, onlyValues);

    var paletteScale = d3.scale.linear()
        .domain([minValue,maxValue])
        .range(["#EFEFFF","#02386F"]);

    // Fill dataset in appropriate format.
    countries_list.forEach(function(item){
        var iso = item[0], value = item[1];
        dataset[iso] = { numberOfThings: value, fillColor: paletteScale(value) };
    });

    // Render map.
    var datamap = new Datamap({
        element: document.getElementById('datamap-container'),
        projection: 'mercator', // Big world map.

        // Countries don't listed in dataset will be painted with this color.
        fills: { defaultFill: '#F5F5F5' },
        data: dataset,
        geographyConfig: {
            borderColor: '#DEDEDE',
            highlightBorderWidth: 2,

            // Don't change color on mouse hover.
            highlightFillColor: function(geo) {
                return geo['fillColor'] || '#F5F5F5';
            },

            // Only change border.
            highlightBorderColor: '#B7B7B7',

            // Show desired information in tooltip.
            popupTemplate: function(geo, data) {

                // Don't show tooltip if country don't present in dataset.
                if (!data) { return ; }

                // Tooltip content.
                return ['<div class="hoverinfo">',
                    '<b>', geo.properties.name, '</b>',
                    '<br>Students: <b>', data.numberOfThings, '</b>',
                    '</div>'].join('');
            }
        }
    });

    Datamap();

    /**
     * Scaling map.
     */
    d3.select('svg')
        .style({
            width: $(this).parent().width(),
            height: $(this).parent().height()
        });
}());
