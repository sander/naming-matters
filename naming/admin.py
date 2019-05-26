from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Concept, Context, Repository, SyncMapping


admin.site.register(Concept, DraggableMPTTAdmin,
                    list_display=("tree_actions", "indented_title",), list_display_links=("indented_title",))
admin.site.register(Context, DraggableMPTTAdmin,
                    list_display=("tree_actions", "indented_title",), list_display_links=("indented_title",))
admin.site.register(Repository)
admin.site.register(SyncMapping)
