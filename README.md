# Contracko skills

These skills teach an AI assistant to work in your [Contracko](https://contracko.com) workspace.

Some of that the assistant can do itself. Some of it you still do in the Contracko app. Each job below says which is which, so the assistant does not pretend to have clicked a button that is not there.

## Before you start

Connecting Contracko to an AI product sends contract data to that product's AI provider. Contracko cannot control what that provider does with it. Turn off model training in the provider's settings before working with real contracts.

## What you can ask

### Bring contracts in

"Import the PDFs in this folder." "Onboard us from Google Drive / SharePoint / Box."

The assistant finds the files (it uses whatever disk or cloud access it already has — Contracko does not open Drive or SharePoint itself), checks the list with you, and imports them. Contracko then extracts dates, parties, types and analysis.

You confirm extractions that land as pending review, and you put contracts into folders in the app.

### What is coming up

"What needs notice in the next 90 days?" "Which contracts end this quarter?" "What is due for annual review?"

The assistant reads notice dates, end dates and renewal flags and gives you the list today.

Reminders that should fire later, when nobody is asking, are set on the contract in Contracko.

### Compare these

"Compare these two vendor proposals." "What changed between this draft and the last redline?"

The assistant puts both sides next to each other: the records, the analysis, and quoted clauses.

Scoring a contract against a playbook you keep in Contracko is still in the app. There is no automatic redline-diff over this connection.

### Audit for risk

"Where is liability uncapped?" "What are the material risks in this MSA?"

The assistant uses Contracko's analysis plus the sentence in the document that supports it.

Measuring a contract against your house playbook is in the app.

### File and type them

"Set up proper contract types." "How should we folder these?"

The assistant shapes contract types and custom fields, and corrects metadata (type, dates, parties, value). It can see which folder a contract is in. It cannot move it.

You create the folder tree and drag contracts into it in Contracko.

### Priorities and gaps

"What should we look at this month?" "Where is the portfolio thin?"

The assistant goes through the workspace and ranks what is urgent, what is missing (dates, types, review, value), and where vendor spend sits.

Saved reports and clickable list filters stay in the app. The assistant cannot filter the list on the server yet, so a large workspace takes a full pass.

### Start a new agreement

"Help me draft an NDA and file it when it is signed."

The assistant runs through what the contract has to say, then files the signed copy.

Writing it from a template and sending it for signature happen in Contracko.

## Connect

One line, to any assistant:

> Fetch and execute the setup instructions at https://contracko.com/agent-setup/prompt.md

That installs the skills and walks through connecting Contracko. Use [the HTTPS git URL](https://github.com/contracko/contracko-skills.git) if you add this as a Claude Code marketplace yourself — the short `owner/repo` form fails on many machines.

Turn off model training before you point it at real contracts.

MIT licensed.
