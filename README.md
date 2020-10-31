# Access-Control-using-AWS-Face-Rekognition-Service-in-Python
In this project, we propose the use of facial recognition in access control system. Nowadays, facial recognition is applied in many fields from logging in to user account through built in camera of smartphones to identification of suspected people by the law enforcements. A manager of a company that uses this system have access to an application, which is designed to let the manger add staff of the company as well as any suspected criminal along with their photo. The application let the manager assign the staffs as employees, but suspected people are assigned as blacklists. The information is stored in amazon web service. On the other hand, a camera is implemented at a required entrance to stream real time video and detect face. If face is detected, the camera sends face recognition request to amazon web service where the manager previously added people. Finally, the system will be able to recognize the detected face as either employee, blacklist or unknown. The entrance opens if the face is recognized as an employee, whereas if the face is unknown the entrance remains closed and a speaker asks the user to visit the security for more information. If the face is detected as a blacklist, the system alerts an alarm.



How this project works:

First, open Amazon Web Service Account so that you use Amazon face rekognition service, 
which is extensively applied in this project. 
In your account, go to user and try to add new policies, Rekognition full access and IAM user.

Then, open admin_monitor.py in your favourite python editor and change the access_key_id and 
