from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Concept


@login_required
def index(request):
    concept_list = Concept.objects.filter(owner=request.user, kind=None)
    context = {"concept_list": concept_list}
    return render(request, "naming/index.html", context)
    # output = ", ".join([c.label for c in concept_list])
    # return HttpResponse(output)


@login_required
def detail(request, concept_key):
    concept = get_object_or_404(Concept, key=concept_key, owner=request.user)
    contexts = Concept.objects.filter(owner=request.user).exclude(kind=None)
    kinds = Concept.objects.filter(owner=request.user, kind=None)
    return render(request, "naming/detail.html", {"concept": concept, "kinds": kinds, "contexts": contexts})


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
