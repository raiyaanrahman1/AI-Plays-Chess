from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .game_classes.game import Game
from .game_classes.game_errors import GameError
from .game_classes.constants import SPECIAL_MOVES


game = None


def get_required_tuple_param(request, param_name, required_len=2):
    param = request.GET.get(param_name)
    if param is None:
        return {'success': False, 'message': f'{param_name} required'}
    arr = param.split(',')
    if len(arr) != required_len:
        return {'success': False, 'message': f'{required_len} elements required for {param_name}'}
    tup = []
    for el in arr:
        try:
            num = int(el.strip())
        except Exception:
            return {
                'success': False,
                'message': f'elements in {param_name} must be integers'
                }

        if num < 0 or num > 7:
            return {
                'success': False,
                'message': f'elements in {param_name} must be between 0 and 7 inclusive'
            }
        tup.append(num)
    return {'success': True, 'tuple': tuple(tup)}


@csrf_exempt
@require_http_methods(["POST"])
def create_game(request):
    # create a new game instance and post it to database
    global game
    game = Game()
    game.calculate_legal_moves()
    response = {
        'board': game.get_board_repr(),
        'legal_moves': game.get_all_legal_moves(),
        'material': game.material,
        'move_history': [str(move) for move in game.move_history],
        'game_status': game.game_status,
    }
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(["POST"])
def submit_move(request):
    global game
    if game is None:
        return JsonResponse(
            'Need to start the game first by making a create-game request',
            safe=False,
            status=400
        )
    req_from_loc = get_required_tuple_param(request, 'from_loc')
    req_to_loc = get_required_tuple_param(request, 'to_loc')
    special_move = request.GET.get('special_move')
    if special_move == 'null':
        special_move = None
    if special_move is not None and special_move not in SPECIAL_MOVES:
        return JsonResponse(f'special_move {special_move} is invalid', safe=False, status=400)
    for param in (req_from_loc, req_to_loc):
        if not param['success']:
            return JsonResponse(param['message'], safe=False, status=400)
    from_loc = req_from_loc['tuple']
    to_loc = req_to_loc['tuple']
    if game.game_status['game_finished']:
        message = game.game_status['game_result_message']
        return JsonResponse(
            f'Cannot submit move, {message}',
            safe=False,
            status=400
        )
    try:
        game.make_move(from_loc, to_loc, special_move)
    except GameError as err:
        return JsonResponse(str(err), safe=False, status=400)

    response = {
        'board': game.get_board_repr(),
        'legal_moves': game.get_all_legal_moves(),
        'material': game.material,
        'move_history': [str(move) for move in game.move_history],
        'game_status': game.game_status,
    }
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(["GET"])
def get_best_move():
    pass
