def calculate_optimal_team(slots, max_cost, exclusion_list=[], inclusion_list=[],
    scores=[], sals=[], names=[]):
    import numpy as np
    sals = (sals/100000).round(0).astype(int)
    slots += 1
    max_cost += 1
    if len(exclusion_list) > 0:
        for name in exclusion_list:
            index = np.argwhere(names == name)
            scores = np.delete(scores, index)
            sals = np.delete(sals, index)
            names = np.delete(names, index)
    if len(inclusion_list) > 0:
        for name in inclusion_list:
            print(name)
            index = np.argwhere(names == name)
            max_cost -= sals[index].flatten().tolist()[0]
            scores = np.delete(scores, index)
            sals = np.delete(sals, index)
            names = np.delete(names, index)
            slots -= 1
    players = len(names)
    mat = (players, max_cost, slots)
    value_matrix = np.zeros(mat)
    for i in range(players):
        for j in range(max_cost):
            for k in range(slots):
                if (sals[i] > j) or (1 > k):
                    value_matrix[i][j][k] = value_matrix[i-1][j][k]
                else:
                    value_matrix[i][j][k] = max(value_matrix[i-1][j][k],
                                                  scores[i] + value_matrix[i-1][j - sals[i]][k-1])

    playerIndex = players-1
    currentCost = -1
    currentSlot = -1
    bestValue = -1

    marked = np.zeros(value_matrix.size)

    for j in range(max_cost):
        for k in range(slots):
            value = value_matrix[playerIndex][j][k]
            if (bestValue == -1) or (value > bestValue):
                currentCost = j
                currentSlot = k
                bestValue = value

    while (playerIndex >= 0 and currentCost >= 0 and currentSlot >= 0):
        if (((playerIndex == 0) & (value_matrix[playerIndex][currentCost][currentSlot] > 0)) or
           (value_matrix[playerIndex][currentCost][currentSlot] != value_matrix[playerIndex - 1][currentCost][currentSlot])):
            marked[playerIndex] = 1
            currentCost -= sals[playerIndex]
            currentSlot -= 1
        playerIndex -= 1

    optimal_players = names[np.argwhere(marked > 0)].flatten().tolist()
    for name in inclusion_list:
        print(optimal_players)
        optimal_players.append(name)
        print(optimal_players)
    return optimal_players
