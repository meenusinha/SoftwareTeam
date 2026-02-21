# Project Management

This folder contains all documentation for managing your software project.

## Folder Structure

```
project-management/
├── tasks/           # Task assignments and tracking
├── designs/         # System architecture and design documents
├── requirements/    # Feature requirements and specifications
├── quality/         # Testing plans, bug reports, QA documentation
├── operations/      # Release management, infrastructure, DevOps
└── workflow/        # Team coordination and workflow processes
```

## What Goes Where

### tasks/
- Task assignments for each agent role (developer, tester, architect, IT)
- Task templates for consistent documentation
- Completed task archives

### designs/
- System architecture diagrams
- Engineering Design Specifications (EDS)
- External Product Specifications (EPS)
- Interface definitions
- Design decisions and rationale

### requirements/
- Functional requirements (what the system should do)
- Non-functional requirements (performance, security, etc.)
- User stories and use cases

### quality/
- Test plans and strategies
- Bug reports
- Test documentation
- Quality metrics and reports

### operations/
- Release documentation
- Build configurations
- Infrastructure setup guides
- Environment documentation
- Deployment scripts

### workflow/
- Team coordination documents
- Workflow summaries
- Process automation scripts

## Using These Folders

1. **New Feature**: Start in `requirements/` → `designs/` → `tasks/`
2. **Bug Fix**: Document in `quality/bugs/` → assign in `tasks/`
3. **Release**: Prepare in `operations/releases/`
4. **Testing**: Plan in `quality/plans/` → report in `quality/reports/`

## Agent Responsibilities

| Folder | Primary Agent |
|--------|---------------|
| tasks/ | Product Owner |
| designs/ | Architect |
| requirements/ | Architect |
| quality/ | Tester |
| operations/ | IT |
| workflow/ | Product Owner |
