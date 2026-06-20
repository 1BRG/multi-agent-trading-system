# AI Tools Usage Report

The project was developed with AI assistance across planning, implementation, validation and documentation. Three development assistants were used during this process: Claude, Codex and GitHub Copilot. They were evaluated through normal development work rather than through an isolated benchmark. In several cases, the same feature or component was approached with more than one assistant, after which the version that best matched the architecture and coding conventions of the project was retained. These development tools must not be confused with the Bull, Bear, Judge and Strategy LLM agents that run inside the application as product functionality.

## Development Assistants Used

- **Claude** was used mainly for exploratory work: discussing architecture, refining requirements, drafting larger implementation ideas and explaining alternative approaches. It was also used to produce initial versions of several backend and frontend solutions before they were adapted to the repository.
- **Codex** was used mainly for repository-level execution: inspecting the existing codebase, making targeted changes across backend and frontend files, running checks and tests, and updating technical documentation. It was particularly useful when a task affected multiple files and had to be completed without breaking existing behavior.
- **GitHub Copilot** was used inside the editor for short, local suggestions such as completing functions, generating repetitive model or serializer fields, proposing TypeScript types and filling in predictable test assertions.
- The tools were complementary rather than interchangeable. Claude was strongest while the solution space was still broad, Codex was strongest once a change had to be integrated and verified in the complete repository, and Copilot was fastest for small completions while the developer was already editing a known file.

### Claude vs. Codex vs. GitHub Copilot

| Criterion | Claude | Codex | GitHub Copilot |
|---|---|---|---|
| Primary role | Reasoning, design and solution exploration | End-to-end repository implementation and maintenance | In-editor code completion |
| Typical input | Requirements, architecture questions, code excerpts and feature descriptions | The working repository, a concrete task, failing checks and current project conventions | The open file, nearby code, comments and the current cursor position |
| Typical output | Explanations, design alternatives, draft implementations and refactoring suggestions | Coordinated file edits, tests, fixes, refactors and documentation updates | Short functions, repeated declarations, conditions and individual test cases |
| Context handling | Very good at following a long written discussion, but code excerpts can omit important repository details | Best when the answer depends on relationships between several existing files | Strongest in the immediate file, weaker when behavior depends on distant modules |
| Strongest contribution | Clarifying trade-offs and producing a coherent first design | Completing a change through inspection, implementation and validation | Reducing the time spent typing predictable code |
| Backend use | Discussing Django/DRF architecture and suggesting service or serializer structures | Updating models, serializers, views, services, validation and backend tests together | Completing fields, imports, query expressions and common test setup |
| Frontend use | Suggesting component structure, UX flows and state-management approaches | Editing Next.js components, API clients, types, styles and validation flows consistently | Completing JSX, TypeScript interfaces and repetitive rendering branches |
| Testing use | Proposing edge cases and explaining the expected behavior | Finding existing test patterns, adding deterministic tests and executing the validation loop | Generating individual assertions from nearby tests |
| Documentation use | Producing readable first drafts and conceptual explanations | Checking descriptions against real files, routes and implemented behavior | Helpful only for small comments or docstrings |
| Speed profile | Fast for obtaining a complete proposal from a broad prompt | Fastest for finishing a repository-level task with verification included | Almost immediate for short local completions |
| Main limitation | A polished answer can still rely on assumptions that do not hold in the full repository | Requires a reasonably concrete objective for the most efficient result | Suggestions can be locally plausible but architecturally incomplete |
| Best use in this project | Architecture, requirements and alternative solutions | Multi-file implementation, debugging, tests and final integration | Boilerplate and low-risk local edits |

The comparison is qualitative because the project did not maintain a strict per-prompt, per-line or time-tracking attribution log. Therefore, no source file is claimed to have been produced exclusively by one model. The comparison reflects how useful each assistant was during iterative implementation, not a controlled scientific benchmark. All generated suggestions were treated as drafts and reviewed in the context of the complete application.

### Overall Assessment

For this project, **Codex was the most effective tool overall for implementation**. Its main advantage was not necessarily generating a better isolated function on the first attempt, but understanding how a requested change interacted with models, serializers, API routes, frontend types, components and tests. It was the most useful assistant for taking a task from request to a repository state that could be checked.

**Claude was better for early-stage reasoning and explanation.** When the requirement was incomplete or several architectural approaches were possible, its responses were often more useful for comparing options and identifying trade-offs. However, an implementation proposed from selected code excerpts sometimes needed additional adaptation after being placed in the real project.

**GitHub Copilot was the best tool for completion speed inside a single file.** It removed repetitive typing and often predicted the next few lines correctly. It was less suitable for deciding how an entire feature should be designed or for confirming that a multi-file change was complete.

