from models.bfs_player import AiPlayer

from models.human_player import HumanPlayer

class PlayerFactory:

    def getPlayer(self, playerType: str):
        print(playerType)
        if playerType == "human":
            return HumanPlayer()
        elif playerType == "ai":
            return AiPlayer()
        else:
            raise ValueError(f"{playerType} you should use either AI or Human")
