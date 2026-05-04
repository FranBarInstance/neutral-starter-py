# [NNN-System Name]

## Executive Summary

> Describe in 2-3 sentences what system or cross-cutting contract this
> specification defines.
> Example: "This specification defines the component loading and orchestration
> system, establishing the contract between the application core and modular
> extensions."

## Normative References

- `.specify/memory/constitution.md` — Immutable project principles.
- [Other relevant system specs]
- [Applicable agent skills]
- [Reference technical documentation]

---

## 1. Objectives

### 1.1 What This System Must Achieve

- Objective 1
- Objective 2
- Objective 3

### 1.2 Non-Objectives (What Is Explicitly Out of Scope)

- Out-of-scope functionality 1
- Out-of-scope functionality 2
- Unsupported edge cases

---

## 2. Technical Contracts

### 2.1 Architecture and Participating Components

```text
[Architecture diagram or textual description]
```

### 2.2 Interfaces and APIs

| Interface | Type | Contract |
|-----------|------|----------|
| [Name] | [API/Class/Event] | [Contract description] |

### 2.3 Configuration

| Key | Type | Description | Default |
|-------|------|-------------|---------|
| `config.key` | `type` | Description | Value |

### 2.4 States and Transitions

```text
[State A] --[event]--> [State B]
```

---

## 3. Behavior

### 3.1 Successful Flow (Happy Path)

1. Step 1
2. Step 2
3. Step 3 -> Expected result

### 3.2 Error Handling

| Error Condition | Expected Behavior | Code/State |
|--------------------|---------------------------|---------------|
| Error 1 | What must happen | Code |
| Error 2 | What must happen | Code |

### 3.3 Edge Cases

| Edge Case | Behavior |
|-------------|----------------|
| Case 1 | Description |
| Case 2 | Description |

---

## 4. Security

### 4.1 Mandatory Security Controls

- [ ] CSP (if JavaScript/CSS/client assets apply)
- [ ] Token validation (if forms/AJAX apply)
- [ ] Rate limiting (if state-changing behavior applies)
- [ ] Host/proxy validation
- [ ] Authentication/authorization (`routes_auth`, `routes_role`)

### 4.2 Risk Analysis

| Risk | Mitigation | Level |
|--------|------------|-------|
| Risk 1 | Mitigation | High/Medium/Low |

---

## 5. Implementation and Operations

### 5.1 Preconditions

- Requirement 1
- Requirement 2

### 5.2 Implementation Process

> Fill this section only if the spec describes new work, migrations, phased
> rollout, or a sensitive sequence.

1. Step 1
2. Step 2
3. Step 3

### 5.3 Rollback and Recovery

> Fill this section only if there are operational changes, migrations, risky
> deployments, or an explicit need for rollback.

| Scenario | Procedure |
|-------------|---------------|
| Failure 1 | Recovery steps |

---

## 6. Testing

### 6.1 Testing Strategy

| Type | Coverage | Method |
|------|-----------|--------|
| Unit | Individual components | pytest |
| Integration | Interaction between components | pytest + fixtures |
| E2E | Complete flows | Playwright/manual |
| Security | Vulnerabilities | OWASP/ad-hoc |
| Performance | Load/stress | Locust/k6 |

### 6.2 Mandatory Test Cases

- [ ] Case 1: [Description]
- [ ] Case 2: [Description]
- [ ] Case 3: [Description]

### 6.3 Execution Commands

```bash
# Activate environment
source .venv/bin/activate

# Spec-specific tests
pytest [test-targets] -v

# Integration tests
pytest [integration-targets] -v --tb=short

# Coverage
pytest [test-targets] --cov=[coverage-target] --cov-report=html
```

---

## 7. Acceptance Criteria

- [ ] Verifiable criterion 1
- [ ] Verifiable criterion 2
- [ ] Verifiable criterion 3
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No undocumented technical debt

---

## 8. Impact and Dependencies

### 8.1 Affected Components

| Component | Impact | Notes |
|------------|---------|-------|
| Component 1 | High/Medium/Low | Notes |

### 8.2 External Dependencies

| Dependency | Type | Version/Contract |
|-------------|------|------------------|
| Dep 1 | [Library/Service] | Version/SLA |

### 8.3 Data Migration

[If applicable: describe required migrations]

---

## 9. Documented Decisions and Risks

### 9.1 Architectural Decisions (ADRs)

| Decision | Context | Consequences |
|----------|----------|---------------|
| Decision 1 | Why it was taken | Trade-offs |

### 9.2 Technical Risks

| Risk | Probability | Impact | Mitigation |
|--------|--------------|---------|------------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Strategy |

### 9.3 Technical Debt

[Identify conscious trade-offs and remediation plan]

---

## 10. Glossary

| Term | Definition |
|---------|------------|
| Term 1 | Definition |

---

*Template: system/spec.md*  
*Last updated: [YYYY-MM-DD]*
