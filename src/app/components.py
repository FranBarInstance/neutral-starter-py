"""Component management module."""

import inspect
import json
import os
import sys
from importlib import import_module

from flask import Blueprint

from constants import UUID_MAX_LEN, UUID_MIN_LEN
from utils.utils import merge_dict, parse_vars

from .config import Config

COMPONENT_SNIPPET_NAME = "core:include-components-register-ntpl"
COMPONENT_INIT_FILE_NAME = "component-init.ntpl"


class Components:
    """Manages component loading, registration, and initialization."""

    def __init__(self, app):
        with open(Config.DEFAULT_SCHEMA, "r", encoding="utf-8") as file:
            self.schema = json.load(file)

        self.app = app
        self.dir = sorted(os.listdir(Config.COMPONENT_DIR))
        self.collection = {}
        self.component_schema = {}
        self.component_snip = ""
        self.custom = {}

        # register components
        self._register_manifest()
        self._register_ntpl()
        self._register_schema()
        self._set_data()
        self._parse_schema_vars()
        self._register_main_module()
        self._register_blueprints()
        self._component_snip()

    def _register_manifest(self):
        """Registers manifests for valid components."""

        for name in self.dir:
            path = os.path.join(Config.COMPONENT_DIR, name)

            if not os.path.isdir(path):
                continue

            if not name.startswith("cmp_"):
                if self.app.debug:
                    print(f"✗ Skipping component not starting with 'cmp_': {name}")
                continue

            manifest = self.get_manifest(path, name)
            uuid = manifest["uuid"]

            self.custom[uuid] = self.get_custom(path, name)

            if "manifest" in self.custom[uuid]:
                merge_dict(manifest, self.custom[uuid]["manifest"])

            self.collection[uuid] = {
                "name": name,
                "path": path,
                "manifest": manifest,
            }

            if self.app.debug:
                print(f"✓ manifest for {name} uuid:{uuid}")

    def _register_ntpl(self):
        """Registers component-init.ntpl if present."""
        for uuid, component in self.collection.items():
            ntpl_path = os.path.join(
                component["path"], "neutral", COMPONENT_INIT_FILE_NAME
            )

            if os.path.isfile(ntpl_path):
                component["ntpl"] = ntpl_path
                if self.app.debug:
                    print(
                        f"✓ {COMPONENT_INIT_FILE_NAME} for {component['name']} uuid:{uuid}"
                    )

    def _register_schema(self):
        """Registers schema.json if present and merges into global schema."""
        for uuid, component in self.collection.items():
            schema_path = os.path.join(component["path"], "schema.json")

            if os.path.exists(schema_path):
                with open(schema_path, "r", encoding="utf-8") as file:
                    self.component_schema[uuid] = json.load(file)

                    if "schema" in self.custom[uuid]:
                        merge_dict(
                            self.component_schema[uuid], self.custom[uuid]["schema"]
                        )

                    merge_dict(self.schema, self.component_schema[uuid])

                    if self.app.debug:
                        print(f"✓ schema for {component['name']} uuid:{uuid}")
            else:
                self.component_schema[uuid] = {}

    def _register_main_module(self):
        """Registers and initializes __init__.py main module if present."""
        for uuid, component in self.collection.items():
            module_path = os.path.join(component["path"], "__init__.py")

            if os.path.exists(module_path):
                module_name = f"component.{component['name']}"
                main_module = import_module(module_name)

                # if init_component exists
                if hasattr(main_module, "init_component"):
                    main_module.init_component(component, self.component_schema[uuid], self.schema)

                    # Update schema; it may have changed in init_component.
                    merge_dict(self.schema, self.component_schema[uuid])
                else:
                    if self.app.debug:
                        print(
                            f"✗ init_component not found in {component['name']} uuid:{uuid}"
                        )

                if self.app.debug:
                    print(f"✓ Main module initialized: {component['name']} uuid:{uuid}")

    def _register_blueprints(self):
        """Registers route blueprints if present."""

        # Reverse order to prioritize the last ones, with two groups:
        # 1. Others in reverse order (processed first)
        # 2. cmp_9 components in reverse order (processed last)
        # The reason for this is to keep catch_all type components at the end
        items_list = list(self.collection.items())
        cmp_9 = [(u, c) for u, c in items_list if c["name"].startswith('cmp_9')]
        others = [(u, c) for u, c in items_list if not c["name"].startswith('cmp_9')]

        for uuid, component in list(reversed(others)) + list(reversed(cmp_9)):
            blueprints_path = os.path.join(component["path"], "route", "__init__.py")

            if os.path.isfile(blueprints_path):
                module_path = f"component.{component['name']}.route"
                module = import_module(module_path)

                if hasattr(module, "init_blueprint"):
                    module.init_blueprint(component, self.component_schema[uuid], self.schema)
                else:
                    print(
                        f"✗ No init_blueprint found in {component['name']} uuid:{uuid}"
                    )

                if hasattr(module, "bp") and module.bp is not None:
                    self.app.register_blueprint(module.bp)
                    component["bp"] = module.bp.name
                    if self.app.debug:
                        print(
                            f"✓ Blueprint registered: {module.bp.name} for {component['name']} uuid:{uuid}"
                        )
                else:
                    if self.app.debug:
                        print(
                            f"✗ No blueprint found in {component['name']} uuid:{uuid}"
                        )

    def _component_snip(self):
        for uuid, component in self.collection.items():
            if "ntpl" in component and os.path.isfile(component["ntpl"]):
                with open(component["ntpl"], "r", encoding="utf-8") as file:
                    self.component_snip += file.read() + "\n"
                    if self.app.debug:
                        print(
                            f"✓ {COMPONENT_SNIPPET_NAME} for {component['name']} uuid:{uuid}"
                        )

        # create COMPONENT_SNIPPET_NAME snippet
        self.schema["inherit"]["snippets"] = {
            COMPONENT_SNIPPET_NAME: self.component_snip
        }

    def _set_data(self):
        self.schema["data"]["COMPONENTS_MAP_BY_NAME"] = {}
        self.schema["data"]["COMPONENTS_MAP_BY_UUID"] = {}

        for uuid, comp in self.collection.items():
            name = comp["name"]
            self.schema["data"]["COMPONENTS_MAP_BY_NAME"][name] = uuid
            self.schema["data"]["COMPONENTS_MAP_BY_UUID"][uuid] = name
            self.schema["data"].setdefault(uuid, {}).update(comp)
            self.schema["data"].setdefault(name, {}).update(comp)

    def _parse_schema_vars(self):
        self.schema = json.loads(parse_vars(json.dumps(self.schema), self.schema))
        for uuid in self.component_schema:
            self.component_schema[uuid] = json.loads(parse_vars(json.dumps(self.component_schema[uuid]), self.schema))

    def get_custom(self, path, name):
        """Retrieves and validates manifest.json for a component."""
        custom_path = os.path.join(path, "custom.json")

        if not os.path.isfile(custom_path):
            return {}

        with open(custom_path, "r", encoding="utf-8") as file:
            custom = json.load(file)
            if not isinstance(custom, dict):
                raise ValueError(
                    f"custom.json in component {name} must be a JSON object"
                )

        return custom

    def get_manifest(self, path, name):
        """Retrieves and validates manifest.json for a component."""
        manifest_path = os.path.join(path, "manifest.json")

        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(f"Component {name} is missing manifest.json file")

        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest = json.load(file)
            if not isinstance(manifest, dict):
                raise ValueError(
                    f"manifest.json in component {name} must be a JSON object"
                )

        if not self.validate_manifest(manifest):
            raise ValueError(f"Component {name} error fields in manifest.json")

        return manifest

    def validate_manifest(self, manifest):
        """Validates required fields in the manifest."""
        required_fields = ["uuid", "name", "description", "version", "route"]

        for field in required_fields:
            if field not in manifest:
                print(f"⚠️  field {field} not found in manifest")
                return False

        if not self.validate_uuid(manifest["uuid"]):
            print(f"⚠️  Invalid uuid {manifest['uuid']}")
            return False

        return True

    def validate_uuid(self, uuid_str):
        """Validates custom UUID format without regex."""
        if not isinstance(uuid_str, str):
            return False

        if len(uuid_str) < UUID_MIN_LEN or len(uuid_str) > UUID_MAX_LEN:
            return False

        if not "_" in uuid_str:
            return False

        allowed_chars = (
            "abcdefghijklmnopqrstuvwxyz0123456789_"
        )
        for char in uuid_str:
            if char not in allowed_chars:
                return False

        return True


