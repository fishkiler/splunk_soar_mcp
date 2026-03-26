from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ── Shared base ──────────────────────────────────────────────────────
class ListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    limit: int = Field(default=25, ge=1, le=200, description="Page size (1-200)")
    page: int = Field(default=0, ge=0, description="Page number (0-indexed)")


# ── System ───────────────────────────────────────────────────────────
class ListAppsInput(ListInput):
    pass


class GetAppActionsInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    app_id: int = Field(description="App ID to retrieve actions for")


# ── Containers ───────────────────────────────────────────────────────
class ListContainersInput(ListInput):
    status: str | None = Field(default=None, description="Filter by status (new, open, closed, resolved)")
    label: str | None = Field(default=None, description="Filter by label (e.g. events)")
    severity: str | None = Field(default=None, description="Filter by severity (high, medium, low)")
    sort: str | None = Field(default=None, description="Sort field (e.g. id, -create_time)")


class GetContainerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID")


class CreateContainerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(description="Container name")
    label: str = Field(default="events", description="Container label (e.g. events)")
    severity: str = Field(default="medium", description="Severity: high, medium, low")
    sensitivity: str | None = Field(default=None, description="TLP sensitivity: red, amber, green, white")
    status: str = Field(default="new", description="Status: new, open, closed, resolved")
    container_type: Literal["default", "case"] = Field(default="default", description="Container type")
    source_data_identifier: str | None = Field(default=None, description="SDI dedup key")
    owner_id: str | None = Field(default=None, description="Owner username or email")
    tags: list[str] | None = Field(default=None, description="Tags to apply")
    run_automation: bool = Field(default=False, description="Trigger active playbooks on creation")


class UpdateContainerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID to update")
    status: str | None = Field(default=None, description="New status")
    severity: str | None = Field(default=None, description="New severity")
    sensitivity: str | None = Field(default=None, description="New sensitivity")
    owner_id: str | None = Field(default=None, description="New owner")
    tags: list[str] | None = Field(default=None, description="Replace tags")


class GetContainerAuditInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID")
    sort: str | None = Field(default=None, description="Sort field")


# ── Artifacts ────────────────────────────────────────────────────────
class ListArtifactsInput(ListInput):
    container_id: int | None = Field(default=None, description="Filter by container ID")


class CreateArtifactInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container to attach artifact to")
    name: str = Field(default="artifact", description="Artifact name")
    label: str = Field(default="event", description="Artifact label")
    cef: dict = Field(description="CEF fields (e.g. sourceAddress, fileHash)")
    cef_types: dict | None = Field(default=None, description="CEF type overrides (e.g. {sourceAddress: [ip]})")
    tags: list[str] | None = Field(default=None, description="Tags")
    run_automation: bool = Field(default=True, description="Trigger playbooks (set false for batch except last)")


class GetArtifactInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    artifact_id: int = Field(description="Artifact ID")


# ── Playbooks ────────────────────────────────────────────────────────
class ListPlaybooksInput(ListInput):
    active: bool | None = Field(default=None, description="Filter by active status")
    name: str | None = Field(default=None, description="Filter by playbook name (contains)")


class RunPlaybookInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID to run playbook against")
    playbook_id: int | None = Field(default=None, description="Playbook ID (use this OR playbook_name)")
    playbook_name: str | None = Field(default=None, description="Playbook name as repo/name (use this OR playbook_id)")
    scope: Literal["all", "new"] = Field(default="all", description="Artifact scope: all or new")


class GetPlaybookRunInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    playbook_run_id: int = Field(description="Playbook run ID")


class ListPlaybookRunsInput(ListInput):
    container_id: int | None = Field(default=None, description="Filter by container ID")


class CancelPlaybookRunInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    playbook_run_id: int = Field(description="Playbook run ID to cancel")


# ── Actions ──────────────────────────────────────────────────────────
class RunActionInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action: str = Field(description="Action name (e.g. 'geolocate ip')")
    container_id: int = Field(description="Container ID")
    action_type: Literal["investigate", "contain", "correct", "generic"] = Field(
        default="investigate", description="Action type"
    )
    targets: list[dict] = Field(
        description="Targets list: [{assets: [name], parameters: [{key: value}]}]"
    )


class GetActionRunInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action_run_id: int = Field(description="Action run ID")


class ListActionRunsInput(ListInput):
    container_id: int | None = Field(default=None, description="Filter by container ID")


class CancelActionRunInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    action_run_id: int = Field(description="Action run ID to cancel")


# ── Indicators ───────────────────────────────────────────────────────
class ListIndicatorsInput(ListInput):
    timerange: str | None = Field(default=None, description="Time range: last_30_days, last_7_days, etc.")
    sort: str | None = Field(default=None, description="Sort field")


class GetIndicatorInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    indicator_id: int = Field(description="Indicator ID")


class GetIndicatorByValueInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    indicator_value: str = Field(description="Indicator value (e.g. IP, hash, domain)")


class GetIndicatorArtifactsInput(ListInput):
    indicator_id: int = Field(description="Indicator ID")


class GetTopIndicatorsInput(ListInput):
    pass


# ── Notes ────────────────────────────────────────────────────────────
class AddNoteInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID")
    title: str = Field(description="Note title")
    content: str = Field(description="Note content (supports markdown)")
    note_type: Literal["general", "fact"] = Field(default="general", description="Note type")
    phase_id: int | None = Field(default=None, description="Workbook phase ID (optional)")


class ListNotesInput(ListInput):
    container_id: int | None = Field(default=None, description="Filter by container ID")


class GetNoteInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    note_id: int = Field(description="Note ID")


# ── Comments ─────────────────────────────────────────────────────────
class AddCommentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    container_id: int = Field(description="Container ID")
    comment: str = Field(description="Comment text")


class ListCommentsInput(ListInput):
    container_id: int | None = Field(default=None, description="Filter by container ID")


# ── Custom Lists ─────────────────────────────────────────────────────
class ListAllListsInput(ListInput):
    pass


class GetListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name_or_id: str = Field(description="List name or numeric ID")


class GetListFormattedInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(description="List name")


class UpdateListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name_or_id: str = Field(description="List name or numeric ID")
    append_rows: list[list[str]] | None = Field(default=None, description="Rows to append")
    delete_rows: list[int] | None = Field(default=None, description="Row indices to delete")
    update_rows: dict[str, list[str]] | None = Field(default=None, description="Row index -> new values")


class CreateListInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(description="List name")
    content: list[list[str]] = Field(description="2D array of rows")


# ── Approvals ────────────────────────────────────────────────────────
class ListApprovalsInput(ListInput):
    status: str | None = Field(default="pending", description="Filter by status (e.g. pending)")


class RespondToApprovalInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    task_id: int = Field(description="Workbook task ID")
    response_value: str = Field(description="Response value (e.g. approve, decline)")


# ── Assets ───────────────────────────────────────────────────────────
class ListAssetsInput(ListInput):
    product_name: str | None = Field(default=None, description="Filter by product name")
    product_vendor: str | None = Field(default=None, description="Filter by product vendor")


class GetAssetInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    asset_id: int = Field(description="Asset ID")
