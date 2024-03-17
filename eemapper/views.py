from django.shortcuts import render
import geemap.foliumap as geemap 
import ee 
# Create your views here.


def index(request):
    
    Map = geemap.Map() 
    # load our image collection 
    
    
    def mask_s2_clouds(image):
        """Masks clouds in a Sentinel-2 image using the QA band.

        Args:
            image (ee.Image): A Sentinel-2 image.

        Returns:
            ee.Image: A cloud-masked Sentinel-2 image.
        """
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = (
            qa.bitwiseAnd(cloud_bit_mask)
            .eq(0)
            .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
        )

        return image.updateMask(mask).divide(10000)
     
     
    ROI = ee.FeatureCollection('projects/ee-muthamijohn/assets/Taita_Taveta')

    sentinelCollection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")\
    .filterDate('2017-01-01','2023-12-30')\
    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE','less_than',1).map(mask_s2_clouds)\
    .filterBounds(ROI)
    
    
    Map.centerObject(sentinelCollection,10)
    
    sentinel_image = sentinelCollection.median().clip(ROI)
    sentinel_vis_params = {
        'min': 0,
        'max':0.3,
        'bands':['B4','B3','B2']
    }
    
    ndvi = sentinel_image.normalizedDifference(['B4','B8'])
    ndvi_vis_params= {
        'min':-1,
        'max':1,
        'palette':['red','yellow','green']
    }
    
    Map.addLayer(sentinelCollection,sentinel_vis_params,'sentinel collection')
    Map.addLayer(sentinel_image,sentinel_vis_params,'sentinel image')
    Map.addLayer(ndvi,ndvi_vis_params,'ndvi')
    
    context = {
    'map': Map.to_html()
    }
    return render(request,'index.html',context=context)