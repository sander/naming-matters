import uuid

from django.conf import settings
from django.db import models


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
