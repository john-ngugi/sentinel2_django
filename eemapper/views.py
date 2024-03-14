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


    sentinelCollection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")\
    .filterDate('2017-01-01','2023-12-30')\
    .filterMetadata('CLOUDY_PIXEL_PERCENTAGE','less_than',15).map(mask_s2_clouds)
    
    sentinel_vis_params = {
        'min': 0,
        'max':0.3,
        'bands':['B4','B3','B2']
    }
    
    Map.addLayer(sentinelCollection,sentinel_vis_params,'sentinel image')
    
    
    context = {
    'map': Map.to_html()
    }
    return render(request,'index.html',context=context)