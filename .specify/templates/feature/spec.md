# [NNN-Feature Name]

## Executive Summary

> Describe in 2-3 sentences what cross-component feature this specification
> defines.
> Example: "This specification defines the OAuth authentication flow that
> integrates the Sign, User, and Session components."

## Normative References

- `.specify/memory/constitution.md` — Immutable project principles.
- [Relevant system specs: 000, 001, 002, 003, etc.]
- [Involved component specs]
- [Applicable agent skills]

---

## 1. Context and Motivation

### 1.1 Problem to Solve

[Describe the business or technical problem]

### 1.2 Target Users

| Role | Need |
|-----|-----------|
| Role 1 | Specific need |

### 1.3 Feature Scope

**In scope:**
- Functionality 1
- Functionality 2

**Out of scope (Non-Objectives):**
- Out-of-scope functionality 1
- Out-of-scope functionality 2

---

## 2. User Experience

### 2.1 User Flow (User Journey)

```text
[User] --[action 1]--> [State 1] --[action 2]--> [Result]
```

### 2.2 UI States

| State | Description | Trigger |
|--------|-------------|---------|
| State 1 | How it looks | What activates it |

### 2.3 Messages and Feedback

| Situation | User Message | Type |
|-----------|-------------------|------|
| Success | Message | success |
| Error 1 | Message | error |

---

## 3. Technical Design

### 3.1 Involved Components

| Component | UUID | Role in the Feature |
|------------|------|-------------------|
| Component 1 | `uuid_xxx` | What it provides |
| Component 2 | `uuid_yyy` | What it provides |

### 3.2 Contracts Between Components

```text
Component A --[API/Event/Data]--> Component B
```

| Interaction | Type | Contract |
|-------------|------|----------|
| A -> B | [API/Event] | [Description] |

### 3.3 Shared Data

| Data | Source | Consumer | Format |
|------|--------|------------|---------|
| Data 1 | Component A | Component B | JSON/Schema |

---

## 4. Implementation

### 4.1 Changes by Component

#### Component 1 (UUID: `uuid_xxx`)

| Aspect | Change | Location |
|---------|--------|-----------|
| Routes | [New/Modified] | `route/routes.py` |
| Handlers | [New/Modified] | `route/*.py` |
| Templates | [New/Modified] | `neutral/route/root/...` |
| Assets | [New/Modified] | `static/` |
| Schema | [New/Modified] | `route/schema.json` |
| Models | [New/Modified] | `model/*.json` |

#### Component 2 (UUID: `uuid_yyy`)

[Same structure]

### 4.2 Implementation Order

> Fill this section only if the feature requires phased execution, temporary
> dependencies, or coordination between components.

1. Step 1 (foundational for the next ones)
2. Step 2 (depends on 1)
3. Step 3 (depends on 1 and 2)

---

## 5. Security

### 5.1 Attack Surface

| Vector | Mitigation |
|--------|------------|
| Vector 1 | Mitigation |

### 5.2 Security Controls

- [ ] Input validation in all handlers
- [ ] CSRF protection for forms
- [ ] Rate limiting on sensitive routes
- [ ] Output sanitization in templates
- [ ] CSP-compatible handling for new scripts/styles

### 5.3 Authorization

| Route | Auth Required | Minimum Role |
|------|----------------|------------|
| Route 1 | Yes/No | `role_name` |

---

## 6. Testing

### 6.1 Testing Strategy

| Type | Focus | Tool |
|------|---------|-------------|
| Unit | Business logic | pytest |
| Integration | Interaction between components | pytest + HTTP client |
| E2E | Complete user flow | Playwright |
| Visual | UI regression | Comparative screenshots |

### 6.2 Test Scenarios

| ID | Scenario | Expected Result | Priority |
|----|-----------|-------------------|-----------|
| 1 | Full successful flow | User reaches goal | High |
| 2 | Error at step X | Appropriate message, recovery | High |
| 3 | User without permissions | Redirect/denial | Medium |

### 6.3 Test Data

```json
{
  "test_case_1": {
    "input": { ... },
    "expected": { ... }
  }
}
```

### 6.4 Execution Commands

```bash
source .venv/bin/activate

# Feature tests
pytest [feature-test-targets] -v

# Involved component tests
pytest [component-test-targets] -v
```

---

## 7. Acceptance Criteria

### 7.1 Functional

- [ ] AC1: [Measurable description]
- [ ] AC2: [Measurable description]
- [ ] AC3: [Measurable description]

### 7.2 Non-Functional

- [ ] Performance: [Metric]
- [ ] Accessibility: WCAG 2.1 AA
- [ ] Responsive: [Supported breakpoints]

### 7.3 Technical

- [ ] Test coverage >= [X]%
- [ ] No critical vulnerabilities (`bandit`, `safety`)
- [ ] Linting with no errors (`pylint`, `mypy`)

---

## 8. Release / Rollout

### 8.1 Release Checklist

> Fill this section only if the feature requires controlled deployment,
> progressive rollout, communication, or specific monitoring.

- [ ] Feature flag configured (if applicable)
- [ ] Monitoring and alerts configured
- [ ] User documentation updated
- [ ] Rollback plan documented

### 8.2 Success Metrics

> Fill this section only if the feature defines observable post-release goals.

| Metric | Goal | Measurement Method |
|---------|----------|-------------------|
| Metric 1 | Target value | Tool |

---

## 9. Post-Release

### 9.1 Identified Technical Debt

[Conscious trade-offs made during implementation]

### 9.2 Future Improvements

[Ideas for later iterations]

---

## 10. Glossary

| Term | Definition |
|---------|------------|
| Term 1 | Feature-specific definition |

---

*Template: feature/spec.md*  
*Last updated: [YYYY-MM-DD]*
