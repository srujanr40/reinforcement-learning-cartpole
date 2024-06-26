import gymnasium as gym
import numpy as np


class QLearning:
    def __init__(self, env, alpha, gamma, epsilon, numberOfEpisodes, numberOfBins, lowerBounds, upperBounds):
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon 
        self.numberOfActions = env.action_space.n 
        self.numberOfEpisodes = numberOfEpisodes
        self.numberOfBins = numberOfBins
        self.lowerBounds = lowerBounds
        self.upperBounds = upperBounds

        # rewards sum per episode
        self.sumEpisodeRewards=[]
        
        self.Qmatrix=np.random.uniform(low=0, high=1, size=(numberOfBins[0],numberOfBins[1],numberOfBins[2],numberOfBins[3],self.numberOfActions))
        #self.Kmatrix=np.ones(shape = (numberOfBins[0],numberOfBins[1],numberOfBins[2],numberOfBins[3],self.numberOfActions), dtype=int)

    # convert continuous values of the state into discrete values for Q-learning
    def getDiscreteState(self, state):
        position = state[0]
        velocity = state[1]
        angle = state[2]
        angularVelocity = state[3]

        # creating discrete bins for the continuous state space
        cartPositionBin = np.linspace(self.lowerBounds[0],self.upperBounds[0],self.numberOfBins[0])
        cartVelocityBin = np.linspace(self.lowerBounds[1],self.upperBounds[1],self.numberOfBins[1])
        poleAngleBin = np.linspace(self.lowerBounds[2],self.upperBounds[2],self.numberOfBins[2])
        poleAngularVelocityBin = np.linspace(self.lowerBounds[3],self.upperBounds[3],self.numberOfBins[3])

        # get indexs of the bins to which the continuous variables belong to
        indexPosition = np.maximum(np.digitize(position, cartPositionBin)-1,0)
        indexVelocity = np.maximum(np.digitize(velocity, cartVelocityBin)-1,0)
        indexAngle = np.maximum(np.digitize(angle, poleAngleBin)-1,0)
        indexAngularVelocity = np.maximum(np.digitize(angularVelocity, poleAngularVelocityBin)-1,0)

        return (indexPosition, indexVelocity, indexAngle, indexAngularVelocity)

    
    def selectAction(self, state, episodeNumber):

        # enabling random actions for exploration
        if episodeNumber < 500:
            return np.random.choice(self.numberOfActions)
        # eventually decreasing the value for epsilon to make the algorithm more greedy
        elif episodeNumber > 7000:
            self.epsilon = 0.999 * self.epsilon
        
        randomNumber = np.random.random()
        discreteState = self.getDiscreteState(state)

        if randomNumber < self.epsilon:
            return np.random.choice(self.numberOfActions)
        else:
            # select an action such that the Q-value for that action, state pair is the highest possible value in that state
            # np.max(self.Qmatrix[discreteState]))[0] -- will return a list of actions, as there could be multiple possible max actions
            return np.random.choice(np.where(self.Qmatrix[discreteState] == np.max(self.Qmatrix[discreteState]))[0])


    # simulating episodes with Q-learning
    def runEpisodes(self):
        for episodeIndex in range(self.numberOfEpisodes):

            state_S, _ = self.env.reset()
            state_S = list(state_S)

            episodeRewards = []

            print("Episode: ", episodeIndex)

            terminal_state = False
            for _ in range(500):
                state_S_discrete = self.getDiscreteState(state_S)
                action_a = self.selectAction(state_S, episodeIndex)

                state_S_prime, reward, terminal_state, _, _ = self.env.step(action_a)
                episodeRewards.append(reward)

                state_S_prime = list(state_S_prime)
                state_S_prime_discrete = self.getDiscreteState(state_S_prime)

                Q_max = np.max(self.Qmatrix[state_S_prime_discrete])

                if not terminal_state:
                    # update Q-values for non-terminal states
                    diff = reward + self.gamma*Q_max - self.Qmatrix[state_S_discrete + (action_a, )]
                    self.Qmatrix[state_S_discrete + (action_a, )] += self.alpha*diff
                else:
                    diff = reward - self.Qmatrix[state_S_discrete + (action_a, )]
                    self.Qmatrix[state_S_discrete + (action_a, )] += self.alpha*(reward - self.Qmatrix[state_S_discrete + (action_a, )])
                
                state_S = state_S_prime

                if terminal_state:
                    break
            
            
            print("Rewards: ", np.sum(episodeRewards))
            self.sumEpisodeRewards.append(np.sum(episodeRewards))

        
    # final optimal policy using the Q-matrix generated by running Q-learning
    def runOptimalPolicy(self):
        print("Running optimal policy")
        env1 = gym.make('CartPole-v1', render_mode='human')
        curr_state, _ = env1.reset()
        env1.render()

        timeSteps = 1000

        for timeIndex in range(timeSteps):
            print("TimeStep:", timeIndex)
            curr_state_discrete = self.getDiscreteState(curr_state)
            # np.max(self.Qmatrix[discreteState]))[0] -- will return a list of actions, as there could be multiple possible max actions
            optimal_action = np.random.choice(np.where(self.Qmatrix[curr_state_discrete] == np.max(self.Qmatrix[curr_state_discrete]))[0])

            curr_state, reward, terminated, _, _ = env1.step(optimal_action)

            if (terminated):
                print(terminated)
                break
    


env=gym.make('CartPole-v1')
state, _ = env.reset()

# bounds and bins
upperBounds=env.observation_space.high
lowerBounds=env.observation_space.low

upperBounds[1] = 3
upperBounds[3] = 10
lowerBounds[1] =- 3
lowerBounds[3] =- 10

num_bins = [30, 30, 30, 30]

# Q-learning parameters
alpha = 0.1
gamma = 1
epsilon = 0.2
numberOfEpisodes = 20000


Q = QLearning(env, alpha, gamma, epsilon, numberOfEpisodes, num_bins, lowerBounds, upperBounds)


Q.runEpisodes()


Q.runOptimalPolicy()

