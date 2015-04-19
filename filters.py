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

def apply_cifilter_with_name(filter_name, orientation, in_path, out_path, dry_run=False):
    
    print "-- in: ", in_path
    print "-- out:", out_path
    
    assert in_path
    assert out_path
    
    assert filter_name in ["CIPhotoEffectTonal", "CIPhotoEffectMono", "CIPhotoEffectInstant", "CIPhotoEffectTransfer",
                           "CIPhotoEffectProcess", "CIPhotoEffectChrome", "CIPhotoEffectNoir", "CIPhotoEffectFade"]
                     
    url = NSURL.alloc().initFileURLWithPath_(in_path)
    ci_image = CIImage.imageWithContentsOfURL_(url)
    assert ci_image
    
    #orientation = ci_image.properties().valueForKeyPath_("{TIFF}.Orientation")
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
    
    if dry_run:
        print "-- dryrun, don't write", out_path
        return
    
    assert data.writeToFile_atomically_(out_path, True)

def main():

    parser = argparse.ArgumentParser(description='Restore filters on photos imported from iOS 8 with Image Capture.')
    parser.add_argument("-o", "--overwrite", action='store_true', default=False, help="overwrite original photos with filtered photos")
    parser.add_argument("-d", "--dryrun", action='store_true', default=False, help="don't write anything on disk")
    parser.add_argument("path", help="path to folder with JPG and AAC files")
    args = parser.parse_args()
    
    aae_files = [ os.path.join(args.path, f) for f in os.listdir(args.path) if f.endswith('.AAE') ]
    
    for aae in aae_files:
        print "-- reading", aae
        
        d1 = NSDictionary.dictionaryWithContentsOfFile_(aae)
        data = d1["adjustmentData"]
        
        d2 = ipaPASS.archiveFromData_error_(data, None)
        if not d2:
            print "-- can't read data from", aae
            continue
        
        adjustments = d2["adjustments"]
        orientation = d2["metadata"]["orientation"]
        
        effect_names = [ d["settings"]["effectName"] for d in d2["adjustments"] if d["identifier"] == "Effect" and "effectName" in d["settings"]]
        if len(effect_names) == 0:
            continue
        
        filter_name = "CIPhotoEffect" + effect_names[0]
        print "-- filter:", filter_name
        
        name, ext = os.path.splitext(aae)
        jpg_in = name + ".JPG"
                
        if not os.path.exists(jpg_in):
            print "-- missing file:", jpg_in
            continue
                
        jpg_out = jpg_in if args.overwrite else (name + "_" + filter_name + ".JPG")
        
        apply_cifilter_with_name(filter_name, orientation, jpg_in, jpg_out, args.dryrun)

if __name__=='__main__':
    main()
