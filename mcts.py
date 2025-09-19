import math
import random

WIN_LINES = [
    [(0,0),(0,1),(0,2)],  # rows
    [(1,0),(1,1),(1,2)],
    [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)],  # cols
    [(0,1),(1,1),(2,1)],
    [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)],  # diagonals
    [(0,2),(1,1),(2,0)]
]

class GameBoard:

    def __init__(self):

        self.entries = [[0, 0, 0], [0, 0, 0], [0, 0 ,0]]
        
    def print_bd(self):

        for i in range(3):
            for j in range(3):
                print(self.entries[i][j],end='')
            print('')

    def checkwin(self) -> int:
        
        for line in WIN_LINES:
            vals = [self.entries[r][c] for r,c in line]
            if vals == [1, 1, 1]:   
                return 1
            if vals == [2, 2, 2]:
                return 2
            
        if any(0 in row for row in self.entries):
            return 0

        return 3
    
    def check_nextplayer(self, bd = None):
        count_1 = sum(cc == 1 for row in bd for cc in row)
        count_2 = sum(cc == 2 for row in bd for cc in row)
        return 1 if count_1 == count_2 else 2
    
    def getmoves(self):
        return [(r,c) for r in range(3) for c in range(3) if self.entries[r][c]==0] # all possible position where the board is empty
    
    def copy(self):
        new_board = GameBoard()
        new_board.entries = [row[:] for row in self.entries]
        return new_board
    
class MCTSNode:
    def __init__(self, bd: GameBoard, parent: None, action: None):
        self.bd = bd             
        self.parent = parent
        self.action = action # action that led to this node          
        self.children = [] # list of child nodes
        self.possible_moves = bd.getmoves()  # moves that can be played from this node
        self.visits = 0
        self.wins = 0.0         

    def is_fully_expanded(self):
        return len(self.possible_moves) == 0
    
    def is_terminal(self):
        return self.bd.checkwin() != 0
    
def apply_action(bd:GameBoard, action, player):
        r,c = action        
        new_bd = bd.copy()
        new_bd.entries[r][c] = player
        return new_bd

class MCTS:
    def __init__(self, c = math.sqrt(2)):
        self.c = c

    
    def uct_select(self, node:MCTSNode, c = None) -> MCTSNode:
        # node: current node
        # return: child node with highest UCT value
        if c is None:
            c = self.c
        return max(node.children, key=lambda child: (child.wins / child.visits) + c*math.sqrt(math.log(node.visits)/child.visits))

    def expand(self, node:MCTSNode) -> MCTSNode:
        # node: current node
        # return: new child node after applying one of the possible moves

        action = node.possible_moves.pop()
        r,c = action

        child_bd = node.bd.copy()
        player = child_bd.check_nextplayer(child_bd.entries)
        child_bd = apply_action(child_bd, action, player)

        child_node = MCTSNode(child_bd, parent=node, action = action)
        node.children.append(child_node)
        return child_node
    
    def rollout(self,bd:GameBoard) -> int:
        # bd: current board
        # return: score on the same (+1: for winner player)
        
        rollout_bd = bd.copy()

        while rollout_bd.checkwin() == 0:
            next_player = rollout_bd.check_nextplayer(rollout_bd.entries)
            actions = rollout_bd.getmoves()
            if not actions:
                break
            action =random.choice(actions)
            rollout_bd = apply_action(rollout_bd, action, next_player)
        
        winner = rollout_bd.checkwin()
        if winner ==1 or winner ==2:
            return +1
        else:
            return 0
        
    def backpropagate(self, node:MCTSNode, reward:int):
        current = node
        while current is not None:
            current.visits += 1
            current.wins += reward
            # switch perspective
            reward = -reward

            #propagate to parent
            current = current.parent
    
    def search(self,root:MCTSNode, iter = 2000):
        # based on the rood board, run MCTS and return the best action
        #root = MCTSNode(root_bd, parent=None, action=None)
        root_bd = root.bd
        if root_bd.checkwin() != 0:
            raise ValueError("Game is over")
        
        for _ in range(iter):
            node = root

            # selection
            while (not node.is_terminal()) and node.is_fully_expanded():
                node = self.uct_select(node, c= self.c)
            
            # expansion
            if (not node.is_terminal()) and (not node.is_fully_expanded()):
                node = self.expand(node)

            # simulation 
            reward = self.rollout(node.bd)

            # backpropagation
            self.backpropagate(node, reward)
        self.c = 0
        best_child = self.uct_select(root,c=0)
        return best_child.action

    

def MCTS_move(root_state: GameBoard, iterations=2000):
    mcts = MCTS()
    root_node = MCTSNode(bd = root_state, parent= None, action=None)
    
    best_action = mcts.search(root_node, iter=iterations)
    player = root_state.check_nextplayer(root_state.entries)
    next_state = apply_action(root_state, best_action, player)
    
    return best_action, player, next_state


# bd = GameBoard()
# print('-------- before move ----------')
# bd.entries = [[1,0,0],[0,2,0],[0,0,0]]
# bd.print_bd()
# print('-------- after MCTS move ----------')
# best_action, next_player, next_bd = MCTS_move(bd, iterations=1000)
# print("Best action:", best_action, "for player", next_player)
# next_bd.print_bd()
# print('----------------------------------')

def get_x_o_input():
    while True:
        user_input = input("Would you like to be X or O? (Enter X or O, no spaces, uppercase)")
        if user_input == 'X' or user_input == 'O':
            return user_input
        else:
            print("Your input was not correct. Read carefully how to input.")

valid_moves = ['0,0', '0,1', '0,2',
               '1,0', '1,1', '1,2',
               '2,0', '2,1', '2,2']

def get_player_move(previously_played):
    valid_input = False
    while valid_input == False:
        print("Human, please choose a space!")
        user_input = input("Enter two numbers separated by a comma: ")
        if user_input not in previously_played:
            if user_input in valid_moves:
                humanrow, humancol = map(int, map(str.strip, user_input.split(',')))
                previously_played.append(user_input)
                valid_input = True
            else:
                print("You did not input a valid move.")
                continue
        else: 
            print("That move has already been played. Pick another move.")
            continue

    return humanrow, humancol
    

def game_loop():
    previously_played = []
    x_o_value = get_x_o_input()
    human_value = 1 if x_o_value == 'X' else 2
    mcts_value = 2 if x_o_value == 'X' else 1

    bd = GameBoard()
    current_player = 1

    while True:
        bd.print_bd()


        if bd.checkwin() != 0:
            print("Game over")
            if bd.checkwin() == 1:
                if human_value == 1:
                    print("Human Player Wins!")
                else: 
                    print("MCTS Wins!")
            elif bd.checkwin() == 2:
                if human_value == 1:
                    print("MCTS Wins!")
                else:
                    print("Humaan Player Wins!")
            else:
                print("It's a Draw!")  
                
            break

        if current_player == human_value:
            print("It is your move.")
            row, col = get_player_move(previously_played)
            bd.entries[row][col] = human_value

        else:
            print("MCTS is making a move")
            best_action, player, next_board = MCTS_move(bd.copy(),iterations=2000)
            row, col = best_action
            bd.entries[row][col] = mcts_value

        if current_player == human_value:
            current_player = mcts_value
        else:
            current_player = human_value

mcts = MCTS()


while True:
    game_loop()
    quit_game = input("To quit playing, type 'Quit', otherwise hit enter to start a new game.")
    if quit_game == 'Quit':
        break
    else:
        continue


