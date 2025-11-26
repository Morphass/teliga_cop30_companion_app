from rest_framework import serializers
from .models import Evento

class EventoSerializer(serializers.ModelSerializer):
    nome_campeao = serializers.CharField(source='campeao.username', read_only=True)
    nome_criatura_campeao = serializers.CharField(source='item_campeao.item.nome', read_only=True)
    imagem_criatura_campeao = serializers.CharField(source='item_campeao.item.imagem', read_only=True)
    vida_criatura_campeao = serializers.IntegerField(source='item_campeao.vida_atual', read_only=True)
    class Meta:
        model = Evento
        fields = '__all__'
