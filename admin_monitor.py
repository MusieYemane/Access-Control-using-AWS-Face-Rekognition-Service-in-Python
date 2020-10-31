import csv
import tkinter as tk
from tkinter import *
import os
import logging
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import boto3
from botocore.exceptions import ClientError
import _sqlite3

### Before running this code, create an amazone account user and get the aws secret key and access key id.
###And also go to aws users--> add permissions--> add AmazoneS3Fullaccess and AmazonRekognitionFullAccess and IAMUserChanegePassword permissions

access_key_id = 'AKIA4GWCL3QRXRBFSUVJ' ##Enter your AWS access key id here for ex. 'AKIL4GOQL&QREDSFFUTQT'
secret_access_key = 'QS5R/xw5zdZ2bcXebz2ZYyEEQlmqdEibrzyn2S2l' ##Enter your AWS Secret access key here ex.'QS5W/xw5zdM6bcZwbz2ZYyLLQlmqdEibQIyn4L87'

# create a database or connect to one

conn = _sqlite3.connect('Register.db')

# create a cursor

c = conn.cursor()


# # create a table
#
# c.execute(""" CREATE TABLE address(
#     firs_name text,
#     last_name text,
#     username text,
#     password text
#
#     )""")


################################################################################################
# create subbimit functio to define submit

f = open("tempUser", "r")
uname = f.readline()
f.close()

class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        # Setup Menu
        MainMenu(self)
        self.winfo_toplevel().title("Face Recognition Access Control")
        # Setup Frame
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, loginPage, signupPage, deleteAccountPage, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")


        if not uname:
            self.show_frame(StartPage)
        else:
            self.show_frame(PageTwo)


    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class StartPage(Frame):
    def __init__(self, parent, controller):

        Frame.__init__(self, parent)
        self.controller = controller

        Frame.config(self,bg='lightgreen')

        label = Label(self, text="                                                      Start Page                                                            ",
                      font=("Arial Black", 20, 'bold'), bg= 'darkred', fg='lightyellow')
        label.grid(row=0, )

        btnLogin = Button(self, text="Log In", width=50,
                          command=lambda: controller.show_frame(loginPage))
        btnLogin.grid(row=1, column=0, ipady=20, pady=20, padx=120)
        btnSignup = Button(self, text="Sign Up", width=50,
                           command=lambda: controller.show_frame(signupPage))
        btnSignup.grid(row=2, column=0, ipady=20, pady=20, padx=120)

        deleteAccount = Button(self, text="Delete Account", width=50,
                               command=lambda: controller.show_frame(deleteAccountPage))
        deleteAccount.grid(row=3, column=0, ipady=20, pady=20, padx=120)



class loginPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self, bg='lightgreen')

        label = Label(self, text="                                 Login Page                                   ",
                      font=("Arial Black", 20, 'bold'), bg= 'darkred', fg='lightyellow')
        label.grid(row=0, column=0, columnspan=2)
        label.config(font=("Times", 40, 'bold'), fg='white', bg='darkred')

        username_label = Label(self, text="Username:",font=("Times", 20), bg='lightgreen')
        username_label.grid(row=2, column=0, pady=20)

        password_label = Label(self, text="Password:", font=("Times", 20), bg='lightgreen')
        password_label.grid(row=3, column=0, pady=20)

        self.username = Entry(self, width=30)
        self.username.grid(row=2, column=1, padx=0, pady=20)

        self.password = Entry(self, width=30, show="*")
        self.password.grid(row=3, column=1, padx=0, pady=20)

        login_btn = Button(self, text="Login", command=self.login)
        login_btn.grid(row=4, column=0, columnspan=2,
                       pady=20, padx=10, ipadx=100, ipady=10)

        login_btn = Button(self, text="Back",
                           command=lambda: controller.show_frame(StartPage))
        login_btn.grid(row=5, column=0, columnspan=2,
                       pady=20, padx=10, ipadx=100, ipady=10)

    def login(self):
        conn = _sqlite3.connect('Register.db')

        # create a cursor

        c = conn.cursor()
        print_results = ''
        if self.username.get == "" or self.password.get() == "":
            messagebox.showerror('Incomplete Entry','Please complete the required field!')
            # print_results = "Please complete the required field!"
        else:
            c.execute("select * FROM `address` WHERE `username` = ? and `password` = ?",
                      (self.username.get(), self.password.get()))

            if c.fetchone() is not None:
                # print_results = "You Successfully login"
                #set username to the log in username to identify his collection and folder photo

                # write the input to tempUser to remember him as temporary user
                f = open("tempUser", "w")
                f.write(self.username.get())

                f = open("tempUser", "r")
                uname=f.readline()
                # update the uname in PageTwo
                self.controller.get_page(PageTwo).setUserName()

                self.controller.get_page(PageTwo).list_faces_in_collection()
                self.controller.show_frame(PageTwo)
                f.close()

            else:
                messagebox.showerror('Invalid Entry', 'Invalid Username or password')
                # print_results = text = "Invalid Username or password"
        self.username.delete(0, END)
        self.password.delete(0, END)

        # create label results
        lbl_result1 = Label(self, text=print_results)
        lbl_result1.grid(row=11, column=0, columnspan=2)

        # commit changes
        conn.commit()

        # close connection
        conn.close()

    # create a delete registry function


class signupPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self, bg='lightgreen')

        label = Label(self, text="                               Signup Page                                   ",
                      font=("Arial Black", 20, 'bold'), bg='darkred', fg='lightyellow')
        label.grid(row=0, column=0, columnspan=2)
        label.config(font=("Times", 40, 'bold'), fg='white', bg='darkred')


        self.f_name = Entry(self, width=30)
        self.f_name.grid(row=1, column=1, padx=20)

        self.l_name = Entry(self, width=30)
        self.l_name.grid(row=2, column=1, padx=20)

        self.username = Entry(self, width=30)
        self.username.grid(row=3, column=1, padx=20)

        self.password = Entry(self, width=30, show="*")
        self.password.grid(row=4, column=1, padx=20)

        self.email = Entry(self, width=30)
        self.email.grid(row=5, column=1, padx=20)
        #########################################################################################################
        # create Text Boxes Labels
        f_name_label = Label(self, text="First Name", font=("Times New Roman", 16), bg='lightgreen')
        f_name_label.grid(row=1, column=0, pady=20, )

        l_name_label = Label(self, text="Last Name", font=("Times New Roman", 16),bg='lightgreen')
        l_name_label.grid(row=2, column=0, pady=20)

        username_label = Label(self, text="Username", font=("Times New Roman", 16),bg='lightgreen')
        username_label.grid(row=3, column=0, pady=20)

        password_label = Label(self, text="Password", font=("Times New Roman", 16),bg='lightgreen')
        password_label.grid(row=4, column=0, pady=20)

        lblEmail = Label(self, text="Email", font=("Times New Roman", 16), bg='lightgreen')
        lblEmail.grid(row=5, column=0, pady=20)

        ########################################################################################################
        # create a submit buttons
        submit_btn = Button(self, text="Register", command=self.submit)
        submit_btn.grid(row=6, column=0, columnspan=2,
                        pady=10, padx=10, ipadx=100, ipady=20)

        login_btn = Button(self, text="Back",
                           command=lambda: controller.show_frame(StartPage))
        login_btn.grid(row=7, column=0, columnspan=2,
                       pady=10, padx=10, ipadx=100, ipady=20)

        # # create a query button
        # qury_btn = Button(self, text="Show Records", command=self.query)
        # qury_btn.grid(row=9, column=0, columnspan=2, pady=10, padx=10, ipadx=137)
        #
        # # create a delete button
        # delet_btn = Button(self, text="Delete A Record", command=self.delete)
        # delet_btn.grid(row=8, column=0, columnspan=2)

        # navigate to pages
        # page_one = Button(self, text="Page One", command=lambda: controller.show_frame(PageOne))
        # page_one.grid()
        # page_two = Button(self, text="Page Two", command=lambda: controller.show_frame(PageTwo))
        # page_two.grid()
        # This adds a folder to bucket/DB to store photos for each signing up users


    # # Create a folder in the aws database/ bucket named mosibucket1
    # def createFolderInBucket(self, username):
    #     s3 = boto3.client('s3',
    #                       aws_access_key_id=access_key_id,
    #                       aws_secret_access_key=secret_access_key,
    #                       region_name='us-east-2'
    #                       )
    #     bucket_name = "mosibucket1"
    #     directory_name = username  # it's name of your folders
    #     s3.put_object(Bucket=bucket_name, Key=(directory_name + '/'))
    #
    #create a storage of pjotos called s3 bucket at s3 database

    # def deleteFolderInBucket(self, username):
    #     s3 = boto3.resource('s3',
    #                         aws_access_key_id=access_key_id,
    #                         aws_secret_access_key=secret_access_key,
    #                         region_name='us-east-2'
    #                         )
    #     bucket = s3.Bucket('mosibucket1')
    #     bucket.objects.filter(Prefix=username + '/').delete()

    def createBucket(self, username):
        s3 = boto3.client('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name='us-east-2'
                          )
        #better to put try and error as bucket names are unique in the region and others could already took ur name
        response = s3.create_bucket(
            Bucket='mosiusersbucket-' + username,
            CreateBucketConfiguration={
                'LocationConstraint': 'us-east-2',
            },
        )

    def createFaceCollection(self, username):
        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2'
                              )
        response = client.create_collection(
            CollectionId=username
        )




    def submit(self):
        conn = _sqlite3.connect('Register.db')

        # create a cursor

        c = conn.cursor()
        result2 = ""

        if self.f_name.get == "" or self.l_name.get() == "" or self.username.get() == "" or self.password.get == "":
            result2 = "Please complete the required field!"
        else:
            c.execute("SELECT * FROM `address` WHERE `username` = ?",
                      (self.username.get(),))
            if c.fetchone() is not None:
                result2 = "Username is already taken"
            else:
                c.execute("INSERT INTO address VALUES(:f_name, :l_name, :username, :password)",

                          {
                              'f_name': self.f_name.get(),
                              'l_name': self.l_name.get(),
                              'username': self.username.get(),
                              'password': self.password.get()

                          }
                          )

                # Create a folder in the aws database/ bucket named mosibucket1
                self.createBucket(self.username.get())
                # create a collection to store faces
                self.createFaceCollection(self.username.get())


        # create a confirmation label

        lbl_result = Label(self, text=result2)
        lbl_result.grid(row=11, column=0, columnspan=2)

        ###################################################################################################################################

        # Insert Into a Table

        # commit changes
        conn.commit()

        # close connection
        conn.close()

        # clear text boxes
        self.f_name.delete(0, END)
        self.l_name.delete(0, END)
        self.username.delete(0, END)
        self.password.delete(0, END)


    # create a query function
    def query(self):
        conn = _sqlite3.connect('Register.db')

        # create a cursor

        c = conn.cursor()

        # Query the database
        c.execute("SELECT *, oid FROM address")
        records = c.fetchall()
        # print(records)

        # Loop through results
        print_records = ''
        for record in records:
            print_records += str(record[0]) + " " + str(record[1]) + \
                " " + str(record[2]) + " " + str(record[3]) + "\n"

        # creat a label records

        query_label = Label(self, text=print_records)
        query_label.grid(row=10, column=0, columnspan=2)

        # commit changes
        conn.commit()

        # close connection
        conn.close()



class deleteAccountPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self, bg='lightgreen')

        label = Label(self, text="                      Delete Account Page                            ",
                      font=("Arial Black", 20, 'bold'), bg='darkred', fg='lightyellow')
        label.grid(row=0, column=0, columnspan=2)
        label.config(font=("Times", 40, 'bold'), fg='white', bg='darkred')

        self.username = Entry(self, width=30)
        self.username.grid(row=2, column=1, padx=20)

        self.password = Entry(self, width=30, show="*")
        self.password.grid(row=3, column=1, padx=20)

        username_label = Label(self, text="Username:", font=("Times", 18), bg='lightgreen')
        username_label.grid(row=2, column=0, pady=30)

        password_label = Label(self, text="Password:", font=("Times", 18), bg='lightgreen')
        password_label.grid(row=3, column=0,pady=30)

        # create a delete button
        delet_btn = Button(self, text="Delete Account", command=self.delete)
        delet_btn.grid(row=4, column=0, columnspan=2,
                       pady=20, ipadx=40, ipady=10)

        delet_btn = Button(self, text="Back",
                           command=lambda: controller.show_frame(StartPage))
        delet_btn.grid(row=5, column=0, columnspan=2,
                       pady=20, ipadx=40, ipady=10)

        # create a query button
        qury_btn = Button(self, text="Show Records", command=self.query)
        qury_btn.grid(row=6, column=0, columnspan=2,
                      pady=10, padx=10, ipadx=137)

        # create a delete registry function
    def deleteBucket(self, username):
        s = boto3.resource('s3',
                           aws_access_key_id=access_key_id,
                           aws_secret_access_key=secret_access_key,
                           region_name='us-east-2'
                           )
        bucket = s.Bucket('mosiusersbucket-'+username)
        bucket.object_versions.delete()

        s3 = boto3.client('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name='us-east-2'
                          )
        response = s3.delete_bucket(
            Bucket='mosiusersbucket-'+username
        )

    def deleteFaceCollection(self, username):
        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2'
                              )
        response = client.delete_collection(
            CollectionId=username
        )


    def delete(self):
        # create a database or connect to one

        conn = _sqlite3.connect('Register.db')

        # create a cursor

        c = conn.cursor()

        # Delete a record
        print_results2 = ''
        if self.username.get == "" or self.password.get() == "":
            print_results2 = "Please complete the required field!"
        else:
            c.execute("DELETE from address WHERE `username` = ? and `password` = ?",
                      (self.username.get(), self.password.get()))
            # if c.fetchone() is None:
            #     print_results2 = "You Successfully deleted"
            # else:
            #     print_results2 = text = "Invalid Username or password"

            # delete the bucket folder and collection in aws database
            self.deleteFaceCollection(self.username.get())
            self.deleteBucket(self.username.get())

            self.username.delete(0, END)
            self.password.delete(0, END)

        # create label results
        lbl_result2 = Label(self, text=print_results2)
        lbl_result2.grid(row=12, column=0, columnspan=2)

        # commit changes
        conn.commit()

        # close connection
        conn.close()



    def query(self):
        conn = _sqlite3.connect('Register.db')

        # create a cursor

        c = conn.cursor()

        # Query the database
        c.execute("SELECT *, oid FROM address")
        records = c.fetchall()
        # print(records)

        # Loop through results
        print_records = ''
        for record in records:
            print_records += str(record[0]) + " " + str(record[1]) + \
                " " + str(record[2]) + " " + str(record[3]) + "\n"

        # creat a label records

        query_label = Label(self, text=print_records)
        query_label.grid(row=10, column=0, columnspan=2)

        # commit changes
        conn.commit()

        # close connection
        conn.close()


