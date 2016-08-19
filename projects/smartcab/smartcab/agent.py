import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import random

rewards_sum_record = []
debug_previous_not = 0

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.actions = (None, 'forward', 'left', 'right')



        # init q_table
        self.q_table = {
            # schema: ((light, oncoming, right, left, next_waypoint), action) -> value
        }
        directions = 'forward', 'right', 'left', None
        next_waypoints = 'forward', 'right', 'left'
        for light in 'red', 'green':
            for oncoming in directions:
                for right in directions:
                    for left in directions:
                        for next_waypoint in next_waypoints:
                            for action in self.actions:
                                self.q_table[(light, oncoming, right, left, next_waypoint), action] = random.random() * 5

        # init policy
        self.policy = {
            # schema: (light, oncoming, right, left, next_waypoint) -> action
        }
        for light in 'red', 'green':
            for oncoming in directions:
                for right in directions:
                    for left in directions:
                        for next_waypoint in next_waypoints:
                            self.policy[light, oncoming, right, left, next_waypoint] = random.choice(self.actions)



    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.previous_q_state = None
        self.previous_reward = None
        self.rewards_sum = [0]
        rewards_sum_record.append(self.rewards_sum)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        # print 'next_waypoint', self.next_waypoint
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'], inputs['oncoming'], inputs['right'], inputs['left'], self.next_waypoint)
        # print "State: ", self.state

        # TODO: Select action according to your policy
        action = self.policy[self.state]

        # Execute action and get reward
        reward = self.env.act(self, action)
        if reward < 0: self.rewards_sum[0] += reward    # add all negative rewards

        # TODO: Learn policy based on state, action, reward
        q_state = self.state, action
        self.update_q_table()

        # update policy
        self.update_policy()
        self.previous_q_state = q_state
        self.previous_reward = reward

        # print "LearningAgent.update():\n deadline = {},\n inputs = {},\n action = {},\n reward = {}".\
        # format(deadline, inputs, action, reward)  # [debug]
        print '\n'

    def update_q_table(self):
        # a very greedy, active and impatient learner,
        a = 0.5             # learning rate
        discount = 0.25
        # print "old q", q_state, self.q_table[q_state]
        if self.previous_q_state is not None:
            self.q_table[self.previous_q_state] = \
                (1 - a) * self.q_table[self.previous_q_state] + \
                a * (self.previous_reward + discount * self.get_max_q_value())
        else:
            global debug_previous_not
            debug_previous_not += 1

    def get_max_q_value(self):
        q_states = \
            (self.state, self.actions[0]), \
            (self.state, self.actions[1]), \
            (self.state, self.actions[2]), \
            (self.state, self.actions[3])
        values = (
            self.q_table[q_states[0]],
            self.q_table[q_states[1]],
            self.q_table[q_states[2]],
            self.q_table[q_states[3]]
        )
        return max(values)

    def update_policy(self):
        values = (
            self.q_table[(self.state, self.actions[0])],
            self.q_table[(self.state, self.actions[1])],
            self.q_table[(self.state, self.actions[2])],
            self.q_table[(self.state, self.actions[3])]
        )
        max_index = values.index(max(values))
        self.policy[self.state] = self.actions[max_index]
        # print 'q_state values:', values
        # print 'after updating policy', self.state, '->', self.policy[self.state]
        # print "new policy", self.policy



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    # print out rewards record to observe convergence of negative rewards
    print rewards_sum_record
    print len(rewards_sum_record), debug_previous_not

if __name__ == '__main__':
    run()
