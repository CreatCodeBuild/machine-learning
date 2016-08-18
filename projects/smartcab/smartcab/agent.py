import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import random

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.actions = (None, 'forward', 'left', 'right')
        self.q_table = {
            # schema: ((light, oncoming, right, left, next_waypoint), action) -> value
        }
        self.policy = {
            # schema: (light, oncoming, right, left, next_waypoint) -> action
        }

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        print 'next_waypoint', self.next_waypoint
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'], inputs['oncoming'], inputs['right'], inputs['left'], self.next_waypoint)
        print "State: ", self.state

        # TODO: Select action according to your policy
        # action = random.choice(self.actions)
        action = self.choose_action_from_policy()

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.update_q_table(action, reward)

        # update policy
        self.update_policy()

        print "LearningAgent.update():\n deadline = {},\n inputs = {},\n action = {},\n reward = {}".\
        format(deadline, inputs, action, reward)  # [debug]
        print '\n'

    def update_q_table(self, action, reward):
        q_state = self.state, action
        a = 0.3 # learning rate
        discount = 0.9
        if q_state in self.q_table:
            # print "old q", q_state, self.q_table[q_state]
            self.q_table[q_state] = \
                (1 - a) * self.q_table[q_state] + \
                a * (reward + discount * max(self.get_q_values(self.get_next_state()))) #???
        else:
            # print "new q state", q_state
            self.q_table[q_state] = 0.8 * random.randint(-5, 5) + 0.2 * reward

    def update_policy(self):
        if (self.state, self.actions[0]) not in self.q_table:
            self.q_table[self.state, self.actions[0]] = random.randint(-5, 5)

        if (self.state, self.actions[1]) not in self.q_table:
            self.q_table[self.state, self.actions[1]] = random.randint(-5, 5)

        if (self.state, self.actions[2]) not in self.q_table:
            self.q_table[self.state, self.actions[2]] = random.randint(-5, 5)

        if (self.state, self.actions[3]) not in self.q_table:
            self.q_table[self.state, self.actions[3]] = random.randint(-5, 5)
        values = (
            self.q_table[(self.state, self.actions[0])],
            self.q_table[(self.state, self.actions[1])],
            self.q_table[(self.state, self.actions[2])],
            self.q_table[(self.state, self.actions[3])]
        )
        max_index = values.index(max(values))
        self.policy[self.state] = self.actions[max_index]
        # print 'q_state values:', values
        print 'after updating policy', self.state, '->', self.policy[self.state]
        # print "new policy", self.policy

    def choose_action_from_policy(self):
        if self.state in self.policy:
            action = self.policy[self.state]
            print "choose policy action", action
        else:
            action = random.choice(self.actions)
            self.policy[self.state] = action
            print "choose random action", action
        return action



def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.01, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
