import numpy as np

#how big is the imaginary room we're driving in?
xlimit=(-2, 2)
ylimit=(-2, 2)

class RobotUser:

    def __init__(self,
                 joystick_control=0.7, # user's max ability to use the joystick (this should probably be a range, not a value)
                 last_control = (0.0,0.0), # the users current joystick direction (in unit vectors)
                 desired_linear_speeds=(0.9, -0.5), # how fast the user would like to go (forward, backward) [We might add rotational later, if we have time] 
                 ):
        self.joystick_control = joystick_control
        self.last_control = last_control
        self.desired_linear_speeds = desired_linear_speeds
        self.time_elapsed = 0
        self.last_comment = 0


    def get_response(self,i,curr_velocity):
        epsilon = 0.1 # how close to perfect is good enough?
        
        # see what user has to say
        # user isn't going to be saying something at 30 fps, so restrit making comments to 
        # once every 2 seconds (we can change how often they talk, it should probably have 
        # some randomness)
        linear = curr_velocity[0] # the user's velocity (linear, rotational)
        if (i+1)%(2*30) == 0:
            #see if my linear speed is a problem
            
            #If I am going forward
            if linear > 0:
                if linear > self.desired_linear_speeds[0] + epsilon:
                    self.last_comment = 1 # user thinks this is too fast
                elif linear < self.desired_linear_speeds[0] - epsilon:
                    self.last_comment = -1 # user thinks this is too slow
                else:
                    self.last_comment = 0 # user is good
            else: # I am going backwards
                if linear < self.desired_linear_speeds[1] - epsilon:
                    self.last_comment = 1 # user thinks this is too fast
                elif linear > self.desired_linear_speeds[1] + epsilon:
                    self.last_comment = -1 # user thinks this is too slow
                else:
                    self.last_comment = 0 # user is good
            #print("Speed = {}, Answer = {}".format(linear,self.last_comment))
        
            
        # user might change their mind on direction (I don't think this should have much 
        # effect on learning, it just made it more interesting to watch drive around)
        change_direction = np.random.choice([True,False], p=[0.01,0.99])
        if change_direction:
            angle = np.random.uniform(0,2*np.pi)
            self.last_control = (np.cos(angle),np.sin(angle))
            
        return (self.last_control[0] * self.joystick_control, self.last_control[1] * self.joystick_control, self.last_comment)
            

    def update(self, velocity, dt):
        self.time_elapsed += dt
        self.curr_velocity = velocity
        x = self.curr_position[0] + velocity[0]*dt
        y = self.curr_position[1] + velocity[1]*dt         
        
        self.curr_position = (x,y)
        
        return (x, y)
