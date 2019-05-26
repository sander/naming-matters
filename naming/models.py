import uuid

from django.conf import settings
from django.db import models
from django.template import loader


class Concept(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    kind = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="instances")
    context = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="concepts")

    def __str__(self):
        # return f"{self.label} ({self.owner} in {self.context})"
        return self.label

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["key", "owner"],
                name="unique_keys_per_owner"),
            models.UniqueConstraint(
                fields=["owner", "label", "context"], name="unique_concept_per_owner_and_context"),
        ]

    def turtle(self):
        def id(c):
            if c:
                if c.key == self.key:
                    return ""
                else:
                    return f"#{c.key}"
            else:
                return None
        concepts = [{"id": "", "label": self.label,
                     "kind": id(self.kind)}]

        children = Concept.objects.filter(owner=self.owner, context=self)
        concepts.extend([{"id": id(c), "label": c.label, "kind": id(
            c.kind), "context": id(c.context)} for c in children])

        template = loader.get_template("naming/export2.ttl")
        #concepts = Concept.objects.filter(owner=self.owner).order_by("key")
        #concepts = Concept.objects.filter(owner=request.user, key=concept_key)
        export = template.render({"concepts": concepts})
        return export
        #template = loader.get_template("naming/export.ttl")
        #concepts = Concept.objects.filter(owner=request.user).order_by("key")
        #concepts = Concept.objects.filter(owner=request.user, key=concept_key)
        #export = template.render({"concepts": concepts}, request)

#        return """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
#
# """ + "foo"

    def dependencies(self):
        pass
