#!/usr/bin/env python

# Nicolas Seriot
# 2015-04-11

import argparse
import os

from Foundation import NSBundle, NSClassFromString, NSDictionary, NSURL

success = NSBundle.bundleWithPath_("/System/Library/PrivateFrameworks/PhotoLibraryPrivate.framework").load()
assert success == True

success = NSBundle.bundleWithPath_("/System/Library/Frameworks/QuartzCore.framework").load()
assert success == True

CIImage = NSClassFromString("CIImage")
assert CIImage

CIFilter = NSClassFromString("CIFilter")
assert CIFilter

NSBitmapImageRep = NSClassFromString("NSBitmapImageRep")
assert NSBitmapImageRep

IPAPhotoAdjustmentStackSerializer_v10 = NSClassFromString("IPAPhotoAdjustmentStackSerializer_v10")
assert IPAPhotoAdjustmentStackSerializer_v10 != None
        
ipaPASS = IPAPhotoAdjustmentStackSerializer_v10.alloc().init()

def cifilter_name_for_aae_file(path):
    d = NSDictionary.dictionaryWithContentsOfFile_(path)
    assert d
    data = d["adjustmentData"]
    assert data
    
    adjustment_stack = ipaPASS.photoAdjustmentStackFromData_error_(data, None)
    assert adjustment_stack
    
    adjustments = adjustment_stack.adjustments()
    assert adjustments
    
    filter_names = ["CIPhotoEffect" + a.settings()["effectName"] for a in adjustments if a.identifier() == "Effect"]
    
    return filter_names[0] if len(filter_names) else None

def apply_cifilter_with_name(filter_name, in_path, out_path):
    
    print "-- in: ", in_path
    print "-- out:", out_path
    
    assert in_path
    assert out_path
    
    assert filter_name in ["CIPhotoEffectTonal", "CIPhotoEffectMono", "CIPhotoEffectInstant", "CIPhotoEffectTransfer",
                           "CIPhotoEffectProcess", "CIPhotoEffectChrome", "CIPhotoEffectNoir", "CIPhotoEffectFade"]
                     
    url = NSURL.alloc().initFileURLWithPath_(in_path)
    ci_image = CIImage.imageWithContentsOfURL_(url)
    assert ci_image
    
    orientation = ci_image.properties().valueForKeyPath_("{TIFF}.Orientation")
    if orientation != None and orientation != 1:
        print "-- orientation:", orientation
        ci_image = ci_image.imageByApplyingOrientation_(orientation)
    
    ci_filter = CIFilter.filterWithName_(filter_name)
    assert ci_filter
    
    ci_filter.setValue_forKey_(ci_image, "inputImage")
    ci_filter.setDefaults()
    
    ci_image_result = ci_filter.outputImage()
    assert ci_image_result
    
    bitmap_rep = NSBitmapImageRep.alloc().initWithCIImage_(ci_image_result)
    assert bitmap_rep
    
    properties = { "NSImageCompressionFactor" : 0.9 }
    data = bitmap_rep.representationUsingType_properties_(3, properties) # 3 for JPEG
    
    assert data.writeToFile_atomically_(out_path, True)

def main():

    parser = argparse.ArgumentParser(description='Restore filters on photos imported from iOS 8 with Image Capture.')
    parser.add_argument("-o", "--overwrite", action='store_true', default=False, help="overwrite original photos with filtered photos")
    parser.add_argument("path", help="path to folder with JPG and AAC files")
    args = parser.parse_args()
    
    aae_files = [ os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.AAE') ]
    
    for aae in aae_files:
        print "-- reading", aae
        
        filter_name = cifilter_name_for_aae_file(aae)
        print "-- filter:", filter_name
    
        name, ext = os.path.splitext(aae)
        jpg_in = name + ".JPG"
                
        if not os.path.exists(jpg_in):
            print "-- missing file:", jpg_in
            continue
            
        jpg_out = jpg_in if args.overwrite else (name + "_" + filter_name + ".JPG")
        
        apply_cifilter_with_name(filter_name, jpg_in, jpg_out)

if __name__=='__main__':
    main()
