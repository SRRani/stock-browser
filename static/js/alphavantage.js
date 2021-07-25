
/*
  This function will render the additional details found
  in the search results
*/
const renderAdditionalDetails = (item) => {
    const { 
        ['1. symbol']: symbol, ['2. name']: name,
        ['3. type']: type, ['4. region']: region,
        ['5. marketOpen']: marketOpen, ['6. marketClose']: marketClose,
        ['7. timezone']: timezone, ['8. currency']: currency,
        ['9. matchScore']: matchScore  } = item; // ES6 Destructuring object and rename
    let row = "<tr>";
    row += `<td>${symbol}</td>`;
    row += `<td>${name}</td>`;
    row += `<td>${type}</td>`;
    row += `<td>${region}</td>`;
    row += `<td>${marketOpen}</td>`;
    row += `<td>${marketClose}</td>`;
    row += `<td>${timezone}</td>`;
    row += `<td>${currency}</td>`;
    row += `<td>${matchScore}</td>`;
    row += "</tr>";
    $('#additionalDetails').append(row);
};

/*
    This function will get the current quote details
*/
const getQuote = (symbol) => {
  $.ajax({
      beforeSend: () => {
          // to show the initial loader
          $('#quote').html('Loading...');
      },
      type: "GET",
      contentType: 'application/json',
      url: `/companies/${symbol}/quote`,
      success: function (data) {
        if(data.quote && Object.keys(data.quote).length) {
            // Rendering the current quote details
            $('#quote').html(`
                <div class="table-responsive">
                <table class="table table-sm table-borderless mb-0">
                <tbody>
                    <tr>
                    <th class="pl-0 w-25" scope="row"><strong>Open</strong></th>
                    <td>${data.quote['02. open']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>High</strong></th>
                    <td>${data.quote['03. high']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>Low</strong></th>
                    <td>${data.quote['04. low']}</td>
                    </tr>
                    <tr>
                    <th class="pl-0 w-25" scope="row"><strong>Price</strong></th>
                    <td>${data.quote['05. price']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>Volume</strong></th>
                    <td>${data.quote['06. volume']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>Latest trading</strong></th>
                    <td>${data.quote['07. latest trading day']}</td>
                    </tr>
                    <tr>
                    <th class="pl-0 w-25" scope="row"><strong>Prev Close</strong></th>
                    <td>${data.quote['08. previous close']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>Change</strong></th>
                    <td>${data.quote['09. change']}</td>
                    <th class="pl-0 w-25" scope="row"><strong>Change %</strong></th>
                    <td>${data.quote['10. change percent']}</td>
                    </tr>
                </tbody>
                </table>
            </div>
            `);
        } else {
            // Displaying the message which is returned by the api server
            $('#quote').text(data.message);
        }
      }
  });
};

/*
    This method will load and render the indicator results
*/
const getIndicatorResults = (symbol, indicator, interval) => {
  $.ajax({
    beforeSend: () => {
      $("#indicatorResults tbody").empty()
    },
    type: "GET",
    contentType: 'application/json',
    url: `/companies/${symbol}/indicators/${indicator}/${interval}`,
    success: function (data) {
      if(data.series.length) {
        let trs = '';
        $.each(data.series, function(ind, s) {
          trs += `<tr><td>${s.date}</td><td>${s[indicator]}</td></tr>`;
        });
        $("#indicatorResults tbody").append(trs);
        $('#indicatorResults').DataTable(); // Creating the paginated bootstrap table using datatable
      } else {
        $('#indicatorResults').DataTable().clear();
        $("#indicatorResults tbody").append(`<tr><td colspan="2">${data.message}</td></tr>`);
      }
    }
});
};

/*
    This method will render the box-plot timeline chart using canvasjs
*/
const plot = function (symbol, type) {
    var dataPoints1 = [], dataPoints2 = [], dataPoints3 = [];
    var stockChart = new CanvasJS.StockChart("chartContainer",{
        theme: "light2",
        exportEnabled: true,
        charts: [{
          toolTip: {
            shared: true
          },
          axisX: {
            lineThickness: 5,
            tickLength: 0,
            labelFormatter: function(e) {
              return "";
            }
          },
          axisY: {
            prefix: "$"
          },
          legend: {
            verticalAlign: "top"
          },
          data: [{
            showInLegend: true,
            name: "Stock Price (in USD)",
            yValueFormatString: "$#,###.##",
            type: "candlestick",
            dataPoints : dataPoints1
          }]
        },{
          height: 100,
          toolTip: {
            shared: true
          },
          axisY: {
            prefix: "$",
            labelFormatter: addSymbols
          },
          legend: {
            verticalAlign: "top"
          },
          data: [{
            showInLegend: true,
            name: "Volume",
            yValueFormatString: "$#,###.##",
            dataPoints : dataPoints2
          }]
        }],
        rangeSelector: {
            enabled: false, // Change it to true to enable Range Selector
        },
        navigator: {
          data: [{
            dataPoints: dataPoints3
          }],
        }
    });
    const url = `companies/${symbol}/${type}`;
    $.getJSON(url, function(data) {
      if(data.series.length) {
        $.each(data.series, function(ind, series) {
            dataPoints1.push({
                x: new Date(series.date), y: [Number(series['1. open']), 
                Number(series['2. high']), Number(series['3. low']), 
                Number(series['4. close'])]
            });
            dataPoints2.push({x: new Date(series.date), y: Number(series['5. volume'])});
            dataPoints3.push({x: new Date(series.date), y: Number(series['4. close'])});
        });
        stockChart.render();
      } else {
          $('#chartContainer').text(data.message);
      }
    });
};

/*
    This utility method will help to format the tooltip of the box-plot
*/
function addSymbols(e){
    var suffixes = ["", "K", "M", "B"];
    var order = Math.max(Math.floor(Math.log(e.value) / Math.log(1000)), 0);
    if(order > suffixes.length - 1)
      order = suffixes.length - 1;
    var suffix = suffixes[order];
    return CanvasJS.formatNumber(e.value / Math.pow(1000, order)) + suffix;
}


$(function () {
    // This will hold the current selected symbol object
    let selected;
    $("#company").autocomplete({
        source: function (request, response) { // This is load the source data for the autocomplete
            $.ajax({
                beforeSend: function() {
                    selected = null;
                    $("#details").slideUp();
                },
                type: "GET",
                contentType: 'application/json',
                url: `/companies/search/?keyword=${request.term}`,
                success: function (data) {
                    response($.map(data, function (item) {
                        return {
                            id: item['1. symbol'],
                            label: item['2. name'],
                            value: item['2. name'],
                            ...item
                        };
                    }));
                }
            });
        },
        minLength: 1, // Min characters requirement for autocomplete trigger
        select: function (event, ui) { // select event for the Autocomplete
            selected = ui.item;
            $("#details").slideDown();
            $("#additionalDetails tbody").empty();
            renderAdditionalDetails(ui.item);
            plot(selected.id, 'daily');
            getQuote(selected.id);
            getIndicatorResults(selected.id, 'SMA', 'weekly')
        }
    });

    // Subscribing to the interval dropdown on change event
    $(document).on('change', '#intervals', function() {
      plot(selected.id, $(this).val());
    });
});