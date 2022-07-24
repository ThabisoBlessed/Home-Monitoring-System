from flask import render_template, request, Response, redirect, flash, url_for,session
from application import app,socketio,join_room
import sqlite3
from sqlite3 import Error
from application.forms import SignIn, SignUp
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import RPi.GPIO as GPIO                 
import time      
import cv2
import dht11


TRIG = 16                                  
ECHO = 20

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)      

templateData =0

GPIO.setup(TRIG,GPIO.OUT)                  
GPIO.setup(ECHO,GPIO.IN)

           
t=datetime.datetime.now().__str__()

flame='no flame'

db = None
app.config["SECRET_KEY"] = "12345678"


# Define actuators GPIOs
motorIn1 = 2
motorIn2 = 3
motorIn3 = 17
motorIn4 = 27
#initialize GPIO status variables
motorIn1Sts = 0
motorIn2Sts = 0
motorIn3Sts = 0
motorIn4Sts = 0
distance=0


# Define motor controller pins as output
GPIO.setup(motorIn1, GPIO.OUT)   
GPIO.setup(motorIn2, GPIO.OUT) 
GPIO.setup(motorIn3, GPIO.OUT)
GPIO.setup(motorIn4, GPIO.OUT) 
# turn motor controller pins OFF 
GPIO.output(motorIn1, GPIO.LOW)
GPIO.output(motorIn2, GPIO.LOW)
GPIO.output(motorIn3, GPIO.LOW)
GPIO.output(motorIn4, GPIO.LOW)

instance = dht11.DHT11(pin=19)
channel = 21
PIR_input = 26
GPIO.setup(channel, GPIO.IN)
GPIO.setup(PIR_input, GPIO.IN)

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    
    signin = SignIn()
    email = signin.email.data
    password = signin.password.data
    

    if signin.validate_on_submit():
        db = sqlite3.connect("hms.db")
        cur = db.cursor()
        cur.execute("select * from users where email=? ;", [email])
        data = cur.fetchone()
        
        if signin.email.data == data[4] and check_password_hash(
                data[5], password):
            db.close()
            session['email']=signin.email.data
            session['username']=data[3]
            return redirect("/video")
        else:
            flash("Incorrect logins.", "danger")
    return render_template("login.html", signin=signin, login=True)

def callback(channel):
    flame='flame detected'
    
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(channel, callback)


mot='nothing'
@app.route("/sensor")
def sensor():
    username=session['username']
    result = instance.read()
    if(GPIO.input(PIR_input)):
        mot ='motion detected'
        
    else:
        mot='no motion detected'
        time.sleep(6)
  

    templateData = {
        'date'  : datetime.datetime.now().__str__(),
        'temp'  : result.temperature,
        'hum'  : result.humidity,
        'mot'  : mot,
        'flame':flame,
    }

    return render_template('sensor.html',username=username,**templateData )

@app.route("/display")
def display():
    username=session['username']
    return render_template('display.html',username=username )

@app.route("/chat")
def chat():
    username=session['username']
    room=1
    messages=get_messages()
    return render_template('chat.html',messages=messages,username=username ,room=room)



@app.route("/get_messages") 
def get_messages():
    
    
    try:
        db = sqlite3.connect("hms.db")
        cur = db.cursor()
        res = cur.execute('select * from  messages')
        data =res.fetchall()
        db.commit()
        db.close()  

        return data
    except Error as e:
        print(e)
        flash(e, "danger")

@app.route("/settings, methods=['GET', 'POST']")
def settings():
    username=session['username']
    return render_template('settings.html',username=username)



@app.route("/logout")
def logout():
    session['email']=False
    session['username']=False
    return redirect(url_for('index'))

@app.route("/register", methods=['POST', 'GET'])
def register():
    if session.get('email'):
        return redirect(url_for('index'))
    signup = SignUp()

    if signup.validate_on_submit():

        try:
            accid = signup.accid.data
            email = signup.email.data
            password = signup.password.data
            fname = signup.fname.data
            lname = signup.lname.data
            username = fname + '_' + lname
            #encrypting the password
            psscode = generate_password_hash(password)
            try:
                db = sqlite3.connect("hms.db")
                cur = db.cursor()
                cursor = cur.execute('SELECT max(id) FROM users')
                id = cursor.fetchone()[0]
                id = id + 1

                cur.execute(
                    "insert into users(id,firstname,lastname,username,email,password,accid)values(?,?,?,?,?,?,?)",
                    (id, fname, lname, username, email, psscode, accid))
                print('after')
                db.commit()
                flash("You are successfully registered!", "success")
                db.close()
                return redirect(url_for('video'))
            except Error as e:
                flash(e, "danger")

        except:
            flash("Error in Insert Operation", "danger")

    else:
        print(signup.errors)

    return render_template("register.html", signup=signup, register=True)


