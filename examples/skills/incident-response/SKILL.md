---
name: incident-response
description: |
  Guide for handling production incidents effectively. Use when responding to
  outages, debugging production issues, or establishing incident management
  processes. Covers detection, response, communication, and post-mortems.
version: 1.0.0
tags: [incident, outage, production, on-call, sre, debugging]
category: devops/reliability
trigger_phrases:
  - "production down"
  - "service outage"
  - "incident response"
  - "on-call"
  - "post-mortem"
  - "site down"
  - "server crash"
  - "SEV1"
  - "emergency"
  - "pager alert"
variables:
  severity:
    type: string
    description: Incident severity level
    enum: [sev1, sev2, sev3, all]
    default: all
  phase:
    type: string
    description: Current incident phase
    enum: [detection, response, resolution, postmortem, all]
    default: all
  team_size:
    type: string
    description: Size of the on-call team
    enum: [solo, small, large]
    default: small
---

# Incident Response Guide

## Incident Philosophy

**Stay calm. Communicate clearly. Fix forward.**

```
The goal during an incident is NOT to find the root cause.
The goal is to RESTORE SERVICE as quickly as possible.

Root cause analysis comes AFTER the incident is resolved.
```

> "In an incident, every minute of downtime costs money and trust. Speed matters."

---

## Severity Definitions

| Severity | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| **SEV1** | Critical - Service down | < 15 min | Complete outage, data loss, security breach |
| **SEV2** | Major - Degraded service | < 30 min | Partial outage, severe performance issues |
| **SEV3** | Minor - Limited impact | < 4 hours | Feature broken, minor performance degradation |
| **SEV4** | Low - Minimal impact | Next business day | Cosmetic issues, minor bugs |

---

{% if phase == "detection" or phase == "all" %}
## Phase 1: Detection

### Alert Triage

When an alert fires:

```
1. ACKNOWLEDGE the alert (stops escalation)
2. ASSESS the impact:
   - Is the service actually down?
   - How many users affected?
   - Is it getting worse?
3. CLASSIFY severity (SEV1-4)
4. DECIDE: Handle alone or escalate?
```

### Initial Assessment Checklist

```bash
# Quick health checks
curl -I https://api.example.com/health    # Is the service responding?
curl https://status.example.com           # Check status page

# Recent changes
git log --oneline -10                      # Recent deployments?
kubectl rollout history deployment/api    # K8s rollout history

# Resource status
kubectl get pods -n production            # Pod status
kubectl top pods -n production            # Resource usage

# Error rates
# Check your monitoring dashboard for:
# - Error rate spike
# - Latency increase
# - Traffic anomalies
```

### When to Escalate

```
ESCALATE IMMEDIATELY if:
- [ ] Service is completely down
- [ ] Data loss or corruption possible
- [ ] Security breach suspected
- [ ] You can't diagnose within 15 minutes
- [ ] Multiple services affected
- [ ] Customer-facing impact is growing

HOW TO ESCALATE:
1. Page the on-call lead
2. Create incident channel (Slack: #inc-YYYYMMDD-brief-desc)
3. Post initial assessment in channel
```

{% endif %}

{% if phase == "response" or phase == "all" %}
## Phase 2: Response

### Incident Roles

