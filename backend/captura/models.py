from django.conf import settings
from django.db import models
from item.models import Item
from events.models import Evento
from habilidades.models import Habilidade

class MochilaItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mochila_itens')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='capturado_por')
    captured_at = models.DateTimeField(auto_now_add=True)

    foi_captura_forcada = models.BooleanField(default=False, help_text="Indica se a captura usou 'atacar'")
    vida_atual = models.IntegerField(default=100)
    vida_maxima = models.IntegerField(default=100)
    ataque = models.IntegerField(default=10)
    bonus_vida_recebido = models.IntegerField(default=0)
    bonus_ataque_recebido = models.IntegerField(default=0)

    class Meta:
        #esta comentado para que a função de pegar varios animais funcione unique_together = ('user', 'item')
        ordering = ['-captured_at']

    def __str__(self):
        return f'{self.user} -> {self.item} (ATQ: {self.ataque} | HP: {self.vida_atual})'


class MochilaEvento(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mochila_eventos')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='capturado_por')
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'evento')
        ordering = ['-captured_at']

    def __str__(self):
        return f'{self.user} -> {self.evento}'


class MochilaPocao(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mochila_pocoes')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='pocoes_capturadas')
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-captured_at']
        verbose_name = 'Mochila - Poção'
        verbose_name_plural = 'Mochilas - Poções'

    def __str__(self):
        return f'{self.user} -> {self.item} (poção)'


# ===========================
#  CAPTURA E PROGRESSO
# ===========================

class Captura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    habilidade_usada = models.ForeignKey(Habilidade, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.usuario} capturou {self.item} usando {self.habilidade_usada or 'desconhecida'}"


class CapturaProgresso(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    chance = models.FloatField(default=0)
    capturado = models.BooleanField(default=False)
    atualizado_em = models.DateTimeField(auto_now=True)
    conversa_usada = models.BooleanField(default=False)
    foi_ataque_usado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'item')

    def aumentar_chance(self, valor):
        """Aumenta a chance de captura sem ultrapassar 100."""
        self.chance = min(100, self.chance + valor)
        self.save()
        return self.chance

    def mudar_chance(self, valor):
        """Modifica a chance sem ultrapassar 0–1."""
        self.chance = max(0, min(1, self.chance + valor))
        self.save()
        return self.chance


# ===========================
#  QUESTÕES
# ===========================

class ConversaQuestoes(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversa_questoes')
    pergunta = models.CharField(max_length=255)
    escolha_a = models.CharField(max_length=100)
    escolha_b = models.CharField(max_length=100)
    escolha_c = models.CharField(max_length=100)
    resposta_correta = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C')],
    )

    def checar_resposta(self, resposta: str) -> bool:
        return resposta.strip().upper() == self.resposta_correta

    def __str__(self):
        return f"Pergunta para {self.item.nome}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Questão de Conversa'
        verbose_name_plural = 'Questões de Conversa'