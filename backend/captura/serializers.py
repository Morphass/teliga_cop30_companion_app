from rest_framework import serializers
from .models import (
    MochilaItem, MochilaEvento, MochilaPocao,
    ConversaQuestoes, CapturaProgresso
)
from item.serializers import ItemSerializer
from events.serializers import EventoSerializer
from item.models import Item
from events.models import Evento
# import random # Não é mais necessário


class MochilaItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(write_only=True, source='item', queryset=Item.objects.all())
    # chance_bonus = serializers.SerializerMethodField() # REMOVIDO

    class Meta:
        model = MochilaItem
        fields = [
            'id', 
            'item', 
            'item_id', 
            'captured_at', 
            'foi_captura_forcada' # ADICIONADO
        ]
    
    # get_chance_bonus removido daqui


class MochilaEventoSerializer(serializers.ModelSerializer):
    evento = EventoSerializer(read_only=True)
    evento_id = serializers.PrimaryKeyRelatedField(write_only=True, source='evento', queryset=Evento.objects.all())

    class Meta:
        model = MochilaEvento
        fields = ['id', 'evento', 'evento_id', 'captured_at']


class MochilaPocaoSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    pocao_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='item', queryset=Item.objects.filter(tipo=Item.Tipo.POC), required=False
    )
    item_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source='item', queryset=Item.objects.filter(tipo=Item.Tipo.POC), required=False
    )
    chance_bonus = serializers.SerializerMethodField()

    class Meta:
        model = MochilaPocao
        fields = ['id', 'item', 'pocao_id', 'item_id', 'captured_at', 'chance_bonus']

    def get_chance_bonus(self, obj):
        """
        Retorna a porcentagem de chance real da poção.
        """
        # CORRIGIDO: Pega o bônus real do item
        if obj.item and obj.item.bonus_captura:
            return obj.item.bonus_captura
        return 0 # Valor padrão se não houver bônus


class ConversaQuestoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversaQuestoes
        fields = ['id', 'item', 'pergunta', 'escolha_a', 'escolha_b', 'escolha_c']


class RespostaSerializer(serializers.Serializer):
    resposta = serializers.CharField(max_length=1)


class CapturaProgressoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapturaProgresso
        fields = ['id', 'user', 'item', 'chance', 'capturado', 'conversa_usada']
        read_only_fields = ['user', 'chance', 'capturado', 'conversa_usada']
