import uuid

from django.conf import settings
from django.db import models
from django.template import loader
from mptt.models import MPTTModel, TreeForeignKey


class Concept(MPTTModel):
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    parent = TreeForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children", verbose_name="Kind")

    def __str__(self):
        return self.label

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["key", "owner"],
                name="unique_keys_per_owner"),
        ]

    def descendants_in_context(self):
        if hasattr(self, "context"):
            return [ctx.concept for ctx in self.context.get_descendants()]
        else:
            return []

    def descendants_in_context_including_self(self):
        if hasattr(self, "context"):
            return [ctx.concept for ctx in self.context.get_descendants(include_self=True)]
        else:
            return [self]

    def kind_hierarchy(self):
        return self.get_ancestors()

    def deps(self):
        if self.context:
            desc = {ctx.concept for ctx in self.context.get_descendants(
                include_self=True)}
        else:
            desc = {self}
        return {concept.parent for concept in desc if concept.parent != None} - desc


class Context(MPTTModel):
    concept = models.OneToOneField(
        Concept, on_delete=models.CASCADE, primary_key=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="children")

    def __str__(self):
        return str(self.concept)
