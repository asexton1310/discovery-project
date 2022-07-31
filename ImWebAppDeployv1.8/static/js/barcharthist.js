function barChartHist(values){

var xValues = ["bitrate",
"framerate",
"resolution",
"avg_blockiness",
"max_blockiness",
"min_blockiness",
"avg_blur",
"max_blur",
"min_blur",
"avg_contrast",	
"max_contrast",	
"min_contrast",
"avg_color",	
"max_color",	
"min_color",	
"avg_ltp",
"max_ltp",
"min_ltp",
"avg_noise",	
"max_noise",	
"min_noise",	
"avg_brisque",
"max_brisque",	
"min_brisque",	
"avg_flicker",	
"avg_flickering_agh",	
"avg_blockiness_agh",	
"avg_letterBox_agh",	
"avg_pillarBox_agh",	
"avg_blockloss_agh",	
"avg_blur_agh",
"avg_blackout_agh",
"avg_freezing_agh",	
"avg_exposure_agh",	
"avg_contrast_agh",	
"avg_interlace_agh",	
"avg_noise_agh",	
"avg_si_agh",	
"avg_ti_agh",
"quality_estimate"];
chunks = values.split('|');
const index = chunks.indexOf("");
if (index > -1) { 
  chunks.splice(index, 1); 
}
console.log(chunks);
chunknums = [];
for(i = 0; i < chunks.length; i++){
  chunknums.push(parseInt(i)+1);
}
console.log(chunknums);
bitrate = [];
framerate = [];
resolution = [];
avg_blockiness = [];
max_blockiness = [];
min_blockiness = [];
avg_blur = [];
max_blur = [];
min_blur = [];
avg_contrast = [];
max_contrast = [];
min_contrast = [];
avg_color	= [];
max_color	= [];
min_color	= [];
avg_ltp = [];
max_ltp = [];
min_ltp	= [];
avg_noise	= [];
max_noise	= [];
min_noise	= [];
avg_brisque = [];
max_brisque	= [];
min_brisque	= [];
avg_flicker	= [];
avg_flickering_agh = [];	
avg_blockiness_agh = [];	
avg_letterBox_agh	= [];
avg_pillarBox_agh	= [];
avg_blockloss_agh	= [];
avg_blur_agh = [];
avg_blackout_agh = []
avg_freezing_agh = [];
avg_exposure_agh = [];
avg_contrast_agh	= [];
avg_interlace_agh	= [];
avg_noise_agh	= [];
avg_si_agh = [];
avg_ti_agh = [];
quality_estimate = [];
for(j = 0; j<chunks.length; j++){
  holdarr = chunks[j].split(';');
  index1 = holdarr.indexOf("");
  if (index1 > -1) { 
    holdarr.splice(index1, 1); 
  }
  bitrate.push(holdarr[0]);
  framerate.push(holdarr[1]);
  resolution.push(holdarr[2]);
  avg_blockiness.push(holdarr[3]);
  max_blockiness.push(holdarr[4]);
  min_blockiness.push(holdarr[5]);
  avg_blur.push(holdarr[6]);
  max_blur.push(holdarr[7]);
  min_blur.push(holdarr[8]);
  avg_contrast.push(holdarr[9]);	
  max_contrast.push(holdarr[10]);	
  min_contrast.push(holdarr[11]);
  avg_color.push(holdarr[12]);	
  max_color.push(holdarr[13]);	
  min_color.push(holdarr[14]);	
  avg_ltp.push(holdarr[15]);
  max_ltp.push(holdarr[16]);
  min_ltp.push(holdarr[17]);
  avg_noise.push(holdarr[18]);	
  max_noise.push(holdarr[19]);	
  min_noise.push(holdarr[20]);	
  avg_brisque.push(holdarr[21]);
  max_brisque.push(holdarr[22]);	
  min_brisque.push(holdarr[23]);	
  avg_flicker.push(holdarr[24]);	
  avg_flickering_agh.push(holdarr[25]);	
  avg_blockiness_agh.push(holdarr[26]);	
  avg_letterBox_agh.push(holdarr[27]);	
  avg_pillarBox_agh.push(holdarr[28]);	
  avg_blockloss_agh.push(holdarr[29]);	
  avg_blur_agh.push(holdarr[30]);
  avg_blackout_agh.push(holdarr[31]);
  avg_freezing_agh.push(holdarr[32]);	
  avg_exposure_agh.push(holdarr[33]);	
  avg_contrast_agh.push(holdarr[34]);	
  avg_interlace_agh.push(holdarr[35]);	
  avg_noise_agh.push(holdarr[36]);	
  avg_si_agh.push(holdarr[37]);	
  avg_ti_agh.push(holdarr[38]);
  quality_estimate.push(holdarr[39]);
}
console.log(bitrate);



var ctx = document.getElementById('myChart');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'Bitrate',
      data: bitrate,
      borderColor: "red",
      fill: false
    }]
  },
  options: {
    legend: {display: true},
    text: "Bitrate",
  }
});
var ctx = document.getElementById('myChart2');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'Framerate',
      data: framerate,
      borderColor: "green",
      fill: false
    }]
  },
  options: {
    legend: {display: true},
    text: "Framerate",
  }
});
var ctx = document.getElementById('myChart3');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'Resolution',
      data: resolution,
      borderColor: "orange",
      fill: false
    }]
  },
  options: {
    legend: {display: true},
    text: "Resolution",
  }
});


