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
        """
        Endpoint para desafiar o campeão atual do evento.
        """
        evento = self.get_object()

        if evento.campeao == request.user:
            return Response(
                {"error": "Você já é o campeão deste evento! Aguarde um desafiante."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item_desafiante_id = request.data.get('mochila_item_id')
        if not item_desafiante_id:
            return Response({"error": "Você precisa escolher um item da mochila para batalhar."}, status=status.HTTP_400_BAD_REQUEST)

        desafiante_item = get_object_or_404(MochilaItem, id=item_desafiante_id, user=request.user)

        # --- LÓGICA DO COMBATE ---

        if not evento.campeao:
            self._definir_novo_campeao(evento, request.user, desafiante_item)
            return Response({
                "resultado": "VITORIA",
                "mensagem": "O evento estava sem proteção! Você é o novo campeão!",
                "novo_campeao": request.user.username
            })

        defensor_item = evento.item_campeao
        
        if not defensor_item:
             self._definir_novo_campeao(evento, request.user, desafiante_item)
             return Response({
                 "resultado": "VITORIA", 
                 "mensagem": "O antigo campeão fugiu. Vitória por W.O.!"
             })

        dano_causado = desafiante_item.ataque
        vida_defensor = defensor_item.vida_atual

        if dano_causado >= vida_defensor:
            self._definir_novo_campeao(evento, request.user, desafiante_item)
            return Response({
                "resultado": "VITORIA",
                "mensagem": f"Vitória! Seu {desafiante_item.item.nome} derrotou o {defensor_item.item.nome}!",
                "detalhes": f"Seu ataque ({dano_causado}) superou a vida ({vida_defensor}) do oponente.",
                "novo_campeao": request.user.username
            })
        else:
            return Response({
                "resultado": "DERROTA",
                "mensagem": f"Seu ataque não foi forte o suficiente.",
                "detalhes": f"Seu ataque ({dano_causado}) foi menor que a vida ({vida_defensor}) do campeão."
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