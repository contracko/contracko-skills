# Onboarding

## Connect with consent

Follow the [README connection and consent steps](https://github.com/contracko/contracko-skills#install). Consent belongs to the user: do not automate it or ask for credentials in chat. In a non-interactive session, report browser sign-in as blocked. Connecting imports nothing. Follow the [core connection checks](../SKILL.md#connect-and-discover).

## Add your first contract

Ask the user to attach their own file or give its path, explain that Contracko will extract dates and terms, and ask permission before reading or uploading. Use [managed import and the client transfer path](importing-contracts.md). For an empty workspace, use the [core tool search](../SKILL.md#find-the-right-tool), not guessed calls.

**Done when:** the contract reads back in the intended workspace and the user knows the extraction is [pending review](reviewing-ai-analysis.md#pending-review-and-reconciliations).

## What extraction gives you automatically

Worth telling the user, because it changes what they should do first. On a plain NDA, in a workspace with no configuration at all, the import produced:

- title, start and end dates, renewal and notice terms
- both parties, created as counterparty records and linked with roles
- a new contract type, with custom fields inferred from the document
- governing law, jurisdiction, liability summary, notice instructions
- a full analysis with obligations and risks, through `clm_get_contract_analysis`

So for a first-time user with a folder of contracts: import first, configure after. Hand-built contract types are work the extraction was going to do, and then has to reconcile against. After the batch lands, follow [types and fields](organising-the-workspace.md#import-before-modelling).

