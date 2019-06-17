#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import subprocess
from BTrees.OOBTree import OOBTree
from cocktail import schema
from cocktail.persistence import PersistentMapping
from cocktail.html import templates
from woost import app
from woost.models import Item, Publishable, LocaleMember

export_task_schema = schema.Schema(
    "woost.extensions.staticpub.export.export_task_schema",
    members = [
        schema.Reference(
            "item",
            type = Publishable,
            required = True
        ),
        LocaleMember(
            "language"
        ),
        schema.String(
            "action",
            required = True,
            enumeration = ["post", "delete"]
        ),
        schema.String(
            "state",
            required = True,
            enumeration = ["pending", "failed", "success"]
        ),
        schema.String(
            "error_message"
        )
    ]
)


class Export(Item):

    type_group = "staticpub"
    instantiable = False

    members_order = [
        "destination",
        "state",
        "tasks"
    ]

    destination = schema.Reference(
        editable = schema.READ_ONLY,
        type = "woost.extensions.staticpub.destination.Destination",
        bidirectional = True,
        required = True
    )

    state = schema.String(
        editable = schema.READ_ONLY,
        default = "idle",
        enumeration = [
            "idle",
            "running",
            "completed"
        ],
        indexed = True,
        display = "woost.extensions.staticpub.ExportStateDisplay"
    )

    tasks = schema.Mapping(
        editable = schema.NOT_EDITABLE,
        searchable = False,
        type = OOBTree,
        keys = schema.Tuple(
            items = (schema.Integer(), LocaleMember())
        ),
        values = export_task_schema
    )

    def add_task(self, action, item, language):

        valid_actions = ("post", "delete")
        if action not in valid_actions:
            raise ValueError(
                "Invalid export action (%r); should be one of %r"
                % (action, valid_actions)
            )

        if not isinstance(item, Publishable):
            raise ValueError(
                "Can't export (%r); expected an instance of "
                "woost.models.Publishable"
                % item
            )

        key = (item.id, language)
        task = self.tasks.get(key)
        if task is None:
            task = PersistentMapping({
                "item": item,
                "language": language
            })
            self.tasks[key] = task

        task["action"] = action
        task["state"] = "pending"
        task["error_message"] = None
        return task

    @property
    def progress(self):

        total = 0
        completed = 0

        for task in self.tasks.itervalues():
            total += 1
            if task["state"] != "pending":
                completed += 1

        if not total:
            return 0.0

        return float(completed) / total

    def create_export_job(self):
        return self.destination.export_job_class(self)

    def execute_in_subprocess(self):
        script = app.path("scripts", "staticpub.py")
        return subprocess.Popen([sys.executable, script, "export", "export:%d" % self.id])
