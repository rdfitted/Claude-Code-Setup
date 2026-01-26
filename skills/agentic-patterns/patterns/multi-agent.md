# Multi-Agent Pattern

Orchestrating multiple specialized agents to collaborate on complex tasks.

## When to Use

- Tasks requiring diverse expertise
- Separation of concerns (researcher, writer, reviewer)
- Parallel specialized processing
- Quality assurance through multiple perspectives
- Complex workflows with handoffs

## Pattern Variants

### 1. Sequential Multi-Agent (Pipeline)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

interface AgentConfig {
  name: string;
  model: any;
  system: string;
}

const agents: AgentConfig[] = [
  {
    name: 'Researcher',
    model: openai('gpt-4o'),
    system: 'You are a research specialist. Gather and organize information thoroughly.'
  },
  {
    name: 'Writer',
    model: anthropic('claude-sonnet-4-20250514'),
    system: 'You are a professional writer. Transform research into clear, engaging content.'
  },
  {
    name: 'Editor',
    model: openai('gpt-4o'),
    system: 'You are a meticulous editor. Improve clarity, fix errors, enhance quality.'
  }
];

async function sequentialPipeline(task: string): Promise<string> {
  let currentOutput = task;

  for (const agent of agents) {
    console.log(`\n--- ${agent.name} ---`);

    const { text } = await generateText({
      model: agent.model,
      system: agent.system,
      prompt: `Previous output:\n${currentOutput}\n\nYour task: Process and improve this.`
    });

    currentOutput = text;
    console.log(`${agent.name} completed`);
  }

  return currentOutput;
}
```

### 2. Orchestrator-Worker Pattern

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const TaskAssignmentSchema = z.object({
  tasks: z.array(z.object({
    taskId: z.string(),
    worker: z.enum(['coder', 'analyst', 'writer', 'reviewer']),
    description: z.string(),
    dependencies: z.array(z.string())
  }))
});

const workers = {
  coder: {
    model: openai('gpt-4o'),
    system: 'You are an expert programmer. Write clean, efficient code.'
  },
  analyst: {
    model: openai('gpt-4o'),
    system: 'You are a data analyst. Analyze data and provide insights.'
  },
  writer: {
    model: openai('gpt-4o'),
    system: 'You are a technical writer. Create clear documentation.'
  },
  reviewer: {
    model: openai('gpt-4o'),
    system: 'You are a code reviewer. Find issues and suggest improvements.'
  }
};

async function orchestratorWorker(project: string): Promise<Record<string, string>> {
  const orchestrator = openai('gpt-4o');
  const results: Record<string, string> = {};

  // Step 1: Orchestrator breaks down project
  const { object: plan } = await generateObject({
    model: orchestrator,
    schema: TaskAssignmentSchema,
    prompt: `Break down this project into tasks and assign to workers:

Project: ${project}

Available workers: coder, analyst, writer, reviewer
Assign based on expertise. Define dependencies.`
  });

  console.log(`Orchestrator created ${plan.tasks.length} tasks`);

  // Step 2: Execute tasks respecting dependencies
  const completed = new Set<string>();

  while (completed.size < plan.tasks.length) {
    // Find tasks with satisfied dependencies
    const ready = plan.tasks.filter(
      task => !completed.has(task.taskId) &&
        task.dependencies.every(dep => completed.has(dep))
    );

    // Execute ready tasks in parallel
    await Promise.all(
      ready.map(async (task) => {
        const worker = workers[task.worker];
        const depContext = task.dependencies
          .map(dep => `${dep}:\n${results[dep]}`)
          .join('\n\n');

        const { text } = await generateText({
          model: worker.model,
          system: worker.system,
          prompt: `Task: ${task.description}
${depContext ? `\nContext from dependencies:\n${depContext}` : ''}`
        });

        results[task.taskId] = text;
        completed.add(task.taskId);
        console.log(`Completed: ${task.taskId} (${task.worker})`);
      })
    );
  }

  return results;
}
```

