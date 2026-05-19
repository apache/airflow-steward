# Step 3 output spec

The model must produce a completion summary with the following
structure:

- `candidate`: candidate name and Apache ID
- `project`: project name
- `scenario`: one of "new-committer", "committer-to-pmc", "direct-to-pmc"
- `communications_sent`: list of sent communications (each: type + recipient)
- `karma_granted`: list of completed karma items
- `pending_items`: list of items still waiting (empty list if all done)
- `onboarding_complete`: boolean — true only when pending_items is empty

When `pending_items` is non-empty:
- Each item must name what is pending and what the nominator needs
  to do next (e.g. "wait for secretary to confirm ICLA processing")
- `onboarding_complete` must be false
