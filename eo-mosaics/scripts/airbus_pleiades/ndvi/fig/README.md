# Normalized difference vegetation index, Pleiades

## General description

The well known and widely used [Normalized Difference Vegetation Index (NDVI)](https://en.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index) is a simple, but effective index for quantifying green vegetation. It normalizes green leaf scattering in Near Infra-red wavelengths with chlorophyll absorption in red wavelengths.

The value range of the NDVI is -1 to 1. Negative values of NDVI (values approaching -1) correspond to water. Values close to zero (-0.1 to 0.1) generally correspond to barren areas of rock, sand, or snow. Low, positive values represent shrub and grassland (approximately 0.2 to 0.4), while high values indicate temperate and tropical rainforests (values approaching 1). It is a good proxy for live green vegetation; see [1] for details.

The normalized difference vegetation index, abbreviated NDVI, is defined as   

$$NDVI := \mathtt{Index}(NIR,RED) = \frac{NIR-RED}{NIR+RED}.$$  

For Pleiades, the index looks like this:

$$NDVI := \mathtt{Index}(B3,B2) = \frac{B3-B2}{B3+B2}.$$   

## Description of representative images

NDVI of Rome. 

![NDVI of Rome](fig/ndvi.jpg)