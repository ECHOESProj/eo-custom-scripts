//VERSION=3
// Simple Ratio Red/NIR Ratio Vegetation-Index (abbrv. SRRed/NIR)
//
// General formula: RED/NIR
// This is an auto-generated script. Double checking the source information with the URL below is recommended.
// URL https://www.indexdatabase.de/db/si-single.php?sensor_id=168&rsindex_id=568

let index = B04 / B05;
let min = 0.058;
let max = 17.267;

// colorBlend will return a color when the index is between min and max and white when it is less than min.
// To see black when it is more than max, uncomment the last line of colorBlend.
// The min/max values were computed automatically and may be poorly specified, feel free to change them to tweak the displayed range.

var underflow_color = [1, 1, 1];
var low_color = [208/255, 88/255, 126/255];
var high_color = [241/255, 234/255, 200/255];
var overflow_color = [0, 0, 0];

return colorBlend(index, [min, min, max],
[
	underflow_color,
	low_color,
	high_color,
	//overflow_color // uncomment to see overflows
]);
