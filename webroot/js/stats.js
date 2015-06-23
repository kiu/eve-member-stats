// ---------------------------------------------------------------

history_options = {
    responsive: true,

    bezierCurve : true,

    pointDot : true,
    pointDotRadius : 3,
    pointDotStrokeWidth : 1,

    datasetStroke : true,
    datasetStrokeWidth : 2,
    datasetFill : true,

    animation : true,
    animationSteps : 100,
    animationEasing : "easeOutQuart",
}

doughnut_options = {
    responsive: true,

    segmentShowStroke : true,
    segmentStrokeColor : "#fff",
    segmentStrokeWidth : 1,

    percentageInnerCutout : 40, // This is 0 for Pie charts

    animation : true,
    animationSteps : 100,
    animationEasing : "easeOutBounce",

    legendTemplate : "<% for (var i=0; i<segments.length; i++){%><span style=\"background-color:<%=segments[i].fillColor%>\">&nbsp;&nbsp;&nbsp;&nbsp;</span> <%if(segments[i].label){%><%=segments[i].label%> (<%=segments[i].value%>)<br><%}%><%}%>",
}


function loadDoughnut(name) {
    var ctx = $("#chart-" + name).get(0).getContext("2d");
    $.getJSON("stats_" + name + ".json", function(data) {
	var c = new Chart(ctx).Doughnut(data, doughnut_options);
	$("#legend-" + name).html(c.generateLegend());
    });
}

$(document).ready(function() {

    var ctx = $("#chart-history").get(0).getContext("2d");
    $.getJSON("stats_history.json", function(data) {
	var c = new Chart(ctx).Line(data, history_options);
    });

    loadDoughnut("security-28");
    loadDoughnut("security-21");
    loadDoughnut("security-14");
    loadDoughnut("security-7");

    loadDoughnut("region-28");
    loadDoughnut("region-21");
    loadDoughnut("region-14");
    loadDoughnut("region-7");

    loadDoughnut("system-28");
    loadDoughnut("system-21");
    loadDoughnut("system-14");
    loadDoughnut("system-7");

    $.getJSON("stats_last_update.json", function(data) {
	$('#last_update').html(data['last_update']);
    });
});


// ---------------------------------------------------------------

