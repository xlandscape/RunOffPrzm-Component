"""
Script for documenting the code of the RunOffPrzm component.
"""
import os
import base.documentation
import RunOffPrzm

root_folder = os.path.abspath(os.path.join(os.path.dirname(base.__file__), ".."))
base.documentation.document_component(
    RunOffPrzm.RunOffPrzm("RunOffPrzm", None, None),
    os.path.join(root_folder, "..", "variant", "RunOffPrzm", "README.md"),
    os.path.join(root_folder, "..", "variant", "mc.xml")
)
base.documentation.write_changelog(
    "RunOffPrzm component",
    RunOffPrzm.RunOffPrzm.VERSION,
    os.path.join(root_folder, "..", "variant", "RunOffPrzm", "CHANGELOG.md")
)
base.documentation.write_contribution_notes(os.path.join(root_folder, "..", "variant", "RunOffPrzm", "CONTRIBUTING.md"))