def gen():
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) 
    cam.set(4, 480) 
    face_id = input('\n enter user id end press <return> ==>  ')
    count = 0
        
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces =face_detector.detectMultiScale(gray, 1.3, 5)
        

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            count += 1
        #Take 20 face sample and stop video
        if count >= 20: 
            break
        print(count)
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()

        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



def video_gen():
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) 
    cam.set(4, 480) 
        
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces =face_detector.detectMultiScale(gray, 1.3, 5)
        

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            
       
        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()

        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route("/video", methods=['GET', 'POST'])
def video():
  
    
    templateData = {
            'motorIn1'  : motorIn1Sts,
            'motorIn2'  : motorIn2Sts,
            'motorIn3'  : motorIn3Sts,
            'motorIn4'  : motorIn4Sts,
        }
        
    
    username=session['username']
    room=1 
    if not session.get('email'):
        return redirect(url_for('login'))

    return render_template("video.html",username=username,**templateData,login=True)

@app.route("/forward")
def forward():
    distance= getDistance()
    
    print(distance)
    
    if distance> 10.34:
        GPIO.output(motorIn1, GPIO.HIGH)
        GPIO.output(motorIn2, GPIO.LOW)
        GPIO.output(motorIn3, GPIO.HIGH)
        GPIO.output(motorIn4, GPIO.LOW)
        motorIn1Sts = GPIO.input(motorIn1)
        motorIn2Sts = GPIO.input(motorIn2)
        motorIn3Sts = GPIO.input(motorIn3)
        motorIn4Sts = GPIO.input(motorIn4)
        print(9999)
    return("nothing")
    
 
    
    

@app.route("/reverse")
def reverse():
    distance= getDistance()
    print(distance)
    if distance> 10.34:
         GPIO.output(motorIn1, GPIO.LOW)
         GPIO.output(motorIn2, GPIO.HIGH)
         GPIO.output(motorIn3, GPIO.LOW)
         GPIO.output(motorIn4, GPIO.HIGH)

    return("nothing")
         
    
@app.route("/right")
def right():
    distance= getDistance()
    print(distance)
    
    if distance> 10.34:
        GPIO.output(motorIn1, GPIO.LOW)
        GPIO.output(motorIn2, GPIO.LOW)
        GPIO.output(motorIn3, GPIO.HIGH)
        GPIO.output(motorIn4, GPIO.LOW)
    return("nothing")

@app.route("/left")
def left():
    distance= getDistance()
    print(distance)
    if distance> 10.34:
        GPIO.output(motorIn1, GPIO.HIGH)
        GPIO.output(motorIn2, GPIO.LOW)
        GPIO.output(motorIn3, GPIO.LOW)
        GPIO.output(motorIn4, GPIO.LOW)
    return("nothing")

@app.route("/stop")
def stop():
    GPIO.output(motorIn1, GPIO.LOW)
    GPIO.output(motorIn2, GPIO.LOW)
    GPIO.output(motorIn3, GPIO.LOW)
    GPIO.output(motorIn4, GPIO.LOW)
    return("nothing")
    


@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/videopage_feed')
def videopage_feed():
    return Response(video_gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

   
@socketio.on('send_message')
def handle_send_message_event(data):
    print(999)
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))                                                          
    insert_messages(data['message'] ,data['username'])
    socketio.emit('receive_message', data, room=data['room'])


def insert_messages(message ,sender):
    try:
        
        
        db = sqlite3.connect("hms.db")
        
        cur = db.cursor()
        cursor = cur.execute('SELECT max(id) FROM messages')
        id = cursor.fetchone()[0]
        if id ==None:
            id=0
        print(id)
        id = id + 1
        print('hie1')
        cur.execute(
            "insert into messages(id  ,message ,date ,sender)values(?,?,?,?)",
            (id,message ,t,sender))
        db.commit()
        db.close()
        print(e)
                
    except Error as e:
        print(e)

        flash(e, "danger")
        

    except:
        flash("Error in Insert Operation", "danger")

    




@socketio.on('join_room')
def handle_join_room_event(data):
    print(data['username'],data['room'])
    app.logger.info("{} has joined the room {}".format(data['username'],data['room']))
    join_room(data['room'])
    
    socketio.emit('join_room_announcement',data)

    #Get distance from HC-SR04 
def getDistance():
  GPIO.output(TRIG, GPIO.LOW)                 
  time.sleep(1)                            

  GPIO.output(TRIG, GPIO.HIGH)                  
  time.sleep(0.00001)                      
  GPIO.output(TRIG, GPIO.LOW)

  #When the ECHO is LOW, get the purse start time
  while GPIO.input(ECHO)==0:                
    pulse_start = time.time()               
  
  #When the ECHO is HIGN, get the purse end time
  while GPIO.input(ECHO)==1:               
    pulse_end = time.time()                 

  #Get pulse duration time
  pulse_duration = pulse_end - pulse_start 
  #Multiply pulse duration by 17150 to get distance and round
  distance = pulse_duration * 17150        
  distance = round(distance, 2)
  
 
 
  return distance