Consequently, there was no single winner for every category. Codex was considered the best overall implementation assistant, Claude the best discussion and architecture assistant, and Copilot the best local autocomplete assistant.

## Comparative Implementation Experience

Several project areas were approached iteratively with more than one assistant. This made it possible to compare not only the appearance of generated code, but also how much manual correction was required before the feature matched the existing application.

### Debate History and Agent Message UI

For the debate interface, Claude was used to explore how Bull, Bear and Judge messages could be represented as separate visual roles and how the verdict should be presented after the discussion. Its proposal was useful for the component hierarchy and user experience, but the first approach was relatively generic and assumed that all data could be managed directly by the page component.

Codex produced a version that aligned more closely with the existing `frontend/types/debate.ts`, API utilities and reusable debate components. It also handled repository-specific details such as the existing role names, loading behavior and the separation between message rendering and data retrieval. In this case, **Codex produced the stronger implementation**, because less integration work was needed and the result reused the project's existing types and structure.

Copilot was still useful during the implementation for completing JSX branches, role-based labels and repeated TypeScript properties. Its suggestions accelerated the final editing stage, although they did not define the overall component architecture.

### Strategy Agent Workflow

The natural-language strategy workflow required both a clear user interaction and strict backend validation. Claude helped reason about the conversation flow and suggested how a free-form prompt could be transformed into a structured strategy. Its explanations were particularly useful for separating conversational input from deterministic rules used by the backtesting engine.

When the workflow was implemented across the backend service, serializer validation, frontend API layer and `StrategyManager` component, Codex was more effective. It could inspect the accepted schema and adjust the connected files consistently. The implementation generated with repository context was preferable to a standalone component draft because it respected the actual API response and error structure. **Claude was better at explaining the concept; Codex was better at finishing the integrated feature.**

Copilot contributed smaller completions such as form state declarations, TypeScript mappings and repeated rendering code. These suggestions were useful after the main data flow had already been decided.

### Portfolio Validation and Error Handling

Portfolio validation was another area where multiple approaches were considered. Claude suggested user-friendly validation rules and described where checks could be placed. One initial direction relied too heavily on frontend validation, which would not have been sufficient because API clients could bypass the user interface.

Codex traced the workflow through the serializer, view and frontend request handling and favored backend enforcement accompanied by clear frontend feedback. This was the better solution because it preserved the API as the authoritative validation boundary. The final approach included domain checks such as supported currencies and clearer error propagation. In this comparison, **Codex performed better because it considered the complete request path rather than only the visible form**.

Copilot was useful for completing validation branches and error-message rendering, but its local suggestions required review to prevent the same rule from being inconsistently duplicated in several places.

### Automated Tests and Agent Evaluations

Claude generated a useful list of possible edge cases for the debate flow, including malformed Judge output, missing fields and unexpected model responses. This produced good test ideas but did not automatically guarantee that the tests matched the existing Django models and mocking style.

Codex inspected `backend/conversations/tests.py`, the debate service and related models before adding or refining tests. It was better at producing tests that matched the repository and at following failures through to their cause. For deterministic agent evaluations, **Codex was again more effective at implementation**, while Claude contributed broader test scenarios.

Copilot helped complete repeated test fixtures and assertions. It was productive when a neighboring test already demonstrated the expected pattern, but weaker when a new mocking strategy had to be designed.

### Documentation and Grading Evidence

Claude was useful for producing readable initial descriptions of the architecture and the role of the agents. Its prose was generally coherent and suitable for turning technical work into an evaluator-friendly explanation.

Codex was more reliable for the final documentation pass because it could compare statements with repository paths, implemented routes and test files. This reduced the risk of documenting a proposed feature as if it were already complete. The best result came from combining Claude's explanatory style with Codex's repository-level verification.

## Why the Results Differed

The differences observed between the assistants were mainly caused by the type and amount of context available to them:

- Claude performed best when given a complete written problem and asked to reason about alternatives.
- Codex performed best when the answer depended on discovering how the current repository was organized.
- Copilot performed best when the desired pattern was already visible near the cursor.
- Tasks spanning backend, frontend and tests rewarded repository navigation more than isolated code generation.
- Tasks involving product decisions or ambiguous requirements rewarded explanation and trade-off analysis more than immediate editing.
- Repetitive, low-risk code rewarded prediction speed and required less global reasoning.

This also explains why two assistants could generate solutions that looked equally valid in isolation while one integrated much better. Code quality was evaluated by compatibility with the existing project, clarity, testability and the amount of manual correction required—not only by how complete the first generated answer appeared.

## Planning

- AI was used to break the trading system into backend, frontend, agent, strategy and backtesting responsibilities.
- AI helped define API contracts for strategy generation, debate outputs, portfolio holdings and backtest results.
- Product backlog and user stories are tracked in Linear and should be linked from `docs/grading_evidence.md`.
- Claude was especially helpful during divergent planning, where several possible designs or user flows had to be compared.
- Codex was used to connect plans to the current repository structure and identify the exact modules affected by a proposed change.
- Copilot was used after the plan was established, especially where the implementation followed repetitive patterns already present in the codebase.

