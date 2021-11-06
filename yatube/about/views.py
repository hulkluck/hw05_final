from django.shortcuts import render
from django.views.generic.base import TemplateView


class AboutTechView(TemplateView):

    template_name = 'about/tech.html'

    def AboutTechView(request):
        return render(request, 'about/tech.html')


class AboutAuthorView(TemplateView):

    template_name = 'about/author.html'

    def AboutAuthorView(request):
        return render(request, 'about/tech.html')
