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
                 last_direction=(1.0,1.0), # the direction in the x-y plane that the user is currently going
                 curr_velocity=(0.0,0.0)): # the user's velocity in each the x and y directions 
        self.joystick_control = joystick_control
        self.desired_linear_speed = desired_linear_speed
        self.curr_position = curr_position
        self.curr_velocity = curr_velocity
        self.last_direction = last_direction
        self.time_elapsed = 0
        self.last_comment = 0

    def get_response(self,i):
        global set_margin
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
                print("too fast, linear is: %f, desired speed: %f" %(linear, self.desired_linear_speed))
                print("velocity: (%f, %f)" %(velocity[0], velocity[1]))
            elif linear < self.desired_linear_speed - epsilon:
                self.last_comment = -1 # user thinks this is too slow
                print("too slow, linear is: %f, desired speed: %f" %(linear, self.desired_linear_speed))
                print("velocity: (%f, %f)" %(velocity[0], velocity[1]))
            else:
                self.last_comment = 0 # user is good
                print("good, linear is: %f, desired speed: %f" %(linear, self.desired_linear_speed))
                print("velocity: (%f, %f)" %(velocity[0], velocity[1]))
            
        # user might change their mind on direction (I don't think this should have much 
        # effect on learning, it just made it more interesting to watch drive around)
        change_direction = np.random.choice([True,False], p=[0.0,1.0])
        if change_direction:
            angle = np.random.uniform(0,2*np.pi)
            self.last_direction = (np.cos(angle),np.sin(angle))
            # set_margin = True
        # if i%(2*30) == 0:
            # print("returned value by get_response(): (%f, %f)" %(self.last_direction[0] * self.joystick_control, self.last_direction[1] * self.joystick_control))
        return (self.last_direction[0] * self.joystick_control, self.last_direction[1] * self.joystick_control, self.last_comment)
            

    def step(self, velocity, dt):
        self.time_elapsed += dt
        self.curr_velocity = velocity
        # print("current velocity in step: (%f, %f)" % velocity)
        x = self.curr_position[0] + velocity[0]*dt
        y = self.curr_position[1] + velocity[1]*dt
        
        # adjust position so it fits in grid 
        if x < xlimit[0] or xlimit[1] < x:
            x = x*-1
        if y < ylimit[0] or ylimit[1] < y:
            y = y*-1           
        
        self.curr_position = (x,y)
        # print("current position: (%f, %f)" %(x, y))
        
        return (x, y)


#------------------------------------------------------------
# set up initial state and global variables
user = RobotUsesr()
dt = 1./30 # 30 fps
velocity_history = []
set_margin = True

#------------------------------------------------------------
# set up figure and animation
fig = plt.figure()
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=xlimit, ylim=ylimit)
ax.grid()

line, = ax.plot([], [], 'o-', lw=2)
velocity_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
voice_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)

def change_vel(pos, goal):
    (pos_x, pos_y) = pos
    (goal_x, goal_y) = goal
    # theta = np.arctan((goal_y - pos_y)/(goal_x - pos_x))
    d = np.sqrt((goal_y - pos_y)**2 + (goal_x - pos_x)**2)
    cos = (goal_x - pos_x)/d
    sin = (goal_y - pos_y)/d
    return (np.abs(cos), np.abs(sin))

def find_magnitude(input_tuple):
    return np.sqrt(input_tuple[0]**2+input_tuple[1]**2)