### 3. Debate/Adversarial Pattern

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const JudgmentSchema = z.object({
  winner: z.enum(['agent1', 'agent2', 'tie']),
  reasoning: z.string(),
  synthesizedAnswer: z.string()
});

async function debatePattern(question: string, rounds: number = 3): Promise<string> {
  const agent1 = { model: openai('gpt-4o'), name: 'Agent 1' };
  const agent2 = { model: anthropic('claude-sonnet-4-20250514'), name: 'Agent 2' };
  const judge = openai('gpt-4o');

  let history: string[] = [];

  // Initial positions
  const { text: position1 } = await generateText({
    model: agent1.model,
    prompt: `Question: ${question}\n\nProvide your answer with reasoning.`
  });
  history.push(`${agent1.name}: ${position1}`);

  const { text: position2 } = await generateText({
    model: agent2.model,
    prompt: `Question: ${question}\n\nProvide your answer with reasoning.`
  });
  history.push(`${agent2.name}: ${position2}`);

  // Debate rounds
  for (let round = 0; round < rounds; round++) {
    console.log(`\n--- Round ${round + 1} ---`);

    // Agent 1 responds to Agent 2
    const { text: response1 } = await generateText({
      model: agent1.model,
      prompt: `Question: ${question}

Debate history:
${history.join('\n\n')}

Respond to ${agent2.name}'s arguments. Defend or refine your position.`
    });
    history.push(`${agent1.name}: ${response1}`);

    // Agent 2 responds to Agent 1
    const { text: response2 } = await generateText({
      model: agent2.model,
      prompt: `Question: ${question}

Debate history:
${history.join('\n\n')}

Respond to ${agent1.name}'s arguments. Defend or refine your position.`
    });
    history.push(`${agent2.name}: ${response2}`);
  }

  // Judge determines winner and synthesizes
  const { object: judgment } = await generateObject({
    model: judge,
    schema: JudgmentSchema,
    prompt: `You are an impartial judge. Evaluate this debate:

Question: ${question}

Debate:
${history.join('\n\n')}

Determine winner and synthesize the best answer.`
  });

  console.log(`\nWinner: ${judgment.winner}`);
  console.log(`Reasoning: ${judgment.reasoning}`);

  return judgment.synthesizedAnswer;
}
```

### 4. Supervisor Pattern (Quality Control)

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const QualityCheckSchema = z.object({
  approved: z.boolean(),
  score: z.number().min(1).max(10),
  issues: z.array(z.string()),
  suggestions: z.array(z.string())
});

async function supervisedAgent(
  task: string,
  maxAttempts: number = 3
): Promise<string> {
  const worker = openai('gpt-4o-mini'); // Cheaper worker
  const supervisor = openai('gpt-4o'); // Smarter supervisor

  let currentOutput = '';
  let feedback = '';

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    console.log(`\n--- Attempt ${attempt} ---`);

    // Worker produces output
    const { text: workerOutput } = await generateText({
      model: worker,
      prompt: `Task: ${task}
${feedback ? `\nPrevious feedback to address:\n${feedback}` : ''}

Produce your best work.`
    });
    currentOutput = workerOutput;

    // Supervisor reviews
    const { object: review } = await generateObject({
      model: supervisor,
      schema: QualityCheckSchema,
      prompt: `Review this work:

Task: ${task}
Output: ${workerOutput}

Score quality 1-10. Approve if score >= 8.`
    });

    console.log(`Score: ${review.score}/10`);

    if (review.approved) {
      console.log('Approved!');
      return currentOutput;
    }

    // Prepare feedback for next attempt
    feedback = `Issues:\n${review.issues.join('\n')}\n\nSuggestions:\n${review.suggestions.join('\n')}`;
    console.log(`Not approved. Issues: ${review.issues.length}`);
  }

  console.log('Max attempts reached, returning best effort');
  return currentOutput;
}
```

