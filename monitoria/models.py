from django.conf import settings
from django.db import models


class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    ativa = models.BooleanField(default=True)
    monitores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='disciplinas_monitoradas',
        blank=True,
    )

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return f'{self.codigo} - {self.nome}'

    def tem_monitor(self, user):
        return self.monitores.filter(pk=user.pk).exists()


class Duvida(models.Model):
    class Situacao(models.TextChoices):
        ABERTA = 'ABERTA', 'Aberta'
        EM_ATENDIMENTO = 'EM_ATENDIMENTO', 'Em atendimento'
        RESPONDIDA = 'RESPONDIDA', 'Respondida'
        ENCERRADA = 'ENCERRADA', 'Encerrada'

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.PROTECT, related_name='duvidas'
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='duvidas_abertas',
    )
    monitor_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='duvidas_atendidas',
    )
    resposta = models.TextField(blank=True)
    situacao = models.CharField(
        max_length=20, choices=Situacao.choices, default=Situacao.ABERTA
    )
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criada_em']
        permissions = [('ver_todas_duvidas', 'Pode ver todas as dúvidas')]

    def __str__(self):
        return self.titulo

    def pode_ser_assumida_por(self, user):
        return self.situacao == self.Situacao.ABERTA and self.disciplina.tem_monitor(user)

    def pode_ser_respondida_por(self, user):
        return (self.situacao == self.Situacao.EM_ATENDIMENTO
                and self.monitor_responsavel_id == user.pk)

    def pode_ser_encerrada_por(self, user):
        return self.situacao == self.Situacao.RESPONDIDA and self.autor_id == user.pk