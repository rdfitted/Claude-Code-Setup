---
name: agentic-patterns
description: Agentic design patterns for building AI agents with Vercel AI SDK v5. Covers reflection, routing, parallelization, planning, tool-use, multi-agent, memory, and guardrails patterns with production-ready TypeScript implementations.
---

# Agentic Design Patterns for AI SDK v5

A comprehensive guide to building intelligent AI agents using proven agentic design patterns, implemented with Vercel AI SDK v5 best practices.

## Available Patterns

| Pattern | Description | Use When |
|---------|-------------|----------|
| [Reflection](#reflection) | Self-critique and iterative improvement | Quality-critical outputs, code generation |
| [Routing](#routing) | Dynamic agent/model selection | Multi-domain tasks, specialized handlers |
| [Parallelization](#parallelization) | Concurrent task execution | Independent subtasks, speed optimization |
| [Planning](#planning) | Task decomposition and sequencing | Complex multi-step workflows |
| [Tool Use](#tool-use) | External capability integration | API calls, database queries, actions |
| [Multi-Agent](#multi-agent) | Orchestrated agent collaboration | Complex systems, specialized roles |
| [Memory](#memory) | Context persistence and retrieval | Long conversations, knowledge bases |
| [Guardrails](#guardrails) | Safety, validation, and constraints | Production systems, user-facing apps |

## Quick Reference

### Pattern Selection Guide

```
Need self-improvement? ─────────────────────► Reflection
Need specialized handling? ─────────────────► Routing
Need speed with independent tasks? ─────────► Parallelization
Need complex task breakdown? ────────────────► Planning
Need external actions? ──────────────────────► Tool Use
Need multiple specialized agents? ───────────► Multi-Agent
Need persistent context? ────────────────────► Memory
Need safety/validation? ─────────────────────► Guardrails
```

### Pattern Combinations (Common)

| Combination | Use Case |
|-------------|----------|
| Planning + Tool Use | Task automation workflows |
| Routing + Multi-Agent | Domain-specific expert systems |
| Reflection + Guardrails | High-quality, safe outputs |
| Memory + Multi-Agent | Persistent collaborative systems |
| Parallelization + Routing | High-throughput classification |

## Pattern Details

See individual pattern files in `patterns/` directory:

- `patterns/reflection.md` - Self-critique loops
- `patterns/routing.md` - Dynamic dispatch
- `patterns/parallelization.md` - Concurrent execution
- `patterns/planning.md` - Task decomposition
- `patterns/tool-use.md` - External integrations
- `patterns/multi-agent.md` - Agent orchestration
- `patterns/memory.md` - Context management
- `patterns/guardrails.md` - Safety patterns

## AI SDK v5 Core Concepts

### Key Functions

```typescript
import { generateText, streamText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

// Single response
const { text } = await generateText({
  model: openai('gpt-4o'),
  prompt: 'Your prompt'
});

// Streaming response
const { textStream } = await streamText({
  model: anthropic('claude-sonnet-4-20250514'),
  prompt: 'Your prompt'
});

// Structured output
const { object } = await generateObject({
  model: openai('gpt-4o'),
  schema: z.object({ name: z.string() }),
  prompt: 'Your prompt'
});
```

### Agentic Loop Controls

```typescript
// Multi-step with termination control
const { text, steps } = await generateText({
  model: openai('gpt-4o'),
  tools: { /* your tools */ },
  maxSteps: 10,
  stopWhen: stepCountIs(5), // Stop after 5 steps
  onStepFinish: ({ stepType, toolCalls }) => {
    console.log('Step completed:', stepType);
  }
});
```

### Tool Definition Pattern

```typescript
import { tool } from 'ai';
import { z } from 'zod';

const myTool = tool({
  description: 'Clear description for LLM selection',
  parameters: z.object({
    param1: z.string().describe('What this parameter does'),
    param2: z.number().optional()
  }),
  execute: async ({ param1, param2 }) => {
    // Tool implementation
    return { result: 'success' };
  }
});
```

## Usage

When building an agent, invoke this skill to get pattern-specific guidance:

1. **Describe your agent's goal**
2. **Identify which patterns apply** (use selection guide above)
3. **Read relevant pattern files** for implementation details
4. **Combine patterns** as needed for complex agents

## Credits

Patterns informed by:
- [Agentic Design Patterns by Antonio Gulli](https://github.com/sarwarbeing-ai/Agentic_Design_Patterns)
- [Vercel AI SDK Documentation](https://ai-sdk.dev)
- [Anthropic Agent Patterns](https://docs.anthropic.com)

## Related Skills

- `ai-sdk-best-practices` - Production best practices for AI SDK
- `ai-sdk-planner` - Planning agent for AI SDK architectures
