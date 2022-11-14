//VERSION=3
function setup() {
  return {
    input: [{
      bands: [
        "B04",
        "B03",
        "B02",
        "B08",
        "SCL"
      ]
    }],
    output: {
      bands: 4,
      sampleType: SampleType.UINT16
    },
    mosaicking: "ORBIT"
  }
}

function evaluatePixel(sample)
{
return [sample.B04, sample.B03, sample.B02, sample.B08, sample.SCL]
}
