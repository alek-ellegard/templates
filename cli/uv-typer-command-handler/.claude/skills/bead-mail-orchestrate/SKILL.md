---
name: Bead-Mail-Orchestrate
description: Coordination protocol for orchestrators using beads (issue tracking) and agent mail (inter-agent messaging). Use proactively at session start when .beads/ exists and agent mail MCP is available. Enables multi-orchestrator scalability through claim-execute-release cycles.
---

# Purpose

Provide orchestrators with a structured workflow for coordinating work using beads and agent mail. Each orchestrator follows the same protocol, enabling natural coordination without central control.

**Core Mental Model**: Claim-Execute-Release Cycle
1. **Claim** - Announce intent via agent mail, wait for conflicts, reserve files
2. **Execute** - Run subagents in waves, commit after each wave
3. **Release** - Release reservations, send handoff, push to remote

**Complements**: This skill adds coordination protocol. Use alongside `claude:orchestrate` for agent mechanics (task decomposition, agent selection, prompt patterns).

## Variables

CLAIM_WAIT_SECONDS: 15
PROJECT_KEY: "{absolute path to working directory}"
HEARTBEAT_TRIGGER: "after each wave"

## Instructions

### Session Start Protocol

**ALWAYS** at session start when .beads/ exists:

1. Register on agent mail:
   ```
   macro_start_session(
     human_key=PROJECT_KEY,
     program="claude-code",
     model="{your model}",
     task_description="{brief task summary}"
   )
   ```

2. Check inbox for active orchestrators:
   ```
   fetch_inbox(project_key=PROJECT_KEY, agent_name=YOUR_NAME, include_bodies=true)
   ```

3. Read project context:
   ```
   read @AGENTS.md for beads commands
   bd ready to see available work
   bd stats for project health
   ```

### Claim Protocol

**ALWAYS** before starting work on an issue:

1. **Announce claim** via agent mail:
   ```
   send_message(
     to=["known agents or broadcast"],
     subject="CLAIM: {issue-ids}",
     body_md="Claiming {issues}. Will start in {CLAIM_WAIT_SECONDS}s unless conflict.",
     importance="high",
     ack_required=false
   )
   ```

2. **Wait for conflicts** - check inbox after CLAIM_WAIT_SECONDS

3. **Reserve files** before editing:
   ```
   file_reservation_paths(
     agent_name=YOUR_NAME,
     paths=["src/path/to/files/*.py"],
     exclusive=true,
     ttl_seconds=1800,
     reason="Working on {issue-id}"
   )
   ```

4. **If conflict** - negotiate or pick different work

5. **Update beads**:
   ```
   bd update {issue-id} --status=in_progress
   ```

### Execute Protocol

**Wave-based execution**:

1. Identify parallelizable work: `bd ready`
2. Launch subagents in parallel (single message, multiple Task calls)
3. Wait for all to complete
4. Close issues: `bd close {id1} {id2} ... --reason="..."`
5. Commit changes with descriptive message
6. Send heartbeat (see below)
7. Repeat until wave complete

**Commit after each wave** - preserves progress, enables handoff.

### Heartbeat Protocol

**ALWAYS** after each wave:

```
send_message(
  to=["known agents"],
  subject="STATUS: Wave N complete",
  body_md="""
  ## Progress
  - Completed: {issue-ids}
  - In progress: {issue-ids}
  - Blocked: {issue-ids or "none"}

  ## Files Reserved
  - {paths}

  ## Next
  - {what's next}
  """,
  importance="normal"
)
```

### Release Protocol

**ALWAYS** after completing work on claimed issues:

1. Release file reservations:
   ```
   release_file_reservations(agent_name=YOUR_NAME)
   ```

2. Sync beads: `bd sync`

3. Acknowledge any pending messages in inbox

### Session Close Protocol

**ALWAYS** before ending session:

```
read @AGENTS.md for full close checklist
```

Then execute:

