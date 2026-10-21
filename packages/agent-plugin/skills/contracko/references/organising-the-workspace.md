# Organising the workspace

## Import before modelling

Start with [import before modelling](onboarding.md#what-extraction-gives-you-for-free), then inspect `clm_list_contract_types` and `clm_list_parties`. Propose the field list and wait for confirmation before creating or changing it. A field earns its place only when it answers a real question. Use native dates, parties, and values rather than duplicate custom fields. Use `select` or `multi_select` with `config.options` for known answer sets.

`fieldKey` uses lowercase letters, digits, and underscores. `clm_update_contract_type` replaces the whole field set when `fields` is present, so send every field to retain. List before creating a type or party because duplicate names conflict. If a type write has `OUTCOME_UNKNOWN`, re-read its fields before retrying.

`isOwned` marks the user's own legal entity. `name` is the display name and `legalName` is the registered name. Resolve existing parties before creating another record.

`taxId` and `registrationNumber` hold an organisation's VAT or tax number and its company registration number. Set them only on a `company`, `non-profit`, or `government` party, never on an `individual`, and never put a personal identifier in them. Changing a party to `individual` needs both cleared in the same `clm_update_party` call.

## Folders and filing

Use `clm_list_folders` to discover only folders the user can see. It accepts `limit`, `parentFolderId`, and an opaque `continuation`. Omitting `parentFolderId`, or sending `parentFolderId: null`, lists only the visible root. Complete those root pages, then list and complete the child pages for every visible folder, recursively, to enumerate the visible tree. Completing root pages alone is not a full-tree result. For each parent, repeat the same parent and limit with the returned continuation until it is `null`. This is separate from contract pagination. Do not send a contract `cursor` to a folder call.

Folder paths contain visible ancestors only. A folder omitted from a list, or a failed lookup of a hidden folder, does not establish whether that folder exists. Do not claim a hidden folder exists or does not exist.

For a requested filing change:

1. Inspect the intended folder with `clm_get_folder` or select it from the visible list.
2. State the visible destination path and the contracts or folders that will change. Explain that moves can remove inherited access and reassign scheduled email notifications to the contract owner. A folder moved to root loses limited access; moving it back needs current permissions and does not restore that setting. Confirm the destination and every bulk change before writing.
3. Create a root or child folder with `clm_create_folder`, rename it with `clm_rename_folder`, or move it with `clm_move_folder` when the user asks.
4. File a contract with `clm_move_contract`. Send its visible destination UUID as `folderId`. Send `folderId: null` only when the user asks to unfile it.
5. Read back the changed folder or contract before claiming completion.

A contract's filing state is `filing.kind`: `unfiled`, `folder`, or `unavailable`. Every contract result has `folderId`: it is a visible UUID only when `filing.kind` is `folder`, otherwise `null`. `filing.folder.id` and `filing.folder.path` are available only when `filing.kind` is `folder`. `unavailable` is not `unfiled`; do not invent a hidden folder identifier. To audit unfiled contracts, page the relevant contract result and evaluate `filing.kind`; `folderId: null` is not a valid contract-list filter.

For contracts in a visible folder, follow [contract filters and pagination](portfolio-review.md#filter-first-then-page).

`clm_get_folder` shows a visible folder's visibility, limited-access state, permission, and bounded member details. `clm_get_contract_access` is a contract's read-only access overview. Neither changes permissions. Direct access changes and folder deletion happen in the Contracko app.

## Registers

[Notifications](notifications.md) owns events and email reminders; [portfolio review](portfolio-review.md#filter-first-then-page) owns contract filtering and pagination.

SaaS subscriptions, leases, permits, certificates, insurance policies, warranties, and domains use the same pattern: a type, countable fields, native renewal dates, and a notification. Follow the linked portfolio pagination rules.

For type generation or re-reads, inspect [tool effects](tool-index.md#type-generation-and-type-re-reads) first; review generated definitions in the normal editor.

**Done when:** requested configuration and filing changes read back correctly.
