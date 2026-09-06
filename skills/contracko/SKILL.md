---
name: contracko
description: Connects Contracko over MCP and organises the workspace: types, fields, counterparties, folders. Use for onboarding, filing, or whenever Contracko comes up.
---

# Contracko

Contracko is contract management: a repository of contracts with extracted dates, values, parties and AI analysis on top. Its MCP server lets an agent read and write that workspace directly.

This skill connects the server, structures the workspace, and routes everything else. Jobs (bring in, calendar, compare, audit, file, report) are in [references/workflows.md](references/workflows.md). Three siblings own the mechanics: [contracko-import](../contracko-import/SKILL.md), [contracko-review](../contracko-review/SKILL.md), [contracko-create](../contracko-create/SKILL.md).

The characteristic failure of this surface is **silence**. Scopes hide tools rather than refusing them, unknown keys are dropped rather than rejected, and broken configuration returns 200. Every rule below exists because something failed quietly. When a Contracko call surprises you, suspect a silent success before you suspect a bug.

## Say this once

In the first response of a session where Contracko is connected to an AI product that is not Contracko's own:

> Contract data will be sent to the AI provider running this session. Contracko cannot control what that provider does with it. Turn off model training in the provider's settings before working with real contracts.

Once, in full, early. The user is about to pipe legal documents through a third party and is entitled to know.

## Connect

Endpoint, all environments: `https://app.contracko.com/mcp`

Check the client for a Contracko server before adding one. Many users arrive here having already connected it from a connector directory, in which case the work is authentication rather than configuration, and adding a second entry gives them the same tools twice.

**OAuth is the default.** The server publishes protected-resource metadata, so any client with remote OAuth support registers itself, opens a browser, and takes the user through sign-in, workspace choice and scope consent. Nothing is copied by hand and no secret lands in a config file.

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp
```

Then `/mcp` in the session and authenticate. The browser does the rest.

**An MCP API key is the fallback**, for a headless client, CI, or a client without OAuth support. Settings > Integrations > API keys, purpose **MCP server**, scopes chosen at creation:

```bash
claude mcp add --transport http contracko https://app.contracko.com/mcp \
  --header "Authorization: Bearer YOUR_MCP_KEY"
