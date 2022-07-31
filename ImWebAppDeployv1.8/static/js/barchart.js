function makeChart(values){
var xValues = ["avg_blockiness",
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
values = values = values.substring(1);
values = values.substring(0, values.length - 1);
var final_y = values.split(',').map(Number);
var yValues = final_y;
console.log(xValues);
console.log(final_y);
console.log(xValues.length);
console.log(final_y.length);
var barColors = ["#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#ffb8b1", "#993441", "#f93800"]
var ctx = document.getElementById('myChart');
new Chart(ctx, {
  type: "bar",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "Quality Metrics"
    }
  }
});
}