def find_next_params(time,
                     curr_velocity, 
                     curr_pos,
                     last_direction,
                     complaint,
                     increase_vel = 2,
                     decrease_vel = 2):
    # (i_x, i_y) = change_vel(curr_pos, goal_direction)
    new_vel = curr_velocity
    epsilon = 0.05
    global low_margin_speed, high_margin_speed
    global set_margin
    # low_margin_speed = (0.0, 0.0)
    # high_margin_speed = (1.0, 1.0)
    multiply_x, multiply_y = change_vel(curr_pos, last_direction)

    if time%(2*30) == 0:
        if complaint == -1: # too slow
            # print("**** current velocity: (%f, %f)" %(curr_velocity[0], curr_velocity[1]))
            if len(velocity_history) >= 1:
                pre_vel = find_magnitude(velocity_history[-1])
                curr_vel = find_magnitude(curr_velocity)
                if curr_vel <= pre_vel and set_margin == False:
                    new_vel = ((curr_velocity[0]+high_margin_speed[0])/2, (curr_velocity[1]+high_margin_speed[1])/2)
                    # print("new vel in too slow after if: (%f, %f)" %(new_vel[0], new_vel[1]))
                else:
                    new_vel = (curr_velocity[0]*increase_vel + epsilon, curr_velocity[1]*increase_vel + epsilon)
            else:
                new_vel = (curr_velocity[0]*increase_vel + epsilon, curr_velocity[1]*increase_vel + epsilon)
                # print("new vel in else (too slow): (%f, %f)" %(new_vel[0], new_vel[1]))
            # velocity_history.append(new_vel)
        elif complaint == 1: # too fast
            if len(velocity_history) >= 1:
                pre_vel = find_magnitude(velocity_history[-1])
                curr_vel = find_magnitude(curr_velocity)
                # pre_pre_vel = find_magnitude(velocity_history[-2])
                # velocity_history[-1]
                if  curr_vel >= pre_vel:
                    if set_margin:
                        low_margin_speed = velocity_history[-2]
                        high_margin_speed = velocity_history[-1]
                        set_margin = False
                    # high_margin_speed = curr_velocity
                    # high_margin_speed = velocity_history[-1]
                    # print("low margin speed: (%f, %f)" %(low_margin_speed[0], low_margin_speed[1]))
                    # diff = pre_vel - pre_pre_vel
                    # new_vel = (curr_velocity[0]-diff/2, curr_velocity[1]-diff/2)
                    # new_vel = ((curr_velocity[0]+ velocity_history[-2][0])/2, (curr_velocity[1]+ velocity_history[-2][1])/2)
                    new_vel = ((curr_velocity[0]+ low_margin_speed[0])/2, (curr_velocity[1]+ low_margin_speed[1])/2)
                    # print("new vel in if statement: (%f, %f)" %(new_vel[0], new_vel[1]))
                else:
                    new_vel = ((curr_velocity[0]+low_margin_speed[0])/2, (curr_velocity[1]+low_margin_speed[1])/2)
                    # print("new vel in else statement: (%f, %f)" %(new_vel[0], new_vel[1]))
                    if find_magnitude(new_vel) > find_magnitude(curr_velocity):
                        print("something not right!")
                    # new_vel = (curr_velocity[0]-decrease_vel, curr_velocity[1]-decrease_vel)
            else:
                new_vel = (curr_velocity[0]/decrease_vel, curr_velocity[1]/decrease_vel)
                print("new vel for len=1: (%f, %f)" %(new_vel[0], new_vel[1]))
        else:
            new_vel = curr_velocity
    # new_vel = (new_vel[0]*multiply_x, new_vel[1]*multiply_y)
    # velocity_history.append(new_vel)
    return new_vel

def init():
    """initialize animation"""
    line.set_data([], [])
    velocity_text.set_text('')
    voice_text.set_text('')
    return line, velocity_text, voice_text

def animate(i):
    """perform animation step"""
    global user, dt, set_low_margin
    (joy_x,joy_y,complaint) = user.get_response(i)
    
    possible_last_direction = (joy_x,joy_y) # map joystick to control to motor (simple robot model assumes 1-1)
    
    # Now we know the user's complaint and joystick control. Given those, we need to 
    # learn how to make an adjustment so they will be happy
    n_velocity = find_next_params(i, user.curr_velocity, user.curr_position, possible_last_direction, complaint)


    if i%(2*30)==0:
        velocity_history.append(n_velocity)
        # print("**** current velocity: (%f, %f)" %(user.curr_velocity[0], user.curr_velocity[1]))
        # print("complaint: %s" %user_complaints[complaint+1])
        # print("---- new velocity: (%f, %f)" %(n_velocity[0], n_velocity[1]))
        # print("!! direction the user wants to go: (%f, %f)" %(joy_x, joy_y))
        # print("^^^^ current position: (%f, %f)" %(user.curr_position[0], user.curr_position[1]))
        print(velocity_history)
    # print("******", n_velocity)
    # print("------", velocity)
    # print(velocity_history)
    
    line.set_data(*user.step(n_velocity,dt)) # get user's update position and plot it 
    # line.set_data(*user.step(n_velocity,dt)) # get user's update position and plot it 
    
    velocity_text.set_text('Velocity  = %.1f, %.1f' % user.curr_velocity)
    voice_text.set_text('User: ' + user_complaints[complaint+1])
    return line, velocity_text, voice_text

# choose the interval based on dt and the time to animate one step
from time import time
from time import sleep
t0 = time()
animate(0)
sleep(5)
t1 = time()
interval = 1000 * dt - (t1 - t0)
ani = animation.FuncAnimation(fig, animate, frames=300,
                              interval=interval, blit=True, init_func=init)

plt.show()