```

An existing platform API key is not an MCP key: the **MCP server** purpose has to be selected when the key is created. A key is also bound to one workspace, where OAuth lets the user pick.

In a headless or non-interactive session OAuth cannot complete, because there is no browser and no consent panel. Report that as the blocker and stop; a key is the way through, and improvising around a sign-in is not.

### Scopes decide which tools exist

Tools are filtered out of the tool list entirely, so a missing scope looks exactly like a missing feature.

| Scope | What appears |
|---|---|
| any valid credential | `auth_validate` only |
| `parser:compute` | the 6 parser tools |
| `contract:read` | contract, type, party, comment and event reads, plus document search, document read and download URLs |
| `contract:write` | create, update (including bulk), import, ingest, extra documents, comments, events, reminders, and read |

**The consent screen belongs to the user.** They open it, they tick the boxes, they approve. Hand them the link and wait, and keep browser automation away from a sign-in and consent flow even where you have it: the point of the screen is that a human granted the access.

Tell them what to expect before they go, because the defaults are narrower than most people assume: `contract:write` is unticked by design. Approving without it leaves a connection that can read contracts and change nothing, and approving with only the parser box ticked leaves one where every contract tool has silently vanished, at which point the agent reports, correctly and uselessly, that contract management is unavailable. So: name the boxes that need ticking for the work they asked for, let them tick, and verify after.

### Verify before working

Tool names in this bundle are written bare. Address them by their server prefix where your client uses one, as `contracko:auth_validate`, matching the name the server was registered under. `auth_validate` in particular is generic enough to collide with another connected server.

Run `auth_validate` first, every session. It returns the workspace and the granted scopes.

Connecting is done when the workspace is the one the user meant **and** the granted scopes cover what they asked for. Where the user wants contract work and only `auth_validate` and parser tools exist, the credential is the problem: say so and point at the key's scopes or a fresh consent.

A key or OAuth grant on Phases 1–4 does not pick up later MCP actions on its own. If search, document read, download URLs, contract updates, events or reminders are missing while `contract:read` or `contract:write` is granted, the credential is on an older capability generation: a workspace admin confirms **Enable new MCP actions** on the key, or the user re-consents OAuth. Existing Phase 5 credentials already include events and reminders.

## Route the work

Job playbooks, including what is Phase 5 vs still in the app: [references/workflows.md](references/workflows.md).

| The user wants | Go to |
|---|---|
| import, onboard, migrate, files on disk / Drive / SharePoint / Box | [contracko-import](../contracko-import/SKILL.md), then types below |
| notice dates, end dates, annual review, reminders | [contracko-review](../contracko-review/SKILL.md) |
| compare proposals, A/B, redline versions | [contracko-review](../contracko-review/SKILL.md) |
| risk, liability, audit | [contracko-review](../contracko-review/SKILL.md) |
| folders, contract types, custom fields, organise | below |
| portfolio, priorities, gaps, vendor spend | [contracko-review](../contracko-review/SKILL.md) |
| a new agreement drafted, signed, filed | [contracko-create](../contracko-create/SKILL.md) |
| extract without filing as a contract | parser tools in [references/tool-index.md](references/tool-index.md) |

## Organising the workspace

What a contract *is* here, what you record about it, who it is with, where it lives, and what warns you before a date passes.

**Import first.** Extraction creates contract types, custom fields and counterparties from the documents themselves, so configuring an empty workspace by hand is work the import was going to do, and then has to reconcile against. Read what it built with `clm_list_contract_types` and `clm_list_parties`, then make the types *comprehensive*: every question they actually ask should have a field, as a `select` where the answers are a known set. Put the proposed field list in front of them before writing. Where they insist on configuring first, say that once and then do it their way.

### Contract types and custom fields

The type is the unit of configuration: it owns the field set, so "track X across our contracts" almost always means "add a field to a type". `clm_list_contract_types`, `clm_get_contract_type`, `clm_create_contract_type`, `clm_update_contract_type`.

Four rules the schema does not carry, each worth one failed call:

- `fieldKey` matches `^[a-z0-9_]+$`. Lowercase and underscores.
- Choices for `select` and `multi_select` live in `config.options`: `{"config": {"options": ["A", "B"]}}`. An `options` key at the top level of the field is accepted with a 200 and dropped, leaving a field with no choices and no error. Read the response back and confirm `config.options` survived.
- `fieldKey` is unique within a request. A duplicate returns a 500 saying the outcome is unknown; the outcome is that nothing was written, so fix the duplicate rather than retrying.
- `clm_update_contract_type` replaces the whole field set when `fields` is present and leaves it alone when `fields` is absent. To add one field, send every field you want to keep.

A duplicate type or party name returns a 409 whose message omits the name, so list before you create.

**Contracts, types and parties cannot be deleted over MCP, by design.** A wrong type stands until someone opens the app. Put a new type in front of the user before creating it, and prefer updating an existing one over adding a near-duplicate. Custom events and linked reminders *can* be deleted; that is a confirm-before-write, not an app handoff.

A field earns its place by answering a question someone asks: renewal owner, cost centre, licence seats, risk tier. Two traps. A field that restates something Contracko models natively (end date, notice period, counterparty, annual value) splits the same fact in two, and the native one is what the renewal logic reads. A free-text field where a `select` would do cannot be counted, so anything with a known set of answers gets `config.options`. Types available: `text`, `number`, `currency`, `percentage`, `date`, `boolean`, `select`, `multi_select`. Use `currency` and `percentage` where they fit rather than a bare `number`, since the unit is then part of the field instead of a convention someone has to remember.

### Counterparties

`clm_list_parties`, `clm_get_party`, `clm_create_party`, `clm_update_party`.

`isOwned` marks your own legal entity rather than the other side; get it wrong and every "who are we contracting with" answer inverts. `name` is what people call them, `legalName` is what the contract says, and matching a contract to a vendor later depends on keeping both. `clm_update_party` is partial, so omitted fields keep their values. Import creates parties on its own, so check for an existing record before adding one: merging duplicates is app work.

### Folders — app to move, MCP to prepare

Contracts carry a `folderId` you can read and cannot set. Creating folders and moving contracts is app work; it is not on the Phase 5 tool list. Metadata you *can* correct over MCP: `clm_update_contract` (one record) and `clm_bulk_update_contracts` (up to 100). Both need the exact `updatedAt` from the latest read as `expectedUpdatedAt`.

When someone asks for contracts organised they mean two things: the type and fields (yours), and the folder tree (theirs). Do your half, then write a tree they can click — typically by owned entity, then type, then vendor — naming which contracts you would put where. Do not claim to have filed them.

### Reminders

Reminders hang off an event on a contract. [contracko-review](../contracko-review/SKILL.md) owns listing dates and creating the alert. Renewal reminders target the contract `end` system event; do not invent a custom event for an ordinary renewal.

### Recurring registers

"Track our SaaS subscriptions", and equally leases, permits, certificates, insurance policies, warranties and domains, are one shape: a contract type per category, `select` fields for anything countable, the renewal date left in Contracko's native `endDate` and notice fields rather than a custom one, and a reminder on the `end` (or `notice`) system event. The register is then a page-through and filter, which [contracko-review](../contracko-review/SKILL.md) covers.

## Workflows run past the end of the tool list

Contracko does more than its MCP server exposes today, and the surface is rolling out in phases. The skills here describe complete workflows for that reason, marking the steps that are done in the app.

So: work the whole flow with the user. Where a step has a tool, call it. Where a step is named as an app step and no tool answers to it, say which step it is and where it happens, then carry on with the rest. What you never do is invent a call for a tool you cannot see, or tell a user a feature does not exist when what you mean is that this connection cannot reach it.

The register of which steps sit where is in [references/tool-index.md](references/tool-index.md), and your tool list outranks it.

## Reading the errors

The messages address a person looking at the web app. Translate before repeating.

| Response | What it means |
|---|---|
| 409 "conflicts with the current Contracko state" | a name is taken, or an idempotency key was reused with a different payload |
| 400 `code: "custom"`, no message | a cross-field rule failed; the named field is fine alone |
| 400 `too_big` / `invalid_format` | a limit or pattern the error withholds; the ones that bite are in this file and the sibling skills |
| 500 `OUTCOME_UNKNOWN` | usually validation escaping as a 500; re-read state before retrying |

## Two places to be literal

The server's own instructions cover tone, and they are in your context already. They leave two gaps worth naming, both cases where a smooth answer is a false one:

- **A capability that does not exist.** Report it as unavailable through this connection, name the nearest thing that is, and stop. Inventing a tool signature for a plausible feature is the most expensive mistake available here.
- **A write that did not land.** Read state back and report what is actually there.
