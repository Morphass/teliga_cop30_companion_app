from django.urls import path
from .views import (
    MochilaItemListCreateView, MochilaEventoListCreateView, MochilaPocaoListCreateView,
    QuestaoView, QuestaoAleatoriaView, QuestaoPorItemView,
    CapturaView, ConfirmarCapturaView, ResetConversaDebugView, 
)

urlpatterns = [
    #  Mochilas
    path('capturas/items/', MochilaItemListCreateView.as_view(), name='captura-items'),
    path('capturas/eventos/', MochilaEventoListCreateView.as_view(), name='captura-eventos'),
    path('capturas/pocoes/', MochilaPocaoListCreateView.as_view(), name='captura-pocoes'),

    #  Captura
    path('captura/<int:item_id>/', CapturaView.as_view(), name='captura'),
    path('captura/<int:item_id>/confirmar/', ConfirmarCapturaView.as_view(), name='confirmar-captura'),

    #  Questões
    path('questao/<int:pk>/', QuestaoView.as_view(), name='questao_view'),
    path('questao/aleatoria/', QuestaoAleatoriaView.as_view(), name='questao-aleatoria'),
    path('questao/item/<int:item_id>/', QuestaoPorItemView.as_view(), name='questao-por-item'),
    
    #debug
    #reset de conversa
    path("debug/reset-conversa/", ResetConversaDebugView.as_view()),

]
