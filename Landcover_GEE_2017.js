// ============================
// Earth Engine LULC Visualization for 2017 Only
// ============================

// Configuration
var CONFIG = {
  year: 2017,
  collection: 'projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m_TS',
  
  // Land cover class definitions
  landCover: {
    names: [
      "Water", "Trees", "Flooded Vegetation", "Crops", 
      "Built Area", "Bare Ground", "Snow/Ice", "Clouds", "Rangeland"
    ],
    colors: [
      "#1A5BAB", "#358221", "#87D19E", "#FFDB5C", 
      "#ED022A", "#EDE9E4", "#F2FAFF", "#C8C8C8", "#eecfa8"  // Updated Rangeland color
    ],
    remapFrom: [1, 2, 4, 5, 7, 8, 9, 10, 11],
    remapTo:   [1, 2, 3, 4, 5, 6, 7, 8, 9]
  },
  
  visParams: {
    min: 1,
    max: 9
  }
};

// Load LULC collection
var esriLulc = ee.ImageCollection(CONFIG.collection);

// Remap function
function remapLandCover(image) {
  return image.remap(CONFIG.landCover.remapFrom, CONFIG.landCover.remapTo);
}

// Create 2017 composite
var startDate = ee.Date.fromYMD(CONFIG.year, 1, 1);
var endDate   = ee.Date.fromYMD(CONFIG.year, 12, 31);

var lulc2017 = esriLulc
  .filterDate(startDate, endDate)
  .mosaic();

var remapped2017 = remapLandCover(lulc2017);

// Add to map
Map.setCenter(0, 0, 2);
Map.addLayer(remapped2017, 
             {min: CONFIG.visParams.min, max: CONFIG.visParams.max, palette: CONFIG.landCover.colors}, 
             CONFIG.year + ' LULC 10m');

// Legend
function createLegend() {
  var panel = ui.Panel({style: {position: 'bottom-left', padding: '8px 15px', backgroundColor: 'white'}});
  
  panel.add(ui.Label('Land Cover Classes', {fontWeight: 'bold', fontSize: '16px', margin: '0 0 8px 0'}));
  
  CONFIG.landCover.names.forEach(function(name, i) {
    var row = ui.Panel({
      widgets: [
        ui.Label('', {backgroundColor: CONFIG.landCover.colors[i], padding: '8px', margin: '0 0 4px 0', border: '1px solid #ccc'}),
        ui.Label(name, {margin: '0 0 4px 6px'})
      ],
      layout: ui.Panel.Layout.Flow('horizontal')
    });
    panel.add(row);
  });
  
  Map.add(panel);
}

createLegend();
