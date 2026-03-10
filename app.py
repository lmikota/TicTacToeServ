import random

from flask import Flask, request

app = Flask(__name__)

player = {}
matches = {}
available_numbers = list(range(1000, 9999))
random.shuffle(available_numbers)


@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json

    player_id = available_numbers.pop()
    player[player_id] = {
        'name': data.get('name', 'Anonymous')
    }
    return {
        'playerID': player_id,
        'name': player[player_id]['name']
    }


@app.route('/status', methods=['GET'])
def getstatus():
    try:
        match_id = int(request.args['matchid'])
        print(matches[match_id])
        return {
            'matchID': match_id,
            'status': matches[match_id]['status'],
            'gameBoard': matches[match_id]['gameBoard']
        }
    except KeyError as TypeError:
        return {
            'error': 'bad request'
        }, 400


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
        match['status'] = 'WinPlayer1'
    elif winnner == 2:
        match['status'] = 'WinPlayer2'
    elif winnner == 3:
        match['status'] = 'Draw'

    return {
        'matchID': match_id,
        'status': matches[match_id]['status'],
        'gameBoard': matches[match_id]['gameBoard']
    }


@app.route('/matchmake')
def matchmake():  # put application's code here

    if matches:
        for id in matches.keys():
            if join_match(id):
                matchId = id
                return {
                    'matchID': matchId,
                    'turnID': 2,
                    'playerID': matches[matchId]['player2']
                }

    matchId = create_match()

    print(matches)

    return {
        'matchID': matchId,
        'turnID': 1,
        'playerID': matches[matchId]['player1']
    }


def create_match():
    match_id = random.randint(100, 999)
    print('MatchID', match_id)
    matches[match_id] = {
        'player1': available_numbers.pop(),
        'player2': None,
        'turnID': 1,
        'status': 'Waiting',
        'gameBoard': [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    }
    return match_id


def join_match(match_id):
    if match_id in matches and matches[match_id]['player2'] is None:
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
