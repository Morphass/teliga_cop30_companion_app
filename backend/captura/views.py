import random
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.views import APIView
from habilidades.models import Habilidade
from captura.models import CapturaProgresso, MochilaItem, MochilaEvento, MochilaPocao, ConversaQuestoes
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from item.models import Item
from .serializers import (
    MochilaItemSerializer, MochilaEventoSerializer, MochilaPocaoSerializer,
    ConversaQuestoesSerializer, RespostaSerializer, CapturaProgressoSerializer
)


class MochilaFaunaListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaItemSerializer

    def get_queryset(self):
        return MochilaItem.objects.filter(
            user=self.request.user, 
            item__tipo=Item.Tipo.ANI
        ).select_related('item')


class MochilaFloraListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaItemSerializer

    def get_queryset(self):
        return MochilaItem.objects.filter(
            user=self.request.user, 
            item__tipo=Item.Tipo.PLA
        ).select_related('item')


class MochilaItensListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaItemSerializer

    def get_queryset(self):
        return MochilaItem.objects.filter(
            user=self.request.user,
            item__tipo=Item.Tipo.NEN
        ).select_related('item')


class MochilaItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaItemSerializer

    def get_queryset(self):
        return MochilaItem.objects.filter(user=self.request.user).select_related('item')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data['item']
        
        captura, created = MochilaItem.objects.get_or_create(user=request.user, item=item)
        
        if created:
            bonus_vida = random.randint(0, 10)
            captura.vida_maxima = item.vida_base + bonus_vida
            captura.vida_atual = captura.vida_maxima
            captura.save()
        
        out = self.get_serializer(captura)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MochilaEventoListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaEventoSerializer

    def get_queryset(self):
        return MochilaEvento.objects.filter(user=self.request.user).select_related('evento')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evento = serializer.validated_data['evento']
        mochila, created = MochilaEvento.objects.get_or_create(user=request.user, evento=evento)
        out = self.get_serializer(mochila)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MochilaPocaoListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MochilaPocaoSerializer 

    def get_queryset(self):
        return MochilaPocao.objects.filter(
            user=self.request.user, 
            item__tipo=Item.Tipo.POC
        ).select_related('item')

    def create(self, request, *args, **kwargs):
        pocao_id = request.data.get('pocao_id') or request.data.get('item_id')
        if not pocao_id:
            return Response({"detail": "Campo 'pocao_id' ou 'item_id' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, pk=pocao_id, tipo=Item.Tipo.POC)
        mochila_pocao, created = MochilaPocao.objects.get_or_create(user=request.user, item=item)
        out = self.get_serializer(mochila_pocao)
        return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class QuestaoView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=ConversaQuestoesSerializer)
    def get(self, request, pk):
        """Retorna a questão com id=pk"""
        questao = get_object_or_404(ConversaQuestoes, pk=pk)
        serializer = ConversaQuestoesSerializer(questao)
        return Response(serializer.data)

    @extend_schema(request=RespostaSerializer)
    def post(self, request, pk):
        """Recebe a resposta do jogador para a questão (pk é id da questão)"""
        questao = get_object_or_404(ConversaQuestoes, pk=pk)
        serializer = RespostaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resposta = serializer.validated_data['resposta']

        progresso = CapturaProgresso.objects.filter(
            user=request.user,
            item=questao.item
        ).first()

        # Bloqueia se já conversou
        if progresso and progresso.conversa_usada:
            return Response(
                {"error": "Você já conversou com este item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        acertou = questao.checar_resposta(resposta)
        chance_atual = None

        if acertou and progresso:
            progresso.aumentar_chance(50)
            chance_atual = progresso.chance

        # Marca uso da conversa
        if progresso:
            progresso.conversa_usada = True
            progresso.save()

        return Response({
            "id": questao.id,
            "pergunta": questao.pergunta,
            "acertou": acertou,
            "chance": chance_atual,
            "resposta_correta": questao.resposta_correta if not acertou else None
        })


class QuestaoAleatoriaView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        questao = ConversaQuestoes.objects.order_by("?").first()
        if not questao: return Response({"error": "Nenhuma questão cadastrada."}, status=404)
        serializer = ConversaQuestoesSerializer(questao)
        return Response(serializer.data)


class QuestaoPorItemView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, item_id):
        questao = ConversaQuestoes.objects.filter(item_id=item_id).order_by("?").first()
        if not questao: return Response({"error": "Nenhuma questão disponível para este item."}, status=404)
        serializer = ConversaQuestoesSerializer(questao)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class CapturaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        progresso, _ = CapturaProgresso.objects.get_or_create(
            user=request.user,
            item=item,
            defaults={"chance": 0, "capturado": False, "conversa_usada": False}
        )
        return Response({
            "item_id": item.id,
            "chance": progresso.chance,
            "capturado": progresso.capturado,
            "conversa_usada": progresso.conversa_usada,
        })

    def post(self, request, item_id):
        habilidade_id = request.data.get("habilidade_id")
        acao = request.data.get("acao")

        item = get_object_or_404(Item, id=item_id)
        progresso, _ = CapturaProgresso.objects.get_or_create(
            user=request.user,
            item=item,
            defaults={"chance": 0, "capturado": False, "conversa_usada": False}
        )

        # Se veio uma ação textual (ex: atacar, conversar, investigar)
        if acao:
            valores = {'atacar': 20, 'conversar': 10, 'investigar': 15}
            if acao == 'atacar':
                progresso.foi_ataque_usado = True
            if acao in valores:
                progresso.aumentar_chance(valores[acao])
                return Response({"chance": progresso.chance, "acao": acao, "conversa_usada": progresso.conversa_usada})

            # ação desconhecida
            return Response({"error": "Ação desconhecida."}, status=400)

        # Se veio uma habilidade
        if habilidade_id:
            # valida existência e posse da habilidade
            try:
                habilidade = get_object_or_404(Habilidade, id=int(habilidade_id))
            except (ValueError, Habilidade.DoesNotExist):
                return Response({"error": "Habilidade inválida."}, status=404)

            from habilidades.models import PlayerHabilidade
            player_hab = PlayerHabilidade.objects.filter(user=request.user, habilidade=habilidade).first()
            if not player_hab:
                return Response({"error": "Você não possui essa habilidade."}, status=400)
            if not player_hab.pode_usar():
                return Response({"error": "Sem usos restantes dessa habilidade."}, status=400)

            # Aplica efeito da habilidade sobre o progresso
            habilidade.aplicar(progresso)

            # Registra uso
            player_hab.registrar_uso()
            progresso.save()

            return Response({
                "success": True,
                "chance": progresso.chance,
                "conversa_usada": progresso.conversa_usada,
                "habilidade": {
                    "id": habilidade.id,
                    "nome": habilidade.nome,
                    "quantidade": player_hab.quantidade,
                },
                "mensagem": f"{habilidade.nome} usada com sucesso! Chance atual: {progresso.chance}%"
            }, status=status.HTTP_200_OK)

        return Response({"error": "Ação ou Habilidade não informada."}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ConfirmarCapturaView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        progresso = CapturaProgresso.objects.filter(user=request.user, item_id=item_id).first()
        if not progresso: return Response({"error": "Progresso não encontrado."}, status=404)
        if progresso.chance < 100: return Response({"error": "Chance insuficiente."}, status=400)

        progresso.capturado = True
        progresso.save()

        item = get_object_or_404(Item, pk=item_id)

        # --- LÓGICA DE ATRIBUTOS ALEATÓRIOS (SPAWN) ---
        bonus_ranges = {
            'COMUM': (0, 10),
            'RARO': (10, 30),
            'EPICO': (30, 60),
            'LENDARIO': (60, 100)
        }

        intervalo = bonus_ranges.get(getattr(item, 'raridade', 'COMUM'), (0, 10))

        bonus_vida = random.randint(intervalo[0], intervalo[1])
        bonus_ataque = random.randint(intervalo[0] // 2, intervalo[1] // 2)

        mochila_item, created = MochilaItem.objects.get_or_create(
            user=request.user,
            item_id=item_id,
            defaults={
                'foi_captura_forcada': progresso.foi_ataque_usado,
                'vida_maxima': item.vida_base + bonus_vida,
                'vida_atual': item.vida_base + bonus_vida,
                'ataque': item.ataque_base + bonus_ataque,
                'bonus_vida_recebido': bonus_vida,
                'bonus_ataque_recebido': bonus_ataque
            }
        )

        if not created:
            mochila_item.foi_captura_forcada = progresso.foi_ataque_usado
            mochila_item.vida_maxima = item.vida_base + bonus_vida
            mochila_item.vida_atual = item.vida_base + bonus_vida
            mochila_item.ataque = item.ataque_base + bonus_ataque
            mochila_item.bonus_vida_recebido = bonus_vida
            mochila_item.bonus_ataque_recebido = bonus_ataque
            mochila_item.save()

        progresso.chance = 0
        progresso.capturado = False
        progresso.conversa_usada = False
        progresso.foi_ataque_usado = False
        progresso.save()

        return Response({
            "mensagem": f"{item.nome} capturado com sucesso!",
            "bonus_vida": f"+{bonus_vida}",
            "bonus_ataque": f"+{bonus_ataque}",
            "vida_total": mochila_item.vida_maxima,
            "ataque_total": mochila_item.ataque
        }, status=status.HTTP_200_OK)


# debug
class ResetConversaDebugView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = CapturaProgresso.objects.filter(user=request.user).update(conversa_usada=False)

        return Response({
            "ok": True,
            "itens_atualizados": count
        })
