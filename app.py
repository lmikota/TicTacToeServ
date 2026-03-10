import random

from flask import Flask, request

app = Flask(__name__)

player = {}
matches = {}
available_numbers = list(range(1000,9999))
random.shuffle(available_numbers)


@app.route('/create_account', methods=['POST'])
def create_account():

    data = request.get_json()

    player_id = available_numbers.pop()
    player[player_id] = {
        'name': data['name']
    }
    return {
        'playerID': player_id,
        'name': player[player_id]['name']
    }



@app.route('/status', methods=['GET'])
def getstatus():
    try:
        match_id= int(request.args['matchid'])
        print(matches[match_id])
        return {
            'matchID': match_id,
            'status': matches[match_id]['status'],
            'gameBoard': matches[match_id]['gameBoard']
        }
    except (KeyError, TypeError):
        return {
            'error': 'bad request'
        }, 400


@app.route('/scoreboard', methods=['GET'])
def get_scoreboard():


    top_sorted_players = sorted(player.items(), key=lambda x: x[1].get('score', 0), reverse=True)[:10]

    scoreboard ={}

    for nr,p in enumerate(top_sorted_players,start=1):
        scoreboard[str(nr)] = {'name':p['name'], 'score': p.get('score', 0)}

    return scoreboard


@app.route('/play', methods=['GET'])
def play():

    match_id = int(request.args['matchid'])
    player_id = int(request.args['playerid'])
    row = int(request.args['row'])
    column = int(request.args['column'])


    match = matches[match_id]


    if match['status'] == 'TurnPlayer1' and player_id == match['player1']:
        match['gameBoard'][int(row)][int(column)] = 1
        match['status'] = 'TurnPlayer2'
    elif match['status'] == 'TurnPlayer2' and player_id == match['player2']:
        match['gameBoard'][int(row)][int(column)] = 2
        match['status'] = 'TurnPlayer1'

    if match['gameBoard'][row][column] != 0:
        return {
            'error': 'Cell already occupied'
        }, 400
    winnner = check_win_condition(match['gameBoard'])

    if winnner == 1:
        if player_id == match['player1']:
            player[player_id]['score'] = player.get(player_id, {}).get('score', 0) + 3

        match['status'] = 'WinPlayer1'
    elif winnner == 2:
        if player_id == match['player2']:
            player[player_id]['score'] = player.get(player_id, {}).get('score', 0) + 3
        match['status'] = 'WinPlayer2'
    elif winnner == 3:
        player[player_id]['score'] = player.get(player_id, {}).get('score', 0) + 1
        match['status'] = 'Draw'



    return {
        'matchID': match_id,
        'status': matches[match_id]['status'],
        'gameBoard': matches[match_id]['gameBoard']
    }

@app.route('/matchmake', methods=['POST'])
def matchmake():  # put application's code here
    turnId = 1

    data = request.get_json(silent=True)
    if not matches:
        if data:
            matchId = create_match(data['playerID'])
        else:
            matchId = create_match()

    elif data:
        player_id = data.get('playerID')
        if not player_id or player_id not in player:
            return {
                'error': 'Invalid player ID'
            }, 400

        for id in matches.keys():
            if join_match(id, player_id):
                matchId = id
                turnId =2
                break
        else:
            matchId =create_match(player_id)

    else:
        for id in matches.keys():
            if join_match(id):
                matchId = id
                turnId = 2
                break
        else:
            matchId = create_match()



    return {
        'matchID': matchId,
        'turnID': turnId,
        'playerID': matches[matchId]['player1' if turnId == 1 else 'player2']
    }


def create_match(player_id=None):
    match_id = random.randint(100,999)
    print('MatchID',match_id)

    if player_id:
        player1 = player_id
    else:
        player1 = available_numbers.pop()
    matches[match_id] = {
        'player1': player1,
        'player2': None,
        'turnID': 1,
        'status': 'Waiting',
        'gameBoard': [[0,0,0],[0,0,0],[0,0,0]]

    }
    return match_id

def join_match(match_id, player_id=None):
    if match_id in matches and matches[match_id]['player2'] is None:
        if player_id:
            matches[match_id]['player2'] = player_id
        else:
            matches[match_id]['player2'] = available_numbers.pop()
        matches[match_id]['status'] = 'TurnPlayer1'
        print(matches[match_id])
        return True
    return False

def check_win_condition(game_board):
    for row in game_board:
        if row[0] == row[1] == row[2] != 0:
            return row[0]

    for col in range(3):
        if game_board[0][col] == game_board[1][col] == game_board[2][col] != 0:
            return game_board[0][col]

    if game_board[0][0] == game_board[1][1] == game_board[2][2] != 0:
        return game_board[0][0]
    if game_board[0][2] == game_board[1][1] == game_board[2][0] != 0:
        return game_board[0][2]

    # Check for draw
    if all(cell != 0 for row in game_board for cell in row):
        return 3  # Indicate a draw

    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0')
