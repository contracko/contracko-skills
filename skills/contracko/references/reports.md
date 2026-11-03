# Reports

Reports are dashboards of blocks (charts, tables and totals) built from the contracts the connected member can see. Use the `report_*` tools to read, build and manage them. The [tool index](tool-index.md#reports) lists every tool and scope.

Reports must be enabled for the organisation, and the connected user must still be a workspace member. If Reports is off, relay the availability message and stop; do not retry. Write calls also need subscription write access. Scope alone grants neither edit nor sharing rights: the member's current rights on each dashboard still apply. Queries only count contracts the member can see. The ordinary API rate limit applies.

## What you can do

| The user wants | Tools |
|---|---|
| See or open dashboards | `report_list_dashboards` (optional title search), `report_get_dashboard` (blocks and current rights) |
| Find out what a block can show | `report_list_templates`, `report_describe_fields` |
| Try a block before saving | `report_preview_block` |
| Build a dashboard | `report_create_dashboard` (1 to 50 blocks, created private), `report_add_block` |
| Change a dashboard | `report_update_block` (replaces one block's configuration), `report_rename_dashboard`, `report_remove_block` |
| Copy a dashboard | `report_duplicate_dashboard` (new private dashboard owned by the member) |
| Let Clara draft one | `report_start_generation`, then `report_get_generation_status` |
| Change who can see it | `report_get_sharing`, `report_list_sharing_principals`, `report_set_sharing` |
| Delete a dashboard | `report_propose_dashboard_deletion`, then `report_delete_dashboard` |

Read tools need `contract:read`. Write tools need `contract:write`. `report_propose_dashboard_deletion` reads only and needs `contract:read`.

## Build from a preview

1. Call `report_list_templates` and `report_describe_fields` for valid block shapes, field references and operations. Do not invent field references.
2. Call `report_preview_block` and show the user what it returns. An invalid block returns precise issues and saves nothing; fix them and preview again.
3. Save with `report_create_dashboard` or `report_add_block` only after the user agrees.

Create, add and generation calls are not safe to repeat blindly if delivery is uncertain. Re-read the dashboard first.

## Generation with Clara

`report_start_generation` takes a `mode` of `dashboard`, `blocks` or `adjust` and a prompt of 1 to 2,000 characters. `blocks` and `adjust` need a dashboard ID; `adjust` also needs a block ID. The result saves automatically, so confirm the request before starting.

Clients that support tasks receive the result as a task. Otherwise poll `report_get_generation_status`, optionally with a bounded wait. Queued and running are pending; succeeded and failed are final. Only the user who started a generation can read it, and only while they still have access to the dashboard. Cancelling a task stops delivery, not the generation.

## Sharing

`report_set_sharing` replaces the visibility and the complete grant set. Any grant you leave out is revoked. Read the current state with `report_get_sharing` first, take eligible people and groups from `report_list_sharing_principals`, send the full intended set, and get explicit approval before calling. It needs sharing rights on the dashboard. Group grants follow plan access.

## Deleting

Deletion is permanent and removes the dashboard and its blocks. Removing a single block with `report_remove_block` is also permanent.

1. Call `report_propose_dashboard_deletion`. It deletes nothing and returns ownership, sharing state, block count and a revision.
2. Show the user what will go and ask for explicit approval.
3. Call `report_delete_dashboard` with `approved: true` and the proposal's exact `expectedRevision`.

If the dashboard changed after the proposal, the revision no longer matches. Propose again and ask again.

## Examples

- "Show me my Reports dashboards, then add a block counting contracts that end in the next 90 days."
- "Build a private dashboard of contract value by type, preview each block first, and share it with the finance group once I have checked it."
