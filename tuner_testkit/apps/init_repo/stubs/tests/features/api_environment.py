"""behave stage-mode: ``behave --stage api`` loads hooks from this file.

Wires the tuner_testkit logging lifecycle (``packages-logging.mdc``), the
``artifacts/reports/<run_id>/`` report manifest (``docs/spec/artifacts-layout.md``)
and puts the project root on ``sys.path`` so ``packages.*`` / ``apps.*`` import.
Stage-specific fixtures (workbench server, CLI sandboxes) are attached to
``context`` by the step modules in ``api_steps/``.
"""
from __future__ import annotations

from tuner_testkit import artifacts
from tuner_testkit.logging import hooks as log_hooks
from tuner_testkit.project import ensure_project_on_path


def before_all(context):
    context.project_root = ensure_project_on_path()
    log_hooks.on_run_begin(context)
    artifacts.report_run_begin(context, root=context.project_root)


def after_all(context):
    artifacts.report_run_end(context)
    log_hooks.on_run_end(context)


def before_feature(context, feature):
    log_hooks.on_feature_begin(context, feature)


def after_feature(context, feature):
    log_hooks.on_feature_end(context, feature)


def before_scenario(context, scenario):
    log_hooks.on_scenario_begin(context, scenario)


def after_scenario(context, scenario):
    artifacts.report_scenario_end(context, scenario)
    log_hooks.on_scenario_end(context, scenario)


def before_step(context, step):
    log_hooks.on_step_begin(context, step)


def after_step(context, step):
    log_hooks.on_step_end(context, step)
