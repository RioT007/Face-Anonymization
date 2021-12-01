import cv2
import sys 
import argparse
import numpy as np

# Defining class Anonymize
class Anonymize:
    # Initialise Function Variables and streaming video input
    def __init__(self,path = None,border = False,pixel = False,mask = False,save = None) -> None:
        self.border = border
        self.pixel = pixel
        self.mask = mask
        self.mask_img = cv2.imread('emoji.jpg')
        self.save = save
        # Taking two types of inputs
        self.videoInput = cv2.VideoCapture(path) if path is not None else cv2.VideoCapture(0, cv2.CAP_DSHOW)
        # Haar Cascade to detect frontal faces
        self.cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
        if self.save:
            self.out = cv2.VideoWriter(save,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (int(self.videoInput.get(3)),int(self.videoInput.get(4))))
        if not self.videoInput.isOpened:
            print('Camera Error')   
        while True:
            self.read()            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.videoInput.release()
        cv2.destroyAllWindows()
    # Reading Video Input frame by frame and the performing appropriate processing technique
    def read(self)->None:
        _, frame = self.videoInput.read()
        # Detect faces in the Webcam Video Stream
        faces = self.cascade.detectMultiScale(frame,1.3,5)
        for (a,b,c,d) in faces:
            # Enclose inside a rectangular box if specified in input
            if self.border:
                cv2.rectangle(frame,(a,b),(a+c,b+d),(0,0,0),3)
            # Blur the detected face pixels 
            if not self.pixel and not self.mask:
                frame[b:b + d, a:a + c] = self.blur(frame[b:b + d, a:a + c])
            elif self.mask:    
                swap_roi = cv2.resize(self.mask_img,(c,d))
                frame[b:b+d,a:a+c] = swap_roi
            else:
                frame[b:b + d, a:a + c] = self.pixelate(frame[b:b + d, a:a + c])
        # Display the Blurred Faces
        if self.save!=None:
            self.out.write(frame)
        cv2.imshow('Detected Face',frame)
    
    def blur(self,roi,factor=3):
        # Determine the size of the blurring kernel based on the spatial dimensions of the input image
        (h, w) = roi.shape[:2]
        kW = int(w / factor)
        kH = int(h / factor)
        # Wwidth of the kernel must be odd
        if kW % 2 == 0:
            kW -= 1
        # Height of the kernel must be odd
        if kH % 2 == 0:
            kH -= 1
        # Apply Gaussian Blur using determined kernel size
        return cv2.GaussianBlur(roi, (kW, kH), 0)

    def pixelate(self,roi, blocks=10):
        # Divide the input image into 10x10 blocks
        (h, w) = roi.shape[:2]
        xSet = np.linspace(0, w, blocks + 1, dtype="int")
        ySet = np.linspace(0, h, blocks + 1, dtype="int")
        # loop over the blocks in both the x and y direction
        for i in range(1, len(ySet)):
            for j in range(1, len(xSet)):
                # Compute the starting and ending (x,y) coordinates for the current block
                xStart = xSet[j - 1]
                yStart = ySet[i - 1]
                xEnd = xSet[j]
                yEnd = ySet[i]
                # Extract the ROI using NumPy array slicing, compute the mean of the ROI, and 
                # then draw a rectangle with the mean RGB values over the ROI in the original image
                mean_roi = roi[yStart:yEnd, xStart:xEnd]
                (B, G, R) = [int(x) for x in cv2.mean(mean_roi)[:3]]
                cv2.rectangle(roi, (xStart, yStart), (xEnd, yEnd),(B, G, R), -1)
        # Return the pixelated blurred image
        return roi
    
# Main Function
if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Python Script to anonymize detetected faces using OpenCV",allow_abbrev=False)
    # Flag to be specified while running to pass video as input
    parser.add_argument('-i',"--input", action='store', type=str,help="Enter the location of the video")
    # Flag to be specified while running to enable borders while blurring
    parser.add_argument('-b',"--border", action='store_true', help="To display a Border")
    # Flag to be specified while running to pixelate face
    parser.add_argument('-p',"--pixel", action='store_true', help="To Pixelize the Face")
    # Flag to be specified while running to mask face
    parser.add_argument('-m',"--mask", action='store_true', help="To Mask the Face")
    # Flag to be specified while running to save processed video
    parser.add_argument('-s',"--save", action='store', type=str,help="Enter the location to save the video")
    args = parser.parse_args()
    try:
        Anonymize(args.input,args.border,args.pixel,args.mask,args.save)
    except Exception as ex:
        message = "An exception of type {0} occurred. Arguments:\n{1!r}".format(type(ex).__name__, ex.args)
        print(message)
        sys.exit('Video Closed')