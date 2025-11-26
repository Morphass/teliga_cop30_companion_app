from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decouple import config
import time
from .models import Evento
from .serializers import EventoSerializer
from captura.models import MochilaItem
from supabase import create_client, Client

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite leitura para qualquer um, mas escrita apenas para admin (staff).
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class EventoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar, criar, atualizar e deletar Eventos.
    """
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAdminOrReadOnly]

    # --- LÓGICA DE BATALHA ---
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def desafiar(self, request, pk=None):
        evento = self.get_object()
        
        if evento.campeao == request.user:
            return Response(
                {"error": "Você já é o campeão deste evento!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        item_desafiante_id = request.data.get('mochila_item_id')
        if not item_desafiante_id:
            return Response({"error": "Escolha um item."}, status=400)

        desafiante_item = get_object_or_404(MochilaItem, id=item_desafiante_id, user=request.user)

        if desafiante_item.defendendo_eventos.exists():
             evento_ocupado = desafiante_item.defendendo_eventos.first()
             return Response({
                 "error": f"Este animal já está defendendo '{evento_ocupado.titulo}'."
             }, status=status.HTTP_400_BAD_REQUEST)

        if not evento.campeao or not evento.item_campeao:
            self._definir_novo_campeao(evento, request.user, desafiante_item)
            return Response({
                "resultado": "VITORIA",
                "mensagem": "O local estava vazio! Você assumiu o controle sem lutar.",
                "novo_campeao": request.user.username
            })

        defensor_item = evento.item_campeao
        
        hp_atacante = desafiante_item.vida_atual
        atk_atacante = desafiante_item.ataque

        hp_defensor = defensor_item.vida_atual
        atk_defensor = defensor_item.ataque

        log_batalha = []
        vitoria = False
        turnos = 0
        max_turnos = 100 

        while hp_atacante > 0 and hp_defensor > 0 and turnos < max_turnos:
            turnos += 1
            
            hp_defensor -= atk_atacante
            log_batalha.append(f"Turno {turnos}: Você causou {atk_atacante} de dano. (Inimigo: {max(0, hp_defensor)} HP)")

            if hp_defensor <= 0:
                vitoria = True
                break 

            hp_atacante -= atk_defensor
            log_batalha.append(f"Turno {turnos}: Inimigo causou {atk_defensor} de dano. (Você: {max(0, hp_atacante)} HP)")

            if hp_atacante <= 0:
                vitoria = False
                break 

        if vitoria:
            self._definir_novo_campeao(evento, request.user, desafiante_item)
            return Response({
                "resultado": "VITORIA",
                "mensagem": f"Batalha intensa! Após {turnos} turnos, seu {desafiante_item.item.nome} venceu!",
                "detalhes": f"O campeão anterior caiu. Você assumiu o posto.",
                "log": log_batalha
            })
        else:
            return Response({
                "resultado": "DERROTA",
                "mensagem": f"Seu animal desmaiou após {turnos} turnos.",
                "detalhes": f"O {defensor_item.item.nome} do campeão ainda tinha {hp_defensor} de vida.",
                "log": log_batalha
            })

    def _definir_novo_campeao(self, evento, novo_campeao, novo_item):
        evento.campeao = novo_campeao
        evento.item_campeao = novo_item
        evento.save()


class SupabaseUploadView(APIView):
    permission_classes = [IsAdminUser] 

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')

        if not image_file:
            return Response(
                {"error": "Nenhum arquivo de imagem foi enviado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            supabase_url = config("SUPABASE_URL")
            supabase_key = config("SUPABASE_SERVICE_KEY") 
            supabase: Client = create_client(supabase_url, supabase_key)

            file_ext = image_file.name.split('.')[-1]
            file_name = f"event-{int(time.time())}.{file_ext}"
            bucket_name = "imagens-eventos"

            supabase.storage.from_(bucket_name).upload(
                file=image_file.read(),
                path=file_name,
                file_options={"content-type": image_file.content_type}
            )

            public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
            return Response({"imageUrl": public_url}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Erro no upload para o Supabase: {e}")
            return Response(
                {"error": "Ocorreu um erro interno ao processar o upload."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )