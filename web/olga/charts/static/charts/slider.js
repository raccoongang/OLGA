var handle;
var loop_slider_timeout = null;

$(document).ready(function() {
    handle = $("#custom-handle");

    $( "#slider" ).slider({
        value: months_keys_sorted.length - 1,
        min: 0,
        max: months_keys_sorted.length - 1,
        step: 1,
        slide: function(event, ui) {
            update_selected_date(ui.value);
        },
        create: function() {
            update_selected_date($(this).slider("value"));
        }
    });
    $('#custom-handle').focus();

    $('#play_retrospective').on('click', function() {
        if (loop_slider_timeout) {
            loop_slider_timeout = clearTimeout(loop_slider_timeout);
            $(this).addClass('btn-default');
            $(this).removeClass('btn-success');
        } else {
            loop_slider_timeout = setTimeout(loop_slider, 1000);
            $(this).addClass('btn-success');
            $(this).removeClass('btn-default');
        }

        return false;
    });

    prepare_months_table();
    select_month(months_keys_sorted[months_keys_sorted.length - 1]);
});

function make_tr_from_tabular_countries(month_key, countries) {
    countries_trs = '';

    for (var country_key in countries) {
        country = countries[country_key];
        countries_trs += `
            <tr role="row" class="odd ${country[0] == "Country is not specified" ? "unspecified-country" : ""}">
            <td role="gridcell">${country[0]}</td>
            <td class="text-right" role="gridcell">${country[1][1]}</td>
                <td class="text-right sorting_1" role="gridcell">${country[1][0]}</td>
            </tr>
        `;
    }

    return `<tbody id="tbody_${month_key}" style="display: none">${countries_trs}</tbody>`;
}

function select_month(month_key) {
    var month = months[month_key]
    // Update top_country
    $('#top_country').html(month.top_country);

    // Update countries_amount
    $('#countries_amount').html(month.countries_amount);

    // Update countries_table
    $('#DataTables_Table_0 tbody').hide();
    $('#tbody_' + month_key).show();

    // Update map
    datamap.updateChoropleth(compose_dataset(month.datamap_countries_list));
}

function prepare_months_table() {
    var country_table = $('#DataTables_Table_0');

    for (var month_key in months) {
        country_table.append(
            make_tr_from_tabular_countries(month_key, months[month_key].tabular_countries_list)
        )
    }
}

function update_selected_date(value) {
    handle.text(months[months_keys_sorted[value]]['label']);
    select_month(months_keys_sorted[value]);
}

function loop_slider() {
    var slider = $('#slider');
    if (slider.slider('value') == slider.slider('option').max) {
        slider.slider('value', slider.slider('option').min);
    } else {
        slider.slider('value', slider.slider('value') + 1);
    }

    update_selected_date(slider.slider('value'));
    loop_slider_timeout = setTimeout(loop_slider, 1000);
}
