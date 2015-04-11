# filters
Apply filters on iOS Camera.app JPG files imported with Image Capture.

### Problem

iOS 8 lets you apply filters on photos like "Chrome", "Transfer" or "Instant".

But when you import the photos on a Mac, the filters are lost.

### Solution

1. import the photos with Image Capture
2. run `$ python filters.py`

### Algorithm

    for each AAE file:
        if there is a paired JPG file:
            read the filter name in the AAE file
            apply the filter to the JPG file
            save the new JPG file

### Disclaimer

Quick and dirty PyObjC script that you can read and hack.

Works for me on OS X 10.10.3.