{% if team_size == "solo" %}
**Solo Response** (when you're alone):

```
You wear all hats:
1. Investigate the issue
2. Communicate status updates
3. Implement the fix
4. Document as you go

Tips for solo response:
- Set a timer for status updates (every 15 min)
- Don't go down rabbit holes - timebox investigations
- Ask for help early if stuck
- Use templates for communication
```

{% elif team_size == "small" %}
**Small Team Roles** (2-4 people):

| Role | Responsibility |
|------|----------------|
| **Incident Commander (IC)** | Coordinates response, makes decisions, manages communication |
| **Tech Lead** | Investigates and implements fixes |
| **Communicator** | Updates stakeholders, status page, customers |

```
IC responsibilities:
- Runs the incident call
- Assigns tasks
- Removes blockers
- Decides on actions
- Calls for escalation/de-escalation
```

{% else %}
**Large Team Roles** (5+ people):

| Role | Responsibility |
|------|----------------|
| **Incident Commander** | Overall coordination and decision making |
| **Tech Lead** | Technical investigation lead |
| **Operations Lead** | Infrastructure and deployment actions |
| **Communications Lead** | Internal and external communications |
| **Scribe** | Documents timeline and actions |

```
Large incident coordination:
- Dedicated video/voice bridge
- IC speaks last, synthesizes info
- Clear handoffs between shifts
- Regular sync points (every 15-30 min)
```

{% endif %}

### Incident Communication Template

**Internal Update:**
```
🚨 INCIDENT UPDATE - [SEVERITY] - [Brief Description]

Status: [Investigating | Identified | Monitoring | Resolved]
Impact: [Who/what is affected]
Current Actions: [What we're doing now]
Next Update: [Time of next update]

Timeline:
- HH:MM - [Event]
- HH:MM - [Event]
```

**External Status Page:**
```
[Investigating] We are investigating reports of [issue].

[Identified] We have identified the cause of [issue].
A fix is being implemented.

[Monitoring] A fix has been deployed. We are monitoring the results.

[Resolved] This incident has been resolved.
Services are operating normally.
```

### Response Actions

{% if severity == "sev1" or severity == "all" %}
#### SEV1 Response Protocol

```
IMMEDIATE ACTIONS (first 15 minutes):
1. [ ] Page all required responders
2. [ ] Start incident bridge (video call)
3. [ ] Create incident channel
4. [ ] Assess blast radius
5. [ ] Consider rollback/failover

STABILIZATION (15-60 minutes):
1. [ ] Identify contributing factors
2. [ ] Implement mitigation (not necessarily fix)
3. [ ] Update status page
4. [ ] Notify affected customers
5. [ ] Document actions in real-time

COMMUNICATION cadence: Every 15 minutes
```

{% endif %}

{% if severity == "sev2" or severity == "all" %}
#### SEV2 Response Protocol

```
INITIAL RESPONSE (first 30 minutes):
1. [ ] Acknowledge and assess
2. [ ] Create incident channel if needed
3. [ ] Begin investigation
4. [ ] Update status page if customer-facing

RESOLUTION (30-120 minutes):
1. [ ] Identify root cause
2. [ ] Implement fix
3. [ ] Verify fix effectiveness
4. [ ] Monitor for recurrence

COMMUNICATION cadence: Every 30 minutes
```

{% endif %}

### Common Mitigation Strategies

```yaml
Rollback:
  when: "Recent deployment caused the issue"
  action: "kubectl rollout undo deployment/api"
  risk: "Loses new features, may not fix if data-related"

Restart:
  when: "Memory leak, stuck process, corrupted state"
  action: "kubectl delete pod <pod-name>"
  risk: "Temporary additional errors during restart"

Scale Up:
  when: "Overwhelmed by traffic"
  action: "kubectl scale deployment/api --replicas=10"
  risk: "Doesn't fix underlying issue, increases cost"

Feature Flag:
  when: "Specific feature causing issues"
  action: "Disable feature via flag"
  risk: "Users lose access to feature"

Failover:
  when: "Regional/zonal outage"
  action: "Switch traffic to backup region"
  risk: "May have stale data, increased latency"

Rate Limit:
  when: "Being overwhelmed/attacked"
  action: "Enable aggressive rate limiting"
  risk: "May block legitimate users"
```

{% endif %}

{% if phase == "resolution" or phase == "all" %}
## Phase 3: Resolution

### Verification Checklist

Before declaring resolved:

```
Service Health:
- [ ] All health checks passing
- [ ] Error rate back to baseline
- [ ] Latency back to normal
- [ ] No elevated resource usage

User Impact:
- [ ] Users can complete key flows
- [ ] No new error reports coming in
- [ ] Support queue not growing

Monitoring:
- [ ] Alerts have cleared
- [ ] Dashboards show normal patterns
- [ ] Logs show normal behavior
```

### Incident Closure

```
1. Update status page to "Resolved"
2. Send final internal update
3. Thank responders
4. Schedule post-mortem (within 48-72 hours)
5. Create follow-up tickets for:
   - Root cause fix (if mitigation was temporary)
   - Monitoring improvements
   - Documentation updates
```

{% endif %}

{% if phase == "postmortem" or phase == "all" %}
## Phase 4: Post-Mortem

### Blameless Post-Mortem Culture

```
BLAMELESS means:
- Focus on SYSTEMS, not individuals
- "What allowed this to happen?" not "Who caused this?"
- Assume everyone did their best with available information
- Improvement over punishment

NOT BLAMELESS:
- "John deployed bad code"
- "The team was careless"
- "This should never have happened"

BLAMELESS:
- "The deployment pipeline lacked integration tests"
- "The runbook was outdated"
- "The alert didn't fire because threshold was wrong"
```

### Post-Mortem Template

```markdown
# Incident Post-Mortem: [Title]

## Summary
- **Date**: YYYY-MM-DD
- **Duration**: X hours Y minutes
- **Severity**: SEV-X
- **Impact**: [Brief description of user/business impact]

## Timeline (all times in UTC)
| Time | Event |
|------|-------|
| HH:MM | First alert fired |
| HH:MM | Incident declared |
| HH:MM | Root cause identified |
| HH:MM | Mitigation deployed |
| HH:MM | Service restored |
| HH:MM | Incident resolved |

## Root Cause
[Technical explanation of what caused the incident]

## Contributing Factors
1. [Factor 1 - e.g., "Missing input validation"]
2. [Factor 2 - e.g., "Insufficient monitoring"]
3. [Factor 3 - e.g., "Outdated runbook"]

## What Went Well
- [Thing that helped during response]
- [Process that worked effectively]

## What Could Be Improved
- [Thing that hindered response]
- [Process that needs improvement]

## Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| Add input validation to API | @engineer | P1 | YYYY-MM-DD |
| Add alert for error rate | @sre | P1 | YYYY-MM-DD |
| Update runbook | @oncall | P2 | YYYY-MM-DD |

## Lessons Learned
[Key takeaways for the team and organization]
```

### Calculating Impact

```python
# Metrics to include in post-mortem

# Duration
total_duration = resolved_time - detected_time
time_to_detect = detected_time - start_time  # If known
time_to_mitigate = mitigated_time - detected_time

# User impact
affected_users = unique_users_with_errors()
error_rate = errors / total_requests * 100
failed_transactions = count_failed_transactions()

# Business impact
estimated_revenue_loss = failed_transactions * avg_transaction_value
support_tickets_created = count_tickets_during_incident()
sla_breach = check_sla_breach()
```

{% endif %}

---

## Debugging Production Issues

### Safe Investigation Commands

```bash
# Kubernetes debugging
kubectl logs <pod> --tail=100                    # Recent logs
kubectl logs <pod> --since=5m                    # Last 5 minutes
kubectl logs <pod> -p                            # Previous container logs
kubectl describe pod <pod>                        # Pod events and status
kubectl exec -it <pod> -- /bin/sh                # Shell into container

# Database (read-only!)
SELECT count(*) FROM orders WHERE created_at > now() - interval '1 hour';
EXPLAIN ANALYZE SELECT ...;                      # Query performance

# Network
curl -v https://api.example.com/health           # Verbose HTTP
dig api.example.com                              # DNS resolution
traceroute api.example.com                       # Network path
```

### What NOT to Do During Incidents

```
❌ DON'T:
- Run untested fixes in production
- Make multiple changes at once
- Skip communication updates
- Investigate without sharing findings
- Delete logs or evidence
- Point fingers
- Panic

✅ DO:
- Make one change at a time
- Document everything
- Communicate frequently
- Ask for help
- Roll back if unsure
- Stay calm
```

---

## On-Call Best Practices

### Sustainable On-Call

```
Schedule:
- Maximum 1 week on-call at a time
- At least 1 week between on-call shifts
- Primary and secondary on-call
- Clear escalation path

Compensation:
- Paid for on-call time
- Comp time for incidents
- No expectation of work next day after night incident

Support:
- Runbooks for common issues
- Access to all necessary systems
- Clear escalation contacts
- Permission to wake people up for SEV1
```

### On-Call Handoff Checklist

```markdown
## On-Call Handoff: [Date]

### Current State
- [ ] All services healthy
- [ ] No ongoing incidents
- [ ] No scheduled maintenance

### Recent Incidents
- [Date]: [Brief description and current state]

### Upcoming Risks
- [Deployment scheduled for X]
- [Marketing campaign starting Y]

### Things to Watch
- [Service X has been flaky]
- [Alert Y has been noisy - ticket #123]

### Contacts
- Escalation: [Name, Phone]
- Database: [Name, Phone]
- Security: [Name, Phone]
```

---

## Incident Metrics

### Key Metrics to Track

```
MTTD (Mean Time To Detect)
- Time from incident start to first alert
- Goal: < 5 minutes for SEV1

MTTA (Mean Time To Acknowledge)
- Time from alert to human response
- Goal: < 5 minutes for SEV1

MTTR (Mean Time To Resolve)
- Time from detection to resolution
- Goal: < 1 hour for SEV1

Incident Frequency
- Number of incidents per week/month
- Goal: Decreasing trend

Post-mortem Completion Rate
- % of incidents with completed post-mortems
- Goal: 100% for SEV1/SEV2
```
