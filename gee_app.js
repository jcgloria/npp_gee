// Create map object
var Map = ui.Map();
var imageList = ee.data.listAssets('projects/ee-96juancg/assets').assets.map(function (asset) {
    return ee.Image(asset.id)
});
var imgCollection = ee.ImageCollection.fromImages(imageList)
var currentYear = null

// For the legend
function createLegend(vizParams) {
    var lon = ee.Image.pixelLonLat().select('longitude');
    var gradient = lon.multiply((vizParams.max - vizParams.min) / 100.0).add(vizParams.min);
    var legendImage = gradient.visualize(vizParams);

    var thumb = ui.Thumbnail({
        image: legendImage,
        params: { bbox: '0,0,100,8', dimensions: '100%' },  // Adjust dimensions to 100% width
        style: { stretch: 'horizontal', margin: '0px 8px', maxHeight: '24px' }
    });

    var legendPanel = ui.Panel({
        widgets: [
            ui.Label(vizParams.min + ' gC/m^2', { margin: '4px 8px' }),
            thumb,
            ui.Label(vizParams.max + ' gC/m^2', { margin: '4px 8px' }),
        ],
        layout: ui.Panel.Layout.flow('horizontal'),
        style: { stretch: 'horizontal' }
    });

    return legendPanel;
}
// Color pallet
var vizParams = {
    min: 0,
    max: 90,
    palette: ['gray', 'yellow', 'orange', 'lime', 'green', 'DarkGreen']
};

// Color pallet UI components
var legendLabel = ui.Label({
    value: 'Legend',
    style: { fontWeight: 'bold', fontSize: '14px' }
});
var legend = createLegend(vizParams);

// Chart components
var chartPanel = ui.Panel({ layout: ui.Panel.Layout.flow('vertical') });
var chartLabel = ui.Label({ value: "", style: { fontSize: "1.5em", textAlign: "center", stretch: "horizontal" } })

// Create the main panel with vertical flow layout.
var panel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: { width: '350px' }
});

// UCL title
panel.add(ui.Label({
    value: "UCL",
    style: { fontSize: "5em", textAlign: "center", stretch: "horizontal", fontWeight: "bold" }
}))

// MSc description
panel.add(ui.Label({
    value: "MSc Emerging Digital Technologies",
    style: { textAlign: "center", stretch: "horizontal", fontSize: "1.5em" }
}));

// The four areas of study
var locations = {
    Sundarbans: [89.1833, 21.9497],
    Everglades: [-80.8987, 25.2867],
    Cairns: [145.8481, -16.9386],
    Can_Gio: [106.8672, 10.4807]
};

// Subtitle
var title = ui.Label({
    value: 'Net Primary Productivity',
    style: { textAlign: "center", stretch: "horizontal", fontSize: "1.2em" }
});

// Description
panel.add(title)
var description = ui.Label("Visualize the NPP of various locations month by month.");
panel.add(description)


// Select Location Widget
var locationSelect = ui.Select({
    items: Object.keys(locations),
    style: { stretch: "horizontal" },
    onChange: function (key) {
        Map.setCenter(locations[key][0], locations[key][1], 9);
    }
});
locationSelect.setPlaceholder('Choose a location...');
panel.add(locationSelect);

// Horizontal panel for date filter
var dateFilterPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('horizontal'),
    style: { width: '350px', backgroundColor: "LightGray" }
});

var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
var years = ["2014", "2015", "2016", "2017", "2018", "2019"]

// Date filter widgets
var monthSelect = ui.Select({ items: months, placeholder: "Month", style: { stretch: 'horizontal' } })
var yearSelect = ui.Select({ items: years, placeholder: "Year", style: { stretch: 'horizontal' } })
dateFilterPanel.add(monthSelect)
dateFilterPanel.add(yearSelect)

//spacer
var spacer = ui.Label('', { stretch: 'horizontal' });
dateFilterPanel.add(spacer);

// Error label for date filter
var errorLabel = ui.Label({ style: { shown: false, color: "red" } });

// Event handler for date filter
function dateFilterOnClick() {
    errorLabel.style().set({ shown: false })
    if (locationSelect.getValue() === null || monthSelect.getValue() === null || yearSelect.getValue() === null) {
        errorLabel.setValue('Please define all filters');
        errorLabel.style().set({ shown: true });
        return;
    }
    if (currentYear != yearSelect.getValue()) {
        genChart()
        currentYear = yearSelect.getValue()
    }
    var filename = "npp_" + locationSelect.getValue() + "_" + (yearSelect.getValue()) + "_" + String(months.indexOf(monthSelect.getValue()) + 1);
    var img = ee.Image("projects/ee-96juancg/assets/" + filename).clip(ee.Geometry.Point(locations[locationSelect.getValue()][0], locations[locationSelect.getValue()][1]).buffer(10000))

    Map.clear()
    Map.addLayer(img.visualize(vizParams), {}, 'NPP');
    chartLabel.setValue("Mean NPP during " + currentYear + ' (gC/m2)') // Update chart label
}

// Create a styled panel for the button
var buttonPanel = ui.Panel({
    style: {
        backgroundColor: 'red',
        padding: '0px'
    }
});

dateFilterPanel.add(ui.Button({
    label: "Load",
    style: { textAlign: "right", fontWeight: "bold" },
    onClick: dateFilterOnClick,
}));


//Chart
function genChart() {
    var geo = ee.Geometry.Point(locations[locationSelect.getValue()][0], locations[locationSelect.getValue()][1])
    var vals = imgCollection.filterDate(ee.Date(yearSelect.getValue() + '-01-01'), ee.Date(yearSelect.getValue() + '-12-31')).filterBounds(geo).aggregate_array('mean_NPP').getInfo()
    var colsData = [{ id: "month", label: 'Month', type: 'string' },
    { id: "npp", label: 'NPP', type: 'number' }]
    var rowsData = []
    for (var i = 0; i < months.length; i++) {
        rowsData.push({ c: [{ v: months[i] }, { v: vals[i] }] });
    }
    var tableData = { cols: colsData, rows: rowsData };

    var chart = ui.Chart({ dataTable: tableData, chartType: "ColumnChart" })

    chartPanel.clear()
    chartPanel.add(chartLabel)
    chartPanel.add(chart)
}


panel.add(dateFilterPanel)
panel.add(errorLabel)
panel.add(chartPanel);
panel.add(legendLabel).add(legend);
ui.root.clear()
ui.root.add(Map)
ui.root.add(panel);





