import dlib
import cv2
from imutils.video import VideoStream
import imutils
import time

import boto3

# with open('credentials.csv','r') as input:
#     next(input)
#     reader=csv.reader(input)
#     for line in reader:
#         access_key_id=line[2]
#         secret_access_key=line[3]
access_key_id='AKIA4GWCL3QRXRBFSUVJ'
secret_access_key='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'

tempUser= open('tempUser', 'r')
col_id= tempUser.read()
def recognizeFace():
    photo= 'result.jpg'

    # client access for rekognition
    client=boto3.client('rekognition',
                        aws_access_key_id = access_key_id,
                        aws_secret_access_key=secret_access_key,
                        region_name='us-east-2')


    # encode the image and get a response
    with open(photo, 'rb') as source_image:
        source_bytes= source_image.read()

    # #  to use phot from the aws s3 storage, apply this code
    response= client.search_faces_by_image(
        CollectionId=col_id,
        Image={'Bytes': source_bytes}
    )

    # since response is a dictionary, we can loop it
    #print(response)
    return response

    


detector = dlib.get_frontal_face_detector()

print("->Starting Face Detection")
c = VideoStream(src=0).start()               #For webcam, comment it if using Raspberry Pi Camera module
# c = VideoStream(usePiCamera=True).start()       #For Raspberry Pi Camera module, comment it if using webcam
# time.sleep(2.0)
while True:

    frame = c.read()
    # frame = imutils.resize(frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)

    name = ''
    auth = ''

    if rects:
        cv2.imwrite('result.jpg',frame)
        print("face detected")
        
        response= recognizeFace()

        for key, value in response.items():
            if key=='FaceMatches':   #go to facematch key of the response dictionary
                if value:             #check if faceMatch have value as list

                    if(value[0]['Similarity']>80):  # similarity of captured image and photo at collection should be greater than 80, just to make sure it is accurate
                        print(key)

                        information=value[0]['Face']['ExternalImageId'].split(".")   # remove .jpg or .png

                        info=information[0].split("_")     # split the names

                        name=info[0]+" "+info[1]
                        authorization=info[2]

                        if authorization=='a':
                            auth='Employee'
                            print("Name: "+ name,"\nAuthorization: Employee")

                        elif(authorization=="b"):
                            auth='Blacklist'
                            print("Name: ", name ,"\nAuthorization: Blacklist")

                        print("Similarity rate: ", value[0]['Similarity'],
                              "\nFace ID from collection: ", value[0]['Face']['FaceId'],
                              "\nImage ID captured photo: ", value[0]['Face']['ImageId'],
                              # "\nImage Name: ", value[0]['Face']['ExternalImageId'],    ###### note: we can put the name of the person and authorization here
                              )  # value[0] is dictionary



                else:                  #if it is empty, then there is no simillary person
                    name='Unknown Person'
                    print("Unknown Person")

        for rect in rects:
            x1 = rect.left()
            y1 = rect.top()-30
            x2 = rect.right()
            y2 = rect.bottom()
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, auth, (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        #time.sleep(50.0)


    cv2.imshow("Frame", frame)
    if rects:
        cv2.waitKey(0)

    key = cv2.waitKey(1) & 0xFF
        

    if key == ord("q"):
        break

cv2.destroyAllWindows()
c.stop()