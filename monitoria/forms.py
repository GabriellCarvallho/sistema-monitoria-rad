from django import forms



from .models import Duvida, Disciplina


class DuvidaForm(forms.ModelForm):
    class Meta:
        model = Duvida
        fields = ['titulo', 'descricao', 'disciplina']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disciplina'].queryset = Disciplina.objects.filter(monitores=user)


class RespostaForm(forms.ModelForm):
    resposta = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Duvida
        fields = ['resposta']