## Implementation

- AI-assisted coding was used for Django models, serializers, viewsets, frontend dashboard pages and validation flows.
- A common workflow was to use Claude to refine the intended behavior and possible implementation, then use Codex to inspect dependencies, apply the selected approach and resolve integration issues.
- GitHub Copilot supported both stages from inside the editor by completing small sections of code, but its output was reviewed with the same care as suggestions from the conversational assistants.
- None of the assistants replaced developer decisions. Generated code was adapted to the project's Django, DRF, Next.js and TypeScript conventions before being retained.
- The product itself includes AI agents:
  - Bull analyst, Bear analyst and Judge agents for stock debates.
  - Strategy agent for turning natural language strategy ideas into deterministic JSON rules.

### Examples of AI-Assisted Implementation Areas

- **Multi-agent debate:** prompt-role separation, debate orchestration, persistence of agent messages and structured Judge output.
- **Strategy generation:** conversion of natural-language requests into validated JSON rules accepted by the backend.
- **Portfolio workflow:** API validation, supported-currency checks, holding valuation behavior and clearer frontend error messages.
- **Frontend integration:** typed API clients, dashboard components, debate-history presentation and loading/error states.
- **Engineering support:** CI checks, deterministic LLM mocks, repository documentation and links between grading criteria and implementation evidence.

## Validation

- AI was used to identify missing validation paths and add automated backend tests.
- Agent eval coverage is implemented in `backend/conversations/tests.py`, using deterministic LLM mocks to verify debate orchestration and Judge JSON parsing.
- CI runs backend tests, Django checks, TypeScript and ESLint.
- Codex was particularly useful for executing the validation loop after edits and tracing failures back to the affected files.
- Claude's proposed edge cases were still verified against the real serializers, views and domain constraints before tests were added.

## Human Oversight and Limitations

- AI output was never considered correct solely because it was syntactically plausible; behavior had to match the API contract and existing data model.
- Model suggestions could omit project-specific constraints, reference outdated library patterns or introduce unnecessary complexity.
- Financial analysis generated by the application's agents is informational and is not treated as guaranteed investment advice.
- Deterministic mocks are used in automated agent evaluations so CI does not depend on model availability or variable model responses.
- Final responsibility for architecture choices, accepted code, security-sensitive configuration and financial-domain assumptions remained with the developers.
- When two tools proposed different solutions, the decision was based on compatibility with the current architecture, simplicity, validation behavior and test results rather than the perceived authority of the model.
- No model was allowed to introduce secrets, production credentials or unreviewed financial assumptions into the repository.

## Effective Combined Workflow

The most productive workflow that emerged during development was:

1. Use Claude to clarify an ambiguous requirement, identify risks and compare possible designs.
2. Select the simplest approach that satisfied the product and grading requirements.
3. Use Codex to inspect the repository, identify all affected files and implement the change consistently.
4. Use GitHub Copilot for short completions and repetitive code while manually editing individual files.
5. Run backend tests, Django checks, TypeScript and ESLint validation.
6. Return to Codex for repository-wide debugging if a check exposed an integration problem.
7. Review the final behavior and documentation manually before accepting the result.

This sequence was not mandatory for every task. Small changes could be completed with Copilot alone, while architecture questions might require only Claude. For features crossing application layers, however, the combined workflow was more reliable than asking one model for a complete solution in a single prompt.

## Result of Using All Three Tools

Using all three assistants reduced the time needed to move from an initial feature idea to a verified repository change. Claude contributed most during open-ended reasoning and communication of alternatives; Codex contributed most during codebase navigation, implementation and validation; GitHub Copilot contributed most by accelerating routine edits. The practical benefit came from combining these strengths with human review, automated tests and source-control history rather than relying on a single model response.

The final ranking for this project was:

1. **Codex — best overall for implementation**, because it handled repository context, multi-file changes and validation most effectively.
2. **Claude — best for architecture and explanations**, especially before the exact implementation path was known.
3. **GitHub Copilot — best for local coding speed**, but not sufficient by itself for complex, cross-layer features.

This ranking is project-specific. A different project or workflow could favor another tool, and model capabilities evolve over time. The conclusion represents the practical experience of building this Django and Next.js application rather than a universal claim about model quality.

## Documentation

- AI was used to draft architecture notes, API route documentation, grading evidence and Mermaid diagrams.
- The documentation is intentionally linked from the README so the evaluator can map each grading requirement to a repository artifact.
- AI-generated documentation was checked against actual paths and behavior in the repository to avoid describing features that were only proposed but not implemented.