class PageTwo(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        Frame.config(self,bg='lightgreen')

        titleFrame = Frame(self)  # create empty box
        # Thin inserts topFrame to the root app
        titleFrame.pack()
        titleFrame.config(bg='lightgreen')

        topFrame = Frame(self)  # create empty box
        topFrame.pack()  # Thin inserts topFrame to the root app
        topFrame.config(bg='lightgreen')

        bottomFrame = Frame(self)
        bottomFrame.pack()
        bottomFrame.config(bg='lightgreen')

        frame3 = Frame(self)
        frame3.pack()
        frame3.config(bg='lightgreen')
        #
        # frame4 = Frame(self)
        # frame4.grid(row=4, pady=10)
        # # frame4.config(bg='lightgreen')
        #
        # frame5 = Frame(self)
        # frame5.grid(row=5, pady=10)
        # frame5.config(bg='lightblue')
        #
        # frame6 = Frame(self)
        # frame6.grid(row=6, pady=10)
        # # frame6.config(bg='lightgreen')

        l = Label(titleFrame, text="                                                 Admin Monitor                                                         ")
        l.grid(row=0)
        l.config(font=("Arial Black", 20, 'bold'),
                 bg='darkred', fg='lightyellow', justify=CENTER)

        self.currentUser = Label(titleFrame, text='')
        self.currentUser.grid(row=1)
        self.currentUser.config(font=("Times", 14,'bold'),
                                fg='green', justify=CENTER, bg='lightgreen')

        l1 = Label(topFrame, text="First Name:  ")
        l1.grid(row=1, padx=0)
        l1.config(font=("Times", 20), fg='black',bg='lightgreen')
        l2 = tk.Label(topFrame, text="Last Name:  ")
        l2.grid(row=2)
        l2.config(font=("Times", 20), fg='black',bg='lightgreen')
        l3 = tk.Label(topFrame, text="Permission: ")
        l3.grid(row=3)
        l3.config(font=("Times", 20), fg='black',bg='lightgreen')

        # make entries/ input
        self.e1 = Entry(topFrame, width=40)
        self.e1.grid(row=1, column=1, pady=10)
        self.e1.config(validate='key' ,validatecommand=(
            self.register(self.validateStr), '%P'))

        self.e2 = Entry(topFrame, width=40)
        self.e2.grid(row=2, column=1, pady=20)
        self.e2.config(validate='key', validatecommand=(
            self.register(self.validateStr), '%P'))

        self.options = tk.StringVar()
        self.e3 = tk.OptionMenu(topFrame, self.options,
                                'Employee', 'Blacklist')
        self.e3.grid(row=3, column=1, pady=10)
        self.e3.config(pady=10, padx=90, width=8, bg='lightgreen')
        self.options.set('---')

        # self.mb = Menubutton(topFrame, text="Add People")
        # self.mb.menu = Menu(self.mb)
        # self.mb["menu"] = self.mb.menu
        # self.mb.menu.add_command(
        #     label="Browse from computer", command=self.uploadFile)
        # self.mb.menu.add_command(
        #     label="Take photo from Camera", command=lambda: print("Opening camera..."))
        #
        # self.mb.grid(row=4, column=1, pady=20)
        # self.mb.config(pady=15, padx=30, width=15,font=("Calibri", 15, 'bold'))

        # delete employees button
        btnAdd = Button(topFrame,
                           text="Add Person",
                           fg="black",
                           width=15,
                           command=self.uploadFile,
                           )

        btnAdd.grid(row=4, column=1, pady=20)
        btnAdd.config(pady=15, padx=30, width=15,font=("Calibri", 15, 'bold'))

        # delete employees button
        btnDelete = Button(frame3,
                           text="Delete",
                           fg="black",
                           width=15,
                           command=self.deletePhoto,
                           )

        btnDelete.grid(row=2,column=1, sticky=tk.W, pady=4, padx=8)
        btnDelete.config(pady=10)

        # show employees photo button
        btnShowEmpPhoto = Button(frame3,
                                 text="Photo",
                                 fg="black",
                                 width=15,
                                 command=self.showEmpImage,
                                 )

        btnShowEmpPhoto.grid(row=2, column=0, sticky=tk.W, pady=4, padx=40)
        btnShowEmpPhoto.config(pady=10)

        # delet blacklist button
        btnDelete2 = Button(frame3,
                            text="Delete",
                            fg="black",
                            width=15,
                            command=self.deleteBlacklist,
                            )

        btnDelete2.grid(row=2, column=4, sticky=tk.W, pady=4, padx=8)
        btnDelete2.config(pady=10)

        # show blacklist photo button
        btnShowBlackPhoto = Button(frame3,
                                   text="Photo",
                                   fg="black",
                                   width=15,
                                   command=self.showBlackPhoto,
                                   )

        btnShowBlackPhoto.grid(row=2, column=3, sticky=tk.W, pady=4, padx=40)
        btnShowBlackPhoto.config(pady=10)

        # List of people authorized
        self.showList = Label(frame3, text=" Id   List of Employees                                                   ")
        self.showList.grid(row=0,columnspan=2, sticky="W")
        self.showList.config(font=("Calibri", 20, 'bold'),fg='white', bg='black')


        self.lboxEmpl = tk.Listbox(
            frame3, justify=LEFT, selectbackground='white', highlightbackground='white')
        self.lboxEmpl.grid(row=1,columnspan=2, sticky="W")
        self.lboxEmpl.config(font=("times", 20), bg='lightblue',
                             fg='darkred', highlightbackground='Black', width=43, height=12)
        self.lboxEmpl.curselection()

        # List of people blacklists
        self.showBlackList = Label(frame3, text=" Id     List of Blacklists                                                    ")
        self.showBlackList.grid(row=0,column=3,columnspan=2, sticky="W",padx=3 )
        self.showBlackList.config(
            font=("Calibri", 20, 'bold'), fg='white', bg='black')

        # showBlackNames=Label(frame5,text = "",anchor=W, justify=LEFT)
        # showBlackNames.grid(row=1, sticky="W")
        # showBlackNames.config(font=("times", 20),bg='lightblue',fg='darkred')
        self.lboxBlack = tk.Listbox(
            frame3, justify=LEFT, selectbackground='white', highlightbackground='white')
        self.lboxBlack.grid(row=1,column=3,columnspan=2, sticky="W", padx=3)
        self.lboxBlack.config(font=("times", 20),
                              bg='lightblue', fg='darkred', width=43, height=12)


        self.btnLogout = Button(self, text="Log out",bg='darkred', command=self.logout,
                                font = ('calibri', 10, 'bold'),
                                        foreground = 'green',)
        # btnLogout.grid(ipadx=5, ipady=10)
        self.btnLogout.place(x=775, y=12,relwidth=0.1, relheight=0.03)
        self.faceNameInBucket = []

        # read the username from tempUser file
        f = open("tempUser", "r")
        self.uname = f.readline()
        f.close()

        self.setUserName()

        #create a label to show photos
        self.theImage = Label(self,image='',bg="black", borderwidth=4, relief="groove")
        self.theImage.place(x=283, y=518, height=130, width=150)

        self.theImageB = Label(self, image='',bg='black', borderwidth=4, relief="groove")
        self.theImageB.place(x=719, y=518, height=130, width=150)

        # When program starts, after loading GUI, the list of peoplr available will be displayed on user endpoint
        self.list_faces_in_collection()

    def setUserName(self):
        f = open("tempUser", "r")
        uname = f.readline()
        self.currentUser.config(text='Hi '+uname.capitalize())
        self.btnLogout.config(text='Log out '+uname.capitalize())
        f.close()


    def logout(self):

        self.theImage.config(image='' )
        self.theImageB.config(image='')

        # log out of the previous user
        f = open("tempUser", "w")
        f.write('')

        self.controller.show_frame(StartPage)

    def getEntry(self):
        firstName = self.e1.get()
        lastName = self.e2.get()
        permission = self.options.get()
        if permission == 'Employee':
            permission = 'a'
        elif permission == 'Blacklist':
            permission = 'b'

        fileName = firstName + "_" + lastName + "_" + permission + ".jpg"

        return fileName

    def getImagePath(self, title='Select File'):
        # root.attributes("-topmost", True)
        # root.withdraw()
        file_path = filedialog.askopenfile()
        if file_path:
            return file_path.name
        else:
            return None

    def searchFaceInCollection(self, face):
        # client access for rekognition
        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2')

        # encode the image and get a response
        with open(face, 'rb') as source_image:
            source_bytes = source_image.read()


        # #  to use phot from the aws s3 storage, apply this code
        response = client.search_faces_by_image(
            CollectionId=self.uname,
            Image={'Bytes': source_bytes}
        )

        # since response is a dictionary, we can loop it
        # print(response)

        for key, value in response.items():
            if key == 'FaceMatches':  # go to facematch key of the response dictionary
                if value:  # check if faceMatch have value as list

                    if (value[0][
                            'Similarity'] > 80):  # similarity of captured image and photo at collection should be greater than 80, just to make sure it is accurate
                        print(key)
                        print("Similarity rate: ", value[0]['Similarity'],
                              "\nFace ID from collection: ", value[0]['Face']['FaceId'],
                              "\nImage ID captured photo: ", value[0]['Face']['ImageId'],
                              # "\nImage Name: ", value[0]['Face']['ExternalImageId'],    ###### note: we can put the name of the person and authorization here
                              )  # value[0] is dictionary

                        information = value[0]['Face']['ExternalImageId'].split(
                            ".")  # remove .jpg or .png

                        info = information[0].split("_")  # split the names

                        name = info[0] + " " + info[1]
                        authorization = info[2]

                        if authorization == 'a':
                            print("This Face is already registered as " +
                                  name + ' as an Employee')
                            self.notifyAdmin = "Face already registered as: \n" + \
                                'Name: ' + name + ' \nAuthority: Employee'
                            return True

                        elif (authorization == "b"):
                            print("This Face is already registered as " +
                                  name + ' as a Blacklist')
                            self.notifyAdmin = "Face already registered as: \n" + \
                                'Full Name: ' + name + ' \nAuthority: Blacklist'
                            return True

                else:  # if it is empty, then there is no simillary person
                    return False

    def upload_file(self, file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Upload the file
        client = boto3.client('s3',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2'
                              )
        try:
            response = client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def uploadFile(self,):
        s3 = boto3.client('s3',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name='us-east-2'
                          )
        imagePath = self.getImagePath()

        # Check if user exist or not
        firstName = self.e1.get()
        lastName = self.e2.get()
        fullName = firstName + " " + lastName

        # Check if same person exist on the s3 and face detected on the collection of faces
        if fullName not in self.faceNameInBucket:
            if not self.searchFaceInCollection(imagePath):
                if imagePath:  # check if selected image is not empty directory
                    faceName = self.getEntry()  # name the face in the format of firstName_lastName_a.jpg

                    with open(imagePath, "rb") as f:  # put the path of the captured image
                        # s3.upload_fileobj(f, "mosibucket1", faceName)
                        s3.upload_fileobj(f,'mosiusersbucket-'+self.uname,faceName)

                    print("Uploading Done!")

                    # afetr uploading image to bucket, then add it to collection
                    self.addPhoto(faceName)

                else:
                    print("No file selected!")
            else:
                messagebox.showerror('Person Identified',
                                     self.notifyAdmin)
                # print(searchFaceInCollection.notifyAdmin)
        else:
            print("Name Exist In our record, Please Change name")
            messagebox.showerror(
                "Invalid Name", "Name Exist In our record, Please Change Name")

        self.e1.delete(0, END)
        self.e2.delete(0, END)


    # adding faces to collection
    def add_faces_to_collection(self, bucket, photo, collection_id):
        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2'
                              )

        response = client.index_faces(CollectionId=collection_id,
                                      Image={'S3Object': {
                                          'Bucket': bucket,'Name': photo}},
                                      ExternalImageId=photo,
                                      MaxFaces=1,
                                      QualityFilter="AUTO",
                                      DetectionAttributes=['ALL'])

        print('Results for ' + photo)
        print('Faces indexed:')
        if response['FaceRecords']:
            print("Face Successfully added")
            for faceRecord in response['FaceRecords']:
                print('  Face ID: ' + faceRecord['Face']['FaceId'])
                print('  Location: {}'.format(
                    faceRecord['Face']['BoundingBox']))
                # update the list of users avilable at the user end
                self.list_faces_in_collection()
        else:
            messagebox.showerror(
                'Face not detected, Please provide clear photo!')
            print('Face not detected, Please provide clear photo!')
            for unindexedFace in response['UnindexedFaces']:
                print(' Location: {}'.format(
                    unindexedFace['FaceDetail']['BoundingBox']))
                print(' Reasons:')
                for reason in unindexedFace['Reasons']:
                    print('   ' + reason)
        return len(response['FaceRecords'])

# add face to collection
    def addPhoto(self, faceName):

        ###?????????????????????????????????????????????????????????????????????????????????????????????????????????
        f = open("tempUser", "r")
        uname = f.readline()

        bucket = 'mosiusersbucket-'+uname
        collection_id = uname
        photo = faceName

        indexed_faces_count = self.add_faces_to_collection(
            bucket, photo, collection_id)
        if indexed_faces_count != 0:
            print("Faces indexed count: " + str(indexed_faces_count))
        else:
            # ????????
            print("User already exist, not added to bucket as key for bucket is name")
            # but still added to collection as the key is different, colllection uses faceid as key so similar face will not be added bu similar name will be added

    # if __name__ == "__main__":
    #     main()

    # List photos in the collection

    # change the format of the names by removing _
    def fixNameFormat(self, name):
        n = name.split("_")
        res = n[0] + " " + n[1]
        return res

    # check the authotization
    def checkAuthorization(self, name):
        n = name.split(".")
        aut = n[0]

        if aut.endswith('a'):
            return True
        else:
            return False

    def downloadImageFromS3(self, img, imgName):
        s3 = boto3.resource('s3', aws_access_key_id=access_key_id,
                            aws_secret_access_key=secret_access_key,
                            region_name='us-east-2')

        s3.Bucket('mosiusersbucket-'+self.uname).download_file(img, imgName)

    def showEmpImage(self):
        if self.lboxEmpl.curselection():
            index = self.lboxEmpl.curselection()[0]

            folderPath = r'images'
            img_size = (200, 200)
            path = folderPath + '/' + 'imgE.jpg'

            #  face key to to be searched
            f = self.bucketKeysEmp[index]

            # download the images
            self.downloadImageFromS3(f, path)

            openImg = Image.open(path)
            openImg.thumbnail(img_size, Image.ANTIALIAS)
            img = ImageTk.PhotoImage(openImg)
            self.theImage.config(image=img)
            self.theImage.image = img

            # self.theImage.place(x=282, y=476, height=130, width=150)
        else:
            messagebox.showerror('Name Not Selected',
                                 'Select person from the list')



    def showBlackPhoto(self):
        if self.lboxBlack.curselection():
            index = self.lboxBlack.curselection()[0]

            folderPath = r'images'

            img_size = (200, 200)
            # path=folderPath+'/'+fileNames[index]
            path = folderPath + '/' + 'imgB.jpg'

            #  face key to to be searched
            f = self.bucketKeysBlack[index]

            # download the images
            self.downloadImageFromS3(f, path)

            openImg = Image.open(path)
            openImg.thumbnail(img_size, Image.ANTIALIAS)
            img = ImageTk.PhotoImage(openImg)
            self.theImageB.config(image=img)
            self.theImageB.image = img
            # self.theImageB.place(x=718, y=476, height=130, width=150)
        else:
            messagebox.showerror('Name Not Selected',
                                 'Select person from the list')



    def list_faces_in_collection(self):

        #read the current user's username
        f = open("tempUser", "r")
        self.uname = f.readline()
        f.close()

        collection_id = self.uname

        maxResults = 2
        faces_count = 0
        blacklist_count = 0
        tokens = True

        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2')

        if collection_id:

            response = client.list_faces(CollectionId=collection_id,
                                         MaxResults=maxResults)

            print('Faces in collection ' + collection_id)

            listOfPeople = ''
            blacklists = ''

            # this list will be used in upload function to make sure the same name doesn't exist in the bucket
            self.faceNameInBucket=[]
            # this stores the names/keys in s3 bucket in the format of Musie_Yemane_a.jpg
            self.bucketKeysEmp = []
            self.bucketKeysBlack = []

            # initiate a list to collect list of ID printed from 1 to ---
            self.faceID = []  # This is a normal list, we use function.listname name to make the list accessible by others
            # for black listed people to store their faceid to help us to delete them by id
            self.faceID2 = []
            c = 1
            # make the list boxes empty before loading updated data
            self.lboxEmpl.delete(0, END)
            self.lboxBlack.delete(0, END)
            while tokens:

                faces = response['Faces']
                for face in faces:
                    print(face)
                    tempName1 = 'empImages/' + str(c) + '.jpg'
                    tempName2 = 'blackImages/' + str(c) + '.jpg'
                    c = c + 1

                    # check if the face is employee or blacklisted
                    autho = self.checkAuthorization(face['ExternalImageId'])
                    # removes the _ and make the correct names
                    FullName = self.fixNameFormat(face['ExternalImageId'])

                    self.faceNameInBucket.append(
                        FullName)  # This is to check if user with same name already registered in our record at the user creation

                    if autho:
                        self.lboxEmpl.insert(
                            tk.END, '  ' + str(faces_count + 1) + '.     ' + FullName)

                        self.bucketKeysEmp.append(face[
                            'ExternalImageId'])  # public list that stores the employees names/keys used in s3 bucket. eg Musie_Yemane_a.jpg

                        listOfPeople = listOfPeople + "\n" + "  " + \
                            str(faces_count + 1) + "     " + FullName
                        self.faceID.append(face['FaceId'])
                        faces_count += 1
                    else:

                        self.lboxBlack.insert(
                            tk.END, '  ' + str(blacklist_count + 1) + '.     ' + FullName)

                        self.bucketKeysBlack.append(face[
                            'ExternalImageId'])  # public list that stores the blacklisted names/keys used in s3 bucket. eg Musie_Yemane_a.jpg

                        blacklists = blacklists + "\n" + "  " + \
                            str(blacklist_count + 1) + "     " + FullName
                        self.faceID2.append(face['FaceId'])
                        blacklist_count += 1

                if 'NextToken' in response:
                    nextToken = response['NextToken']
                    response = client.list_faces(CollectionId=collection_id,
                                                 NextToken=nextToken, MaxResults=maxResults)
                else:
                    tokens = False


    # Delete photo from the bucket s3 amazon database, it uses the image name as key eg. Musie_Yemane_a.jpg
    def deletePhotoFromBucket(self, photoKey):
        client = boto3.resource('s3',
                                aws_access_key_id=access_key_id,
                                aws_secret_access_key=secret_access_key,
                                region_name='us-east-2'
                                )

        client.Object('mosiusersbucket-'+self.uname, photoKey).delete()

    # delete photo in the collection
    def delete_faces_from_collection(self, collection_id, faces):
        client = boto3.client('rekognition',
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              region_name='us-east-2')

        response = client.delete_faces(CollectionId=collection_id,
                                       FaceIds=faces)

        print(str(len(response['DeletedFaces'])) + ' faces deleted:')
        for faceId in response['DeletedFaces']:
            print(faceId)
        return len(response['DeletedFaces'])

    def deletePhoto(self):

        if self.lboxEmpl.curselection():
            # index of selected item in listbox of employees
            index = self.lboxEmpl.curselection()[0]
            # access the faceID from list faces in collection, which contains all the IDs indexed
            faceIdToBeDeleted = self.faceID[index]

            # delete face

            collection_id = self.uname
            faces = []
            faces.append(faceIdToBeDeleted)  # deletes face from collection
            # delete photo from s3 bucket database
            self.deletePhotoFromBucket(self.bucketKeysEmp[index])

            faces_count = self.delete_faces_from_collection(
                collection_id, faces)

            print("deleted faces count: " + str(faces_count))


            # remove photo from the screen
            self.theImage.config(image='')

            # Update the lis of users sored in the bucket and collection
            self.list_faces_in_collection()

        else:
            messagebox.showerror(
                "Select a person", "Please Select Person to Delete")
            print('Person not selected!!!')

    def deleteBlacklist(self):

        if self.lboxBlack.curselection():
            # index of selected item in listbox of blacklists
            index = self.lboxBlack.curselection()[0]
            # access the faceID from list faces in collection, which contains all the IDs indexed
            faceIdToBeDeleted = self.faceID2[index]

            # delete face
            collection_id = self.uname
            faces = []
            faces.append(faceIdToBeDeleted)

            # delete photo from bucket
            self.deletePhotoFromBucket(self.bucketKeysBlack[index])

            faces_count = self.delete_faces_from_collection(
                collection_id, faces)

            print("deleted faces count: " + str(faces_count))

            # remove photo from the screen
            self.theImageB.config(image='')

            # Update the lis of users sored in the bucket and collection
            self.list_faces_in_collection()

        else:
            messagebox.showerror(
                "Select a person", "Please Select Person to Delete")
            print('Person not selected!!!')

    # validate enty to use only integers
    def validateInt(self, inp):
        if inp.isdigit():
            return True
        elif inp == "":
            return True
        else:
            return False

    # validate enty to use only alphabets
    def validateStr(self, inp):
        if inp.isalpha():
            return True
        elif inp == "":
            return True
        else:
            return False


# class PageTwo(Frame):
# 	def __init__(self, parent, controller):
# 		Frame.__init__(self, parent)
#
# 		label = Label(self, text="Page Two")
# 		label.pack(padx=10, pady=10)
# 		start_page = Button(self, text="Start Page", command=lambda:controller.show_frame(StartPage))
# 		start_page.pack()
# 		page_one = Button(self, text="Page One", command=lambda:controller.show_frame(PageOne))
# 		page_one.pack()

class MainMenu:
    def __init__(self, master):
        menubar = Menu(master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=master.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        master.config(menu=menubar)


app = App()
app.mainloop()