def create_blueprint(component, component_schema):
    """Creates Blueprint for a component using its manifest."""

    component_name = component.get("name", "unknown")
    manifest = component.get("manifest", {})

    if not manifest:
        raise ValueError(f"Manifest not found for component: {component_name}")

    url_prefix = manifest.get("route", "")

    bp_name = "bp_" + component_name.replace(".", "_").replace("-", "_")
    bp = Blueprint(bp_name, __name__, url_prefix=url_prefix)

    # Inject bp into the module
    caller_module = inspect.currentframe().f_back.f_globals["__name__"]
    setattr(sys.modules[caller_module], "bp", bp)

    bp.url_prefix = url_prefix
    bp.component = component
    bp.schema = component_schema
    bp.manifest = manifest
    bp.neutral_route = os.path.join(component["path"], "neutral", "route")

    return bp


def set_current_template(component, component_schema):
    """Set the current template for the app"""

    template_dir = os.path.join(component['path'], 'neutral')
    template_route = os.path.join(template_dir, 'route')

    component_schema.setdefault('data', {})
    component_schema['data'].setdefault('current', {})
    component_schema['data']['current'].setdefault('template', {})
    component_schema['data']['current']['template']['dir'] = template_dir
    component_schema['data']['CURRENT_NEUTRAL_ROUTE'] = template_route
    component_schema['data']['CURRENT_COMP_ROUTE'] = Config.COMP_ROUTE_ROOT

    return template_dir, template_route