var ctx = document.getElementById('myChart4');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'avg_blockiness',
      data: avg_blockiness,
      borderColor: "red",
      fill: false
    }, { 
      label: 'max_blockiness',
      data: max_blockiness,
      borderColor: "green",
      fill: false
    }, { 
      label: 'min_blockiness',
      data: min_blockiness,
      borderColor: "blue",
      fill: false
    }, { 
      label: 'avg_blur',
      data: avg_blur,
      borderColor: "green",
      fill: false
    }, { 
      label: 'max_blur',
      data: max_blur,
      borderColor: "#D2691E",
      fill: false
    }, { 
      label: 'min_blur',
      data: min_blur,
      borderColor: "#FF7F50",
      fill: false
    }, { 
      label: 'avg_contrast',
      data: avg_contrast,
      borderColor: "#6495ED",
      fill: false
    }, { 
      label: 'max_contrast',
      data: max_contrast,
      borderColor: "#FFF8DC",
      fill: false
    }, { 
      label: 'min_contrast',
      data: min_contrast,
      borderColor: "#DC143C",
      fill: false
    }, { 
      label: 'avg_color',
      data: avg_color,
      borderColor: "#00FFFF",
      fill: false
    }, { 
      label: 'max_color',
      data: max_color,
      borderColor: "#BDB76B",
      fill: false
    }, { 
      label: 'min_color',
      data: min_color,
      borderColor: "#8B008B",
      fill: false
    }, { 
      label: 'avg_ltp',
      data: avg_ltp,
      borderColor: "#556B2F",
      fill: false
    }, { 
      label: 'max_ltp',
      data: max_ltp,
      borderColor: "#FF8C00",
      fill: false
    }, { 
      label: 'min_ltp',
      data: min_ltp,
      borderColor: "#9932CC",
      fill: false
    }, { 
      label: 'avg_noise',
      data: avg_noise,
      borderColor: "#8B0000",
      fill: false
    }, { 
      label: 'max_noise',
      data: max_noise,
      borderColor: "#E9967A",
      fill: false
    }, { 
      label: 'min_noise',
      data: min_noise,
      borderColor: "#228B22",
      fill: false
    }, { 
      label: 'avg_brisque',
      data: avg_brisque,
      borderColor: "#FF69B4",
      fill: false
    }, { 
      label: 'max_brisque',
      data: max_brisque,
      borderColor: "#CD5C5C",
      fill: false
    }, { 
      label: 'min_brisque',
      data: min_brisque,
      borderColor: "#4B0082",
      fill: false
    }, { 
      label: 'avg_flicker',
      data: avg_flicker,
      borderColor: "#F08080",
      fill: false
    }, { 
    }]
  },
  options: {
    legend: {display: true}
  }
});

var ctx = document.getElementById('myChart5');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'avg_flickering_agh',
      data: avg_flickering_agh,
      borderColor: "#800000",
      fill: false
    }, { 
      label: 'avg_blockiness_agh',
      data: avg_blockiness_agh,
      borderColor: "#BA55D3",
      fill: false
    }, { 
      label: 'avg_letterBox_agh',
      data: avg_letterBox_agh,
      borderColor: "#3CB371",
      fill: false
    }, { 
      label: 'avg_pillarBox_agh',
      data: avg_pillarBox_agh,
      borderColor: "#FFE4E1",
      fill: false
    }, { 
      label: 'avg_blockloss_agh',
      data: avg_blockloss_agh,
      borderColor: "#FF8C00",
      fill: false
    }, { 
      label: 'avg_blur_agh',
      data: avg_blur_agh,
      borderColor: "#FF69B4",
      fill: false
    }, { 
      label: 'avg_blackout_agh',
      data: avg_blackout_agh,
      borderColor: "#7CFC00",
      fill: false
    }, { 
      label: 'avg_freezing_agh',
      data: avg_freezing_agh,
      borderColor: "#ADD8E6",
      fill: false
    }, { 
      label: 'avg_exposure_agh',
      data: avg_exposure_agh,
      borderColor: "#90EE90",
      fill: false
    }, { 
      label: 'avg_contrast_agh',
      data: avg_contrast_agh,
      borderColor: "#20B2AA",
      fill: false
    }, { 
      label: 'avg_interlace_agh',
      data: avg_interlace_agh,
      borderColor: "#C71585",
      fill: false
    }, { 
      label: 'avg_noise_agh',
      data: avg_noise_agh,
      borderColor: "#F5FFFA",
      fill: false
    }, { 
      label: 'avg_si_agh',
      data: avg_si_agh,
      borderColor: "#48D1CC",
      fill: false
    }, { 
      label: 'avg_ti_agh',
      data: avg_ti_agh,
      borderColor: "#FFA500",
      fill: false
    }, { 
    }]
  },
  options: {
    legend: {display: true}
  }
});

var ctx = document.getElementById('myChart6');
new Chart(ctx, {
  type: "line",
  data: {
    labels: chunknums,
    datasets: [{ 
      label: 'Quality Estimate',
      data: quality_estimate,
      borderColor: "#00FF00",
      fill: false
    }]
  },
  options: {
    legend: {display: true},
    text: "Quality Estimate",
  }
});
}