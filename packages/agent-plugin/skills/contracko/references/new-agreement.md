# A new agreement

Most of this flow is app work today. Help with the questionnaire and drafting text, explain the app-only steps, then file the executed copy through [imports](importing-contracts.md).

## Human legal review

**A contract a model wrote is a draft, and it needs a human with legal competence to review it before anyone signs.** Say this plainly when the user is about to act on the output, and again at the drafting handoff. Use an in-house lawyer or jurist for material deals, external counsel where value or jurisdiction warrants it, and at minimum somebody whose job is to read contracts. Fluent prose does not prove enforceability or consistency.

Start from a template the organisation has already had reviewed. Ask what they use before offering to write from scratch; a first precedent needs proper review. Draft clauses, summaries, negotiation positions and redline arguments when asked, but never present them as legal advice.

## Questionnaire

Ask in this order and stop when the user has decided:

1. Which owned entity and counterparty? Resolve existing parties with `clm_list_parties`; [party conventions](organising-the-workspace.md#import-before-modelling) explain the records.
2. What is bought or sold, for what value, currency and billing rhythm?
3. Start date: signature or fixed date? Fixed end or open-ended? Automatic renewal, and for how long?
4. **Notice period: ask explicitly, never default it.** Confirm the resulting notice deadline.
5. Liability cap and mutuality; governing law and jurisdiction; termination for convenience and notice; relevant confidentiality, data-processing and IP terms.
6. Contract type and required custom fields: check `clm_list_contract_types`.

Read the answers back before drafting.

## Handoff: destination and consent

Signature takes days or weeks. A draft has no filed Contracko record yet, so offer a handoff the next conversation can use. It can contain sensitive details: show the fields you plan to record and ask the user to choose a destination:

- an exact local path the user names and can secure
- an encrypted vault or notebook destination the user names
- a chat-only copy the user saves themselves

State the exact destination and contents, then ask for explicit consent before writing. Do not write a handoff to the current working directory, a temporary directory, plugin data, logs, transcripts, a remote store, or Contracko without that choice and consent. Never add credentials or full contract text unless the user asks for it.

If the user does not choose a destination and give consent, do not persist the handoff. Provide a redacted block for the user to save themselves and say that it is not stored by the agent.

For an approved secure destination, record the parties and owned entity, dates/open-ended status, renewal term, notice period and deadline, value/currency/billing rhythm, liability cap, governing law/jurisdiction, filing type, and rejected terms with reasons. In a later conversation, read that handoff before repeating questions.

## Drafting and signature: app steps

Creating a contract from a template, filling fields, changing status, sending for signature, checking signature status and chasing signers have no current MCP tool. Name the app step. Do not claim you created or sent anything in Contracko. Text you draft goes with the user and needs legally competent review before signature.

If the user asks where a contract is, check whether it is already filed but unsigned with `clm_list_contracts` and `clm_get_contract` before assuming it is absent.

## File the executed copy and set the notice reminder

Once the signed copy exists, follow [managed import](importing-contracts.md#managed-import), then compare the extracted terms with the approved handoff. Surface differences in notice, renewal or liability instead of silently accepting extraction. Explain [pending-review status](reviewing-ai-analysis.md#pending-review-and-reconciliations). If a folder was requested, follow [confirmed filing](organising-the-workspace.md#folders-and-filing).

Then follow [notifications](notifications.md): prefer the `notice` system event when the user wants to keep the option to exit, or `end` for a renewal alert. Confirm the recipient and timing there.

**Done when:** the signed copy reads back in the intended workspace, discrepancies and review status are clear, and the requested notification reads back correctly.
