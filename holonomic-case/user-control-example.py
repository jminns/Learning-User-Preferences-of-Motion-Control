import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# user's vocal complaints about he speed they are traviling 
user_complaints = ['This is so slow!', 'I\'m good', 'Way too fast!']

#how big is the imaginary room we're driving in?
xlimit=(-2, 2)
ylimit=(-2, 2)

class RobotUsesr:

    def __init__(self,
                 curr_position=(0, 0), # position of the user in the world
                 joystick_control=0.5, # user's ability to use the joystick (this should probably be a range, not a value)
                 desired_linear_speed=0.9, # how fast the user would like to go
                 last_direction=(1.0,0.0), # the direction in the x-y plane that the user is currently going
                 curr_velocity=(0.0,0.0)): # the user's velocity in each the x and y directions 
        self.joystick_control = joystick_control
        self.desired_linear_speed = desired_linear_speed
        self.curr_position = curr_position
        self.curr_velocity = curr_velocity
        self.last_direction = last_direction
        self.time_elapsed = 0
        self.last_comment = 0

    def get_response(self,i):
        epsilon = 0.1 # how close to perfect is good enough?
        
        # see what user has to say
        # user isn't going to be saying something at 30 fps, so restrit making comments to 
        # once every 2 seconds (we can change how often they talk, it should probably have 
        # some randomness)
        velocity = self.curr_velocity
        linear = np.sqrt(velocity[0]**2+velocity[1]**2)
        if i%(2*30) == 0:
            if linear > self.desired_linear_speed + epsilon:
                self.last_comment = 1 # user thinks this is too fast
            elif linear < self.desired_linear_speed - epsilon:
                self.last_comment = -1 # user thinks this is too slow
            else:
                self.last_comment = 0 # user is good
            
        # user might change their mind on direction (I don't think this should have much 
        # effect on learning, it just made it more interesting to watch drive around)
        change_direction = np.random.choice([True,False], p=[0.05,0.95])
        if change_direction:
            angle = np.random.uniform(0,2*np.pi)
            self.last_direction = (np.cos(angle),np.sin(angle))
            
        return (self.last_direction[0] * self.joystick_control, self.last_direction[1] * self.joystick_control, self.last_comment)
            

    def step(self, velocity, dt):
        self.time_elapsed += dt
        self.curr_velocity = velocity
        x = self.curr_position[0] + velocity[0]*dt
        y = self.curr_position[1] + velocity[1]*dt
        
        # adjust position so it fits in grid 
        if x < xlimit[0] or xlimit[1] < x:
            x = x*-1
        if y < ylimit[0] or ylimit[1] < y:
            y = y*-1           
        
        self.curr_position = (x,y)
        
        return (x, y)


#------------------------------------------------------------
# set up initial state and global variables
user = RobotUsesr()
dt = 1./30 # 30 fps

#------------------------------------------------------------
# set up figure and animation
fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=xlimit, ylim=ylimit)
ax.grid()

line, = ax.plot([], [], 'o-', lw=2)
velocity_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
voice_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)

def init():
    """initialize animation"""
    line.set_data([], [])
    velocity_text.set_text('')
    voice_text.set_text('')
    return line, velocity_text, voice_text

def animate(i):
    """perform animation step"""
    global user, dt
    (joy_x,joy_y,complaint) = user.get_response(i)
    
    velocity = (joy_x,joy_y) # map joystick to control to motor (simple robot model assumes 1-1)
    
    # Now we know the user's complaint and joystick control. Given those, we need to 
    # learn how to make an adjustment so they will be happy
    
    line.set_data(*user.step(velocity,dt)) # get user's update position and plot it 
    
    velocity_text.set_text('Velocity  = %.1f, %.1f' % user.curr_velocity)
    voice_text.set_text('User: ' + user_complaints[complaint+1])
    return line, velocity_text, voice_text

# choose the interval based on dt and the time to animate one step
from time import time
t0 = time()
animate(0)
t1 = time()
interval = 1000 * dt - (t1 - t0)

ani = animation.FuncAnimation(fig, animate, frames=300,
                              interval=interval, blit=True, init_func=init)

plt.show()