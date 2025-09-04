from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request: HttpRequest, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request: HttpRequest):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request: HttpRequest, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
