# Planning Pattern

Task decomposition and sequencing where an agent breaks complex goals into manageable steps before execution.

## When to Use

- Complex multi-step tasks
- Tasks requiring dependencies between steps
- Resource allocation decisions
- Project/workflow automation
- When execution order matters

## Pattern Variants

### 1. Simple Plan-Then-Execute

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const PlanSchema = z.object({
  goal: z.string(),
  steps: z.array(z.object({
    id: z.number(),
    description: z.string(),
    dependencies: z.array(z.number()).describe('IDs of steps this depends on'),
    estimatedComplexity: z.enum(['low', 'medium', 'high'])
  })),
  totalSteps: z.number()
});

async function planAndExecute(goal: string): Promise<string> {
  const model = openai('gpt-4o');

  // Step 1: Generate plan
  const { object: plan } = await generateObject({
    model,
    schema: PlanSchema,
    prompt: `Create a detailed execution plan for this goal:

Goal: ${goal}

Break it into clear, actionable steps with dependencies.
Each step should be independently executable.`
  });

  console.log(`Plan created: ${plan.totalSteps} steps`);

  // Step 2: Execute steps in dependency order
  const results: Record<number, string> = {};

  // Simple topological execution (assumes valid DAG)
  const executed = new Set<number>();

  while (executed.size < plan.steps.length) {
    for (const step of plan.steps) {
      // Skip if already executed
      if (executed.has(step.id)) continue;

      // Check if dependencies are met
      const depsReady = step.dependencies.every(dep => executed.has(dep));
      if (!depsReady) continue;

      // Execute step
      const context = step.dependencies
        .map(dep => `Step ${dep} result: ${results[dep]}`)
        .join('\n');

      const { text } = await generateText({
        model,
        prompt: `Execute this step:

Overall goal: ${goal}
Current step: ${step.description}
${context ? `\nPrevious results:\n${context}` : ''}

Provide the output for this step.`
      });

      results[step.id] = text;
      executed.add(step.id);
      console.log(`Completed step ${step.id}: ${step.description}`);
    }
  }

  // Step 3: Synthesize final result
  const { text: finalResult } = await generateText({
    model,
    prompt: `Synthesize the final result from these completed steps:

Goal: ${goal}

Step results:
${Object.entries(results).map(([id, result]) => `Step ${id}: ${result}`).join('\n\n')}

Provide the complete final output.`
  });

  return finalResult;
}
```

### 2. Dynamic Re-Planning

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const StepResultSchema = z.object({
  success: z.boolean(),
  output: z.string(),
  needsReplan: z.boolean(),
  replanReason: z.string().optional()
});

const PlanSchema = z.object({
  steps: z.array(z.object({
    id: z.number(),
    action: z.string(),
    expectedOutcome: z.string()
  }))
});

async function dynamicPlanExecution(goal: string): Promise<string> {
  const model = openai('gpt-4o');
  let currentPlan: z.infer<typeof PlanSchema>;
  let stepIndex = 0;
  const history: string[] = [];

  // Initial planning
  const { object: initialPlan } = await generateObject({
    model,
    schema: PlanSchema,
    prompt: `Create an execution plan for: ${goal}`
  });
  currentPlan = initialPlan;

  while (stepIndex < currentPlan.steps.length) {
    const step = currentPlan.steps[stepIndex];

    // Execute step
    const { text: stepOutput } = await generateText({
      model,
      prompt: `Execute: ${step.action}
Expected: ${step.expectedOutcome}
History: ${history.join('\n')}`
    });

    // Evaluate result
    const { object: evaluation } = await generateObject({
      model,
      schema: StepResultSchema,
      prompt: `Evaluate this step execution:

Action: ${step.action}
Expected: ${step.expectedOutcome}
Actual output: ${stepOutput}

