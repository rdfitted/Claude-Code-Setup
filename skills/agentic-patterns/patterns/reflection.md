# Reflection Pattern

Self-critique and iterative improvement loop where an agent evaluates its own output and refines it.

## When to Use

- Code generation requiring quality assurance
- Content that needs factual accuracy
- Complex reasoning tasks
- Any output where "good enough" isn't acceptable

## Pattern Variants

### 1. Simple Reflection (Generate → Critique → Refine)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

async function reflectiveGeneration(task: string): Promise<string> {
  const model = openai('gpt-4o');

  // Step 1: Initial generation
  const { text: draft } = await generateText({
    model,
    prompt: task
  });

  // Step 2: Self-critique
  const { text: critique } = await generateText({
    model,
    prompt: `Critically evaluate this response. List specific issues:

Task: ${task}
Response: ${draft}

Identify:
1. Factual errors
2. Missing information
3. Unclear explanations
4. Potential improvements`
  });

  // Step 3: Refinement
  const { text: refined } = await generateText({
    model,
    prompt: `Improve this response based on the critique:

Original: ${draft}
Critique: ${critique}

Provide an improved version addressing all issues.`
  });

  return refined;
}
```

### 2. Multi-Model Reflection (Different Critic)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

async function crossModelReflection(task: string): Promise<string> {
  // Generate with one model
  const { text: draft } = await generateText({
    model: openai('gpt-4o'),
    prompt: task
  });

  // Critique with different model (different perspective)
  const { text: critique } = await generateText({
    model: anthropic('claude-sonnet-4-20250514'),
    prompt: `As a critical reviewer, evaluate this response:

Task: ${task}
Response: ${draft}

Be thorough and specific in your critique.`
  });

  // Refine with original model
  const { text: refined } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Address this critique and improve your response:

Original: ${draft}
Critique: ${critique}`
  });

  return refined;
}
```

### 3. Iterative Reflection Loop

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const QualitySchema = z.object({
  score: z.number().min(1).max(10),
  issues: z.array(z.string()),
  passesThreshold: z.boolean()
});

async function iterativeReflection(
  task: string,
  maxIterations: number = 3,
  qualityThreshold: number = 8
): Promise<string> {
  const model = openai('gpt-4o');
  let current = '';

  // Initial generation
  const { text: initial } = await generateText({
    model,
    prompt: task
  });
  current = initial;

  for (let i = 0; i < maxIterations; i++) {
    // Evaluate quality with structured output
    const { object: evaluation } = await generateObject({
      model,
      schema: QualitySchema,
      prompt: `Rate this response (1-10) for the task:

Task: ${task}
Response: ${current}

Score based on: accuracy, completeness, clarity.
List specific issues if score < ${qualityThreshold}.`
    });

    // Check if quality threshold met
    if (evaluation.passesThreshold || evaluation.score >= qualityThreshold) {
      console.log(`Quality threshold met at iteration ${i + 1}`);
      break;
    }

    // Refine based on issues
    const { text: refined } = await generateText({
      model,
      prompt: `Improve this response. Current issues:
${evaluation.issues.map(issue => `- ${issue}`).join('\n')}

Current response: ${current}

Provide improved version.`
    });

    current = refined;
  }

  return current;
}
```

### 4. Reflection with Tool Use

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const reflectionTools = {
  evaluateCode: tool({
    description: 'Evaluate code for bugs, style issues, and improvements',
    parameters: z.object({
      code: z.string(),
      language: z.string()
    }),
    execute: async ({ code, language }) => {
      // Could integrate with actual linter/type checker
      return {
        syntaxValid: true,
        suggestions: ['Consider adding error handling', 'Add type annotations']
      };
    }
  }),

  checkFacts: tool({
    description: 'Verify factual claims against knowledge base',
    parameters: z.object({
      claims: z.array(z.string())
    }),
    execute: async ({ claims }) => {
      // Could integrate with fact-checking API
      return claims.map(claim => ({
        claim,
        verified: true,
        confidence: 0.9
      }));
    }
  })
};

async function toolAssistedReflection(task: string): Promise<string> {
  const model = openai('gpt-4o');

  // Generate with reflection tools available
  const { text } = await generateText({
    model,
    tools: reflectionTools,
    maxSteps: 5,
    prompt: `Complete this task, then use available tools to verify your work:

Task: ${task}

After generating your response:
1. Use evaluateCode if you wrote code
2. Use checkFacts if you made factual claims
3. Revise based on tool feedback`
  });

  return text;
}
```

## Best Practices

1. **Separate generation and critique prompts** - Don't ask the model to self-critique in the same call
2. **Be specific in critique prompts** - Ask for specific issues, not general feedback
3. **Set iteration limits** - Prevent infinite loops with maxIterations
4. **Use structured evaluation** - generateObject for consistent quality scoring
5. **Consider model diversity** - Different models catch different issues
6. **Track improvements** - Log each iteration to verify actual improvement

## Anti-Patterns to Avoid

- **Single-prompt reflection**: "Generate X and check if it's good" doesn't work
- **Vague critique requests**: "Is this good?" produces unhelpful feedback
- **Unlimited iterations**: Always set bounds
- **Ignoring diminishing returns**: More iterations != better results

## When NOT to Use

- Simple, deterministic tasks
- Real-time/low-latency requirements (adds 2-3x latency)
- Tasks where "approximately correct" is acceptable
- High-volume, cost-sensitive applications