### 5. Specialist Routing (Dynamic Team)

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const specialists = {
  'legal-expert': {
    model: anthropic('claude-sonnet-4-20250514'),
    system: 'You are a legal expert. Provide accurate legal analysis and advice.',
    domains: ['contracts', 'compliance', 'regulations', 'legal']
  },
  'finance-expert': {
    model: openai('gpt-4o'),
    system: 'You are a financial analyst. Provide detailed financial analysis.',
    domains: ['budgets', 'investments', 'accounting', 'financial']
  },
  'tech-expert': {
    model: openai('gpt-4o'),
    system: 'You are a technology expert. Provide technical guidance and solutions.',
    domains: ['software', 'architecture', 'security', 'technical']
  },
  'general': {
    model: openai('gpt-4o-mini'),
    system: 'You are a helpful assistant.',
    domains: ['general']
  }
};

const RoutingSchema = z.object({
  primarySpecialist: z.enum(['legal-expert', 'finance-expert', 'tech-expert', 'general']),
  secondarySpecialists: z.array(z.enum(['legal-expert', 'finance-expert', 'tech-expert', 'general'])),
  reasoning: z.string()
});

async function dynamicTeam(query: string): Promise<string> {
  const router = openai('gpt-4o-mini');

  // Determine which specialists are needed
  const { object: routing } = await generateObject({
    model: router,
    schema: RoutingSchema,
    prompt: `Determine which specialists should handle this query:

"${query}"

Specialists available:
- legal-expert: Legal matters, contracts, compliance
- finance-expert: Financial analysis, budgets, investments
- tech-expert: Technology, software, architecture
- general: General questions

Choose primary and any secondary specialists needed.`
  });

  console.log(`Primary: ${routing.primarySpecialist}`);
  console.log(`Secondary: ${routing.secondarySpecialists.join(', ')}`);

  // Get primary response
  const primary = specialists[routing.primarySpecialist];
  const { text: primaryResponse } = await generateText({
    model: primary.model,
    system: primary.system,
    prompt: query
  });

  // Get secondary perspectives if needed
  if (routing.secondarySpecialists.length === 0) {
    return primaryResponse;
  }

  const secondaryResponses = await Promise.all(
    routing.secondarySpecialists.map(async (specialistKey) => {
      const specialist = specialists[specialistKey];
      const { text } = await generateText({
        model: specialist.model,
        system: specialist.system,
        prompt: `Add your perspective to this query:

Query: ${query}

Primary response (from ${routing.primarySpecialist}):
${primaryResponse}

Add any insights from your domain of expertise.`
      });
      return { specialist: specialistKey, response: text };
    })
  );

  // Synthesize all responses
  const { text: synthesis } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Synthesize these expert responses:

Query: ${query}

Primary (${routing.primarySpecialist}):
${primaryResponse}

Secondary perspectives:
${secondaryResponses.map(r => `${r.specialist}: ${r.response}`).join('\n\n')}

Create a comprehensive, unified response.`
  });

  return synthesis;
}
```

## Best Practices

1. **Define clear roles** - Each agent should have a specific purpose
2. **Manage context passing** - Be explicit about what each agent receives
3. **Handle failures** - One agent failing shouldn't crash the system
4. **Monitor coordination** - Log handoffs and agent outputs
5. **Optimize for cost** - Use cheaper models for simpler agents
6. **Set timeouts** - Prevent hanging multi-agent workflows

## Anti-Patterns to Avoid

- **Too many agents**: 3-5 agents is usually sufficient
- **Unclear handoffs**: Ambiguous boundaries cause confusion
- **No error handling**: Agent failures cascade
- **Redundant agents**: Agents doing the same thing
- **Missing synthesis**: Multiple outputs need combination

## Communication Patterns

| Pattern | Communication | Use Case |
|---------|--------------|----------|
| Sequential | A → B → C | Pipelines, refinement |
| Parallel | A, B, C (independent) | Speed, multiple perspectives |
| Hub-Spoke | Orchestrator ↔ Workers | Task distribution |
| Mesh | All ↔ All | Complex collaboration |
