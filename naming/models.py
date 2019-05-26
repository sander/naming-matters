import uuid
import pprint
import posixpath

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


class Repository(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "repositories"

    def missing_dependencies(self):
        defined = {d for mapping in self.mappings.all()
                   for d in mapping.context.get_descendants(include_self=True)}
        used = {a for d in defined for a in d.concept.get_ancestors(
            include_self=True)}
        defined_keys = {d.concept.key for d in defined}
        return [c for c in used if c.key not in defined_keys]

    def files(self):
        keys = {ctx.concept.key: m.path if ctx.concept.key == m.context.concept.key else (m.path, ctx.concept.key)
                for m in self.mappings.all()
                for ctx in m.context.get_descendants(include_self=True)}
        template = loader.get_template("naming/export.ttl")

        def turtle(mapping):
            def key(k):
                if k not in keys:
                    return f"MISSING#{k}"
                elif keys[k] == mapping.path:
                    return ""
                elif isinstance(keys[k], str):
                    return keys[k]
                else:
                    path, segment = keys[k]
                    return f"#{segment}" if path == mapping.path else f"{posixpath.relpath(path, posixpath.dirname(mapping.path))}#{segment}"
            desc = [{"key": key(d.concept.key),
                     "kind": key(d.concept.parent.key) if d.concept.parent else None,
                     "context": key(d.parent.concept.key) if d.parent else None,
                     "label": d.concept.label}
                    for d in mapping.context.get_descendants(include_self=True)]
            return template.render({"concepts": desc})
        return {m.path: turtle(m) for m in self.mappings.all()}


class SyncMapping(models.Model):
    repository = models.ForeignKey(
        Repository, on_delete=models.CASCADE, related_name="mappings")
    context = models.ForeignKey(Context, on_delete=models.CASCADE)
    path = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.repository}: {self.path} ← {self.context}"
