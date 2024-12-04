import RPi.GPIO as GPIO
from time import sleep

def SetAngle(angle):
	duty = angle / 18 + 2
	GPIO.output(33, True)
	pwm.ChangeDutyCycle(duty)
	sleep(1)
	GPIO.output(33, False)
	pwm.ChangeDutyCycle(0)




GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)
pwm=GPIO.PWM(33, 50)
pwm.start(0)

SetAngle(60)
sleep(1)
SetAngle(0)
sleep(1)


pwm.stop()
GPIO.cleanup()
