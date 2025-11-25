from django.urls import path
from .views import (
    MochilaItemListCreateView, MochilaEventoListCreateView, MochilaPocaoListCreateView,
    QuestaoView, QuestaoAleatoriaView, QuestaoPorItemView,
    CapturaView, ConfirmarCapturaView, ResetConversaDebugView, MochilaFaunaListView,
    MochilaFloraListView, MochilaItensListView,
)

urlpatterns = [
    path('capturas/fauna/', MochilaFaunaListView.as_view(), name='captura-fauna'),
    path('capturas/flora/', MochilaFloraListView.as_view(), name='captura-flora'),
    path('capturas/itens/', MochilaItensListView.as_view(), name='captura-itens'),
    path('capturas/eventos/', MochilaEventoListCreateView.as_view(), name='captura-eventos'),
    path('capturas/pocoes/', MochilaPocaoListCreateView.as_view(), name='captura-pocoes'),
    path('capturas/add-item/', MochilaItemListCreateView.as_view(), name='add-item'),
    path('captura/<int:item_id>/', CapturaView.as_view(), name='captura'),
    path('captura/<int:item_id>/confirmar/', ConfirmarCapturaView.as_view(), name='confirmar-captura'),
    path('questao/<int:pk>/', QuestaoView.as_view(), name='questao_view'),
    path('questao/aleatoria/', QuestaoAleatoriaView.as_view(), name='questao-aleatoria'),
    path('questao/item/<int:item_id>/', QuestaoPorItemView.as_view(), name='questao-por-item'),

    # debug
    path("debug/reset-conversa/", ResetConversaDebugView.as_view()),
]
