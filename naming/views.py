import ast

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.conf import settings as conf_settings
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session

from .models import Concept, Repository


@login_required
def index(request):
    concept_list = Concept.objects.filter(
        owner=request.user, parent=None).order_by("label")
    context = {"concept_list": concept_list}
    return render(request, "naming/index.html", context)


@login_required
def detail(request, concept_key):
    concept = get_object_or_404(Concept, key=concept_key, owner=request.user)

    return render(request, "naming/detail.html", {"concept": concept})


@login_required
def new(request):
    try:
        label = request.POST["label"]
    except (KeyError,):
        return render(request, "naming/new.html", {
            "error_message": "Form incomplete"
        })
    else:
        if "kind" in request.POST and request.POST["kind"] != "":
            kind = get_object_or_404(
                Concept, key=request.POST["kind"], owner=request.user)
        else:
            kind = None
        if "context" in request.POST and request.POST["context"] != "":
            context = get_object_or_404(
                Concept, key=request.POST["context"], owner=request.user)
        else:
            context = None
        concept = Concept(label=label, kind=kind,
                          context=context, owner=request.user)
        concept.save()
        return HttpResponseRedirect(reverse("naming:detail", kwargs={"concept_key": concept.key}))


@login_required
def edit(request, concept_key):
    concept = get_object_or_404(Concept, key=concept_key, owner=request.user)
    if "label" in request.POST:
        concept.label = request.POST["label"]
    if "kind" in request.POST:
        if request.POST["kind"] == "":
            concept.kind = None
        else:
            concept.kind = get_object_or_404(
                Concept, key=request.POST["kind"], owner=request.user)
    if "context" in request.POST:
        if request.POST["context"] == "":
            concept.context = None
        else:
            concept.context = get_object_or_404(
                Concept, key=request.POST["context"], owner=request.user)
    concept.save()
    return HttpResponseRedirect(reverse("naming:detail", kwargs={"concept_key": concept.key}))


@login_required
def export(request):
    if request.POST:
        scope = ["public_repo"]
        oauth = OAuth2Session(
            client_id=conf_settings.GITHUB_CLIENT_ID, scope=scope)
        authorization_url, state = oauth.authorization_url(
            "https://github.com/login/oauth/authorize")
        request.session["repo_id"] = request.POST["repo"]
        return HttpResponseRedirect(authorization_url)
    else:
        return render(request, "naming/export.html", {"repositories": Repository.objects.filter(owner=request.user)})


@login_required
def oauth2_callback(request):
    authorization_response = "https://example.com" + request.get_full_path()
    scope = ["public_repo"]
    oauth = OAuth2Session(
        client_id=conf_settings.GITHUB_CLIENT_ID, scope=scope)
    response = oauth.fetch_token("https://github.com/login/oauth/access_token",
                                 authorization_response=authorization_response,
                                 client_secret=conf_settings.GITHUB_CLIENT_SECRET)
    token = response["access_token"]
    repo = get_object_or_404(
        Repository, pk=int(request.session["repo_id"]), owner=request.user)
    del request.session["repo_id"]
    repo.push_to_github(token)
    return HttpResponseRedirect(reverse("naming:export"))


@login_required
def settings(request):
    return render(request, "naming/settings.html", {})
