from __future__ import annotations

from app.models.plan import OrchestrationPlan, PlanStep
from app.models.resolution import ResolutionResult


def build_plan(resolution: ResolutionResult) -> OrchestrationPlan:
    if not resolution.selected_modules:
        return OrchestrationPlan(
            strategy="fallback",
            primary_module=None,
            primary_capability=None,
            secondary_modules=[],
            secondary_capabilities=[],
            steps=[],
            requires_handoff=resolution.handoff,
            preview_only=False,
            notes=["No eligible module selected during resolution."],
        )

    primary_module = resolution.selected_modules[0]
    primary_capability = (
        resolution.selected_capabilities[0]
        if resolution.selected_capabilities
        else None
    )

    if resolution.handoff:
        return OrchestrationPlan(
            strategy="handoff",
            primary_module=primary_module,
            primary_capability=primary_capability,
            secondary_modules=resolution.selected_modules[1:],
            secondary_capabilities=resolution.selected_capabilities[1:],
            steps=[
                PlanStep(
                    step_id="step-1",
                    module_id=primary_module,
                    capability_id=primary_capability,
                    role="primary",
                    optional=False,
                    reason="Primary module identified, but handoff is required.",
                )
            ],
            requires_handoff=True,
            preview_only=(resolution.mode == "preview"),
            notes=["Resolution requires handoff before execution."],
        )

    if resolution.should_compose and len(resolution.selected_modules) > 1:
        steps: list[PlanStep] = []

        for index, module_id in enumerate(resolution.selected_modules):
            capability_id = (
                resolution.selected_capabilities[index]
                if index < len(resolution.selected_capabilities)
                else None
            )

            steps.append(
                PlanStep(
                    step_id=f"step-{index + 1}",
                    module_id=module_id,
                    capability_id=capability_id,
                    role="primary" if index == 0 else "secondary",
                    optional=(index != 0),
                    reason=(
                        "Primary module in composed flow."
                        if index == 0
                        else "Secondary supporting module in composed flow."
                    ),
                )
            )

        return OrchestrationPlan(
            strategy="composed",
            primary_module=primary_module,
            primary_capability=primary_capability,
            secondary_modules=resolution.selected_modules[1:],
            secondary_capabilities=resolution.selected_capabilities[1:],
            steps=steps,
            requires_handoff=False,
            preview_only=(resolution.mode == "preview"),
            notes=["Composed orchestration plan generated."],
        )

    return OrchestrationPlan(
        strategy="single_module",
        primary_module=primary_module,
        primary_capability=primary_capability,
        secondary_modules=[],
        secondary_capabilities=[],
        steps=[
            PlanStep(
                step_id="step-1",
                module_id=primary_module,
                capability_id=primary_capability,
                role="primary",
                optional=False,
                reason="Single-module execution path selected.",
            )
        ],
        requires_handoff=False,
        preview_only=(resolution.mode == "preview"),
        notes=["Single-module orchestration plan generated."],
    )