1. `git status` - check what changed
2. `git add <files>` - stage changes
3. `bd sync` - commit beads changes
4. `git commit -m "..."` - commit code
5. `bd sync` - commit any new beads changes
6. `git push` - push to remote
7. Send handoff message:
   ```
   send_message(
     to=["known agents"],
     subject="OFFLINE: {agent_name} signing off",
     body_md="""
     ## Session Complete
     - Issues closed: {list}
     - Issues remaining: {list or "none"}

     ## Handoff Context
     - {any context next agent needs}

     ## Reservations
     - All released
     """,
     importance="normal"
   )
   ```

Work is **NOT DONE** until `git push` succeeds.

### NEVER Rules

- **NEVER skip claim protocol** - silent execution causes conflicts with other orchestrators
- **NEVER hold file reservations while idle** - release promptly after commit, re-reserve if needed
- **NEVER work without session start** - must register on agent mail before any work
- **NEVER proceed on conflict** - if another agent claims same work, negotiate or pick different issue
- **NEVER end session without push** - local commits are not complete work

## Workflow

1. **Session Start**
   - `macro_start_session` → register identity
   - `fetch_inbox` → check for active agents
   - `bd ready` → identify available work

2. **Claim**
   - `send_message` → announce claim
   - Wait CLAIM_WAIT_SECONDS
   - `fetch_inbox` → check for conflicts
   - `file_reservation_paths` → reserve files
   - `bd update --status=in_progress` → mark claimed

3. **Execute** (repeat per wave)
   - Launch parallel subagents
   - Wait for completion
   - `bd close` → close completed issues
   - `git commit` → save progress
   - `send_message` → heartbeat

4. **Release**
   - `release_file_reservations` → free files
   - `bd sync` → sync issue state
   - `acknowledge_message` → clear inbox

5. **Session Close**
   - Full commit cycle (see protocol above)
   - `send_message` → handoff
   - `git push` → finalize

## Cookbook

<If: No other agents in inbox>
<Then: You're likely the only orchestrator. Still follow protocol - others may join. Claim messages become audit trail.>

<If: Conflict on claim (another agent wants same issue)>
<Then:
  1. Check who claimed first (message timestamps)
  2. If you were first, proceed and message them
  3. If they were first, pick different issue from bd ready
  4. If simultaneous, negotiate via reply_message
>

<If: File reservation conflict>
<Then:
  1. Check who holds reservation: conflicts in file_reservation_paths response
  2. Message holder asking for release or ETA
  3. Pick different files/issues if blocked
  4. Use force_release_file_reservation only if holder inactive (last_active_ts stale)
>

<If: Long-running wave (>30 min)>
<Then: Send interim heartbeat with "still working on..." status. Renew file reservations if approaching TTL.>

<If: Session interrupted (crash, timeout)>
<Then:
  1. On restart, macro_start_session with same agent_name (if known) to resume
  2. Check inbox for messages sent while offline
  3. Check bd list --status=in_progress for orphaned claims
  4. Either complete or release orphaned work
>

<If: Need to hand off mid-work>
<Then:
  1. Commit all current progress
  2. bd update {issue} --status=open (release claim)
  3. release_file_reservations
  4. Send handoff message with full context
  5. bd sync && git push
>

<If: Inbox has unread messages at session start>
<Then: Read and acknowledge before claiming new work. May contain handoff context or conflict notices.>

<If: bd ready returns empty but issues remain>
<Then: Check bd blocked - may need to wait for dependencies. Message agents working on blockers for status.>

## Integration

Load alongside `claude:orchestrate`:

```
WHEN orchestrating with beads and agent mail
READ skill: claude:orchestrate (agent mechanics)
READ skill: claude:bead-mail-orchestrate (coordination protocol)
```

The orchestrate skill handles:
- Task decomposition
- Agent selection (haiku/sonnet/opus)
- Prompt patterns
- Failure handling

This skill handles:
- Multi-agent coordination
- Claim/release cycles
- File reservations
- Heartbeats and handoffs
