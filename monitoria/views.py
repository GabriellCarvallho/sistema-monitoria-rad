from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.http import HttpResponse

from .forms import DuvidaForm, RespostaForm
from .models import Duvida
from .forms import RespostaForm
def index(request):
    return render(request, "monitoria/main.html",)



class DuvidaCreateView(LoginRequiredMixin, CreateView):
    model = Duvida
    form_class = DuvidaForm
    template_name = 'monitoria/duvida_form.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.autor = self.request.user          # o sistema preenche o autor
        form.instance.situacao = Duvida.Situacao.ABERTA  # situação inicial
        messages.success(self.request, 'Dúvida aberta.')
        return super().form_valid(form)



VISIVEIS_NA_BASE = [Duvida.Situacao.RESPONDIDA, Duvida.Situacao.ENCERRADA]


# Quem vê o quê (também é a base do RF4)
def duvidas_visiveis(user):
    qs = Duvida.objects.select_related('disciplina', 'autor', 'monitor_responsavel')
    if user.has_perm('monitoria.ver_todas_duvidas'):        # professor
        return qs
    if user.disciplinas_monitoradas.exists():                 # monitor
        return qs.filter(disciplina__monitores=user)
    return qs.filter(autor=user)                              # aluno


class DuvidaDetailView(LoginRequiredMixin, DetailView):
    model = Duvida
    template_name = 'monitoria/duvida_detail.html'

    def get_queryset(self):
        # Vê o detalhe quem vê a dúvida na lista, ou qualquer um se ela já está na base
        visiveis = duvidas_visiveis(self.request.user).values('pk')
        return Duvida.objects.select_related('disciplina', 'autor', 'monitor_responsavel').filter(
            Q(pk__in=visiveis) | Q(situacao__in=VISIVEIS_NA_BASE)
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user, duvida = self.request.user, self.object
        ctx['pode_assumir'] = duvida.pode_ser_assumida_por(user)
        ctx['pode_responder'] = duvida.pode_ser_respondida_por(user)
        ctx['pode_encerrar'] = duvida.pode_ser_encerrada_por(user)
        ctx['resposta_form'] = RespostaForm()
        return ctx



@login_required
@require_POST
def assumir_duvida(request, pk):
    duvida = get_object_or_404(Duvida, pk=pk)
    if not duvida.disciplina.tem_monitor(request.user):
        raise PermissionDenied                     # 403: não é monitor dessa disciplina

    # Confere "está Aberta" e grava numa única operação no banco:
    # se dois monitores clicarem juntos, só um consegue.
    atualizadas = Duvida.objects.filter(pk=pk, situacao=Duvida.Situacao.ABERTA).update(
        monitor_responsavel=request.user,
        situacao=Duvida.Situacao.EM_ATENDIMENTO,
        atualizada_em=timezone.now(),              # o .update() não aciona o auto_now
    )
    if atualizadas:
        messages.success(request, 'Você assumiu o atendimento.')
    else:
        messages.error(request, 'Esta dúvida já foi assumida ou não está aberta.')
    return redirect('duvida_detail', pk=pk)



class ResponderDuvidaView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Duvida
    form_class = RespostaForm
    template_name = 'monitoria/duvida_responder.html'

    def test_func(self):
        # Só o monitor responsável, com a dúvida Em atendimento; senão, 403
        return self.get_object().pode_ser_respondida_por(self.request.user)

    def form_valid(self, form):
        form.instance.situacao = Duvida.Situacao.RESPONDIDA
        messages.success(self.request, 'Resposta enviada.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('duvida_detail', args=[self.object.pk])


@login_required
@require_POST
def encerrar_duvida(request, pk):
    duvida = get_object_or_404(Duvida, pk=pk)
    if duvida.autor_id != request.user.pk:
        raise PermissionDenied                     # 403: não é o autor
    if duvida.situacao != Duvida.Situacao.RESPONDIDA:
        messages.error(request, 'Só é possível encerrar uma dúvida que já foi respondida.')
    else:
        duvida.situacao = Duvida.Situacao.ENCERRADA
        duvida.save()
        messages.success(request, 'Dúvida encerrada.')
    return redirect('duvida_detail', pk=pk)


class BaseConhecimentoView(LoginRequiredMixin, ListView):
    template_name = 'monitoria/base_conhecimento.html'
    context_object_name = 'duvidas'

    def get_queryset(self):
        qs = Duvida.objects.filter(situacao__in=VISIVEIS_NA_BASE).select_related('disciplina')
        termo = self.request.GET.get('q', '').strip()
        if termo:
            qs = qs.filter(Q(titulo__icontains=termo) | Q(descricao__icontains=termo))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['termo'] = self.request.GET.get('q', '')
        return ctx