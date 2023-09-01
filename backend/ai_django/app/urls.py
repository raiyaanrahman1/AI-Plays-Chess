from django.urls import path

from . import views

urlpatterns = [
    path('create-game', views.create_game, name='create-game'),
    path('submit-move', views.submit_move, name='submit-move'),
    # path('update-move-tree', views.update_move_tree, name='update-move-tree'),
    path('play-best-move', views.play_best_move, name='play-best-move')
]
