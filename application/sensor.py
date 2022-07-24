'''import RPi.GPIO as GPIO 
import time

pin_trigger=18
pin_echo=24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


def return_Space():

    while(True):
        #Gpio pin setup for input and outputbfor trig and echo
        GPIO.setup(pin_trigger,GPIO.OUT)
        GPIO.setup(pin_echo,GPIO.IN)
        GPIO.output(pin_trigger,False)
        #sleep for a few  seconds
        time.sleep(0.3)
        
        GPIO.output(pin_trigger,True)
        time.sleep(0.00001)
        #setting trigger pin to false before starting count
        GPIO.output(pin_trigger,False)

        while GPIO.input(pin_echo)==0:
            begin_count=time.time()
        
        while GPIO.input(pin_echo)==1:
            stop_count=time.time()
        
        
        time_taken=stop_count -begin_count
        distance=time_taken *17150
        obstacle_space=round(distance,2)
        
        
        time.sleep(2)
        return obstacle_space
    
        
        

'''