Did it succeed? Does the plan need adjustment?`
    });

    history.push(`Step ${step.id}: ${stepOutput}`);

    if (evaluation.needsReplan) {
      console.log(`Re-planning: ${evaluation.replanReason}`);

      // Generate new plan from current point
      const { object: newPlan } = await generateObject({
        model,
        schema: PlanSchema,
        prompt: `The plan needs adjustment.

Original goal: ${goal}
Completed so far: ${history.join('\n')}
Issue: ${evaluation.replanReason}

Create updated remaining steps.`
      });

      currentPlan = newPlan;
      stepIndex = 0; // Reset to start of new plan
    } else {
      stepIndex++;
    }
  }

  return history.join('\n\n');
}
```

### 3. Hierarchical Planning (Plan of Plans)

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const SubPlanSchema = z.object({
  phase: z.string(),
  objective: z.string(),
  tasks: z.array(z.string())
});

const MasterPlanSchema = z.object({
  projectName: z.string(),
  phases: z.array(SubPlanSchema),
  criticalPath: z.array(z.string())
});

async function hierarchicalPlanning(project: string): Promise<{
  masterPlan: z.infer<typeof MasterPlanSchema>;
  detailedPlans: Record<string, z.infer<typeof SubPlanSchema>>;
}> {
  const model = openai('gpt-4o');

  // Level 1: High-level master plan
  const { object: masterPlan } = await generateObject({
    model,
    schema: MasterPlanSchema,
    prompt: `Create a high-level project plan:

Project: ${project}

Define major phases, objectives, and critical path.
Keep phases at strategic level (3-5 phases).`
  });

  // Level 2: Detailed plans for each phase (in parallel)
  const detailedPlans: Record<string, z.infer<typeof SubPlanSchema>> = {};

  await Promise.all(
    masterPlan.phases.map(async (phase) => {
      const { object: detailed } = await generateObject({
        model,
        schema: SubPlanSchema,
        prompt: `Create detailed plan for this phase:

Phase: ${phase.phase}
Objective: ${phase.objective}
High-level tasks: ${phase.tasks.join(', ')}

Break down into specific actionable tasks.`
      });
      detailedPlans[phase.phase] = detailed;
    })
  );

  return { masterPlan, detailedPlans };
}
```

### 4. Planning with Tool Discovery

```typescript
import { generateObject, generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// Available tools
const availableTools = {
  searchWeb: tool({
    description: 'Search the web for information',
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => ({ results: [`Result for: ${query}`] })
  }),
  readFile: tool({
    description: 'Read contents of a file',
    parameters: z.object({ path: z.string() }),
    execute: async ({ path }) => ({ content: `Contents of ${path}` })
  }),
  writeFile: tool({
    description: 'Write content to a file',
    parameters: z.object({ path: z.string(), content: z.string() }),
    execute: async ({ path, content }) => ({ success: true })
  }),
  runCode: tool({
    description: 'Execute code and return output',
    parameters: z.object({ code: z.string(), language: z.string() }),
    execute: async ({ code, language }) => ({ output: 'Execution result' })
  })
};

const ToolPlanSchema = z.object({
  steps: z.array(z.object({
    description: z.string(),
    toolToUse: z.enum(['searchWeb', 'readFile', 'writeFile', 'runCode', 'none']),
    toolParams: z.record(z.string()).optional(),
    reasoning: z.string()
  }))
});

async function toolAwarePlanning(task: string): Promise<void> {
  const model = openai('gpt-4o');

  // Describe available tools
  const toolDescriptions = Object.entries(availableTools)
    .map(([name, t]) => `- ${name}: ${t.description}`)
    .join('\n');

  // Generate tool-aware plan
  const { object: plan } = await generateObject({
    model,
    schema: ToolPlanSchema,
    prompt: `Plan how to complete this task using available tools:

Task: ${task}

Available tools:
${toolDescriptions}

Create a step-by-step plan, specifying which tool to use for each step.`
  });

  // Execute plan
  for (const step of plan.steps) {
    console.log(`\nExecuting: ${step.description}`);
    console.log(`Tool: ${step.toolToUse}`);
    console.log(`Reasoning: ${step.reasoning}`);

    if (step.toolToUse !== 'none') {
      const toolFn = availableTools[step.toolToUse as keyof typeof availableTools];
      // Execute tool with params
      // const result = await toolFn.execute(step.toolParams);
    }
  }
}
```

### 5. ReAct-Style Planning (Reason + Act)

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const tools = {
  think: tool({
    description: 'Think through the problem and plan next action',
    parameters: z.object({
      thought: z.string().describe('Your reasoning about what to do next')
    }),
    execute: async ({ thought }) => {
      console.log(`Thought: ${thought}`);
      return { recorded: true };
    }
  }),

  search: tool({
    description: 'Search for information',
    parameters: z.object({ query: z.string() }),
    execute: async ({ query }) => {
      return { results: [`Information about ${query}`] };
    }
  }),

  calculate: tool({
    description: 'Perform calculations',
    parameters: z.object({ expression: z.string() }),
    execute: async ({ expression }) => {
      try {
        return { result: eval(expression) };
      } catch {
        return { error: 'Invalid expression' };
      }
    }
  }),

  finish: tool({
    description: 'Complete the task with final answer',
    parameters: z.object({ answer: z.string() }),
    execute: async ({ answer }) => {
      return { finalAnswer: answer };
    }
  })
};

async function reactPlanning(question: string): Promise<string> {
  const { text, steps } = await generateText({
    model: openai('gpt-4o'),
    tools,
    maxSteps: 10,
    system: `You are a reasoning agent. For each step:
1. Use 'think' to reason about what you need to do
2. Use appropriate tools to gather information or calculate
3. Use 'finish' when you have the final answer

Always think before acting.`,
    prompt: question
  });

  return text;
}
```

## Best Practices

1. **Validate plan structure** - Use Zod schemas to ensure well-formed plans
2. **Handle dependencies** - Topological sort for correct execution order
3. **Build in checkpoints** - Allow for re-planning when things go wrong
4. **Keep steps atomic** - Each step should be independently verifiable
5. **Track state** - Maintain history for context in later steps
6. **Set iteration limits** - Prevent infinite planning loops

## Anti-Patterns to Avoid

- **Over-planning**: Don't plan 50 steps for a 3-step task
- **Rigid plans**: No ability to adapt when steps fail
- **Circular dependencies**: Will cause infinite loops
- **Missing validation**: Assuming LLM plans are always valid
- **No progress tracking**: Losing track of what's been done

## Plan Validation Helper

```typescript
function validatePlan(plan: { steps: { id: number; dependencies: number[] }[] }): boolean {
  const ids = new Set(plan.steps.map(s => s.id));

  for (const step of plan.steps) {
    // Check for invalid dependencies
    for (const dep of step.dependencies) {
      if (!ids.has(dep)) {
        console.error(`Invalid dependency: Step ${step.id} depends on non-existent step ${dep}`);
        return false;
      }
      if (dep === step.id) {
        console.error(`Self-dependency: Step ${step.id} depends on itself`);
        return false;
      }
    }
  }

  // Check for circular dependencies (simple check)
  const visited = new Set<number>();
  const inStack = new Set<number>();

  function hasCycle(stepId: number): boolean {
    if (inStack.has(stepId)) return true;
    if (visited.has(stepId)) return false;

    visited.add(stepId);
    inStack.add(stepId);

    const step = plan.steps.find(s => s.id === stepId);
    for (const dep of step?.dependencies || []) {
      if (hasCycle(dep)) return true;
    }

    inStack.delete(stepId);
    return false;
  }

  for (const step of plan.steps) {
    if (hasCycle(step.id)) {
      console.error('Circular dependency detected');
      return false;
    }
  }

  return true;
}
```
