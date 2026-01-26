# Routing Pattern

Dynamic dispatch of tasks to specialized agents, models, or handlers based on input classification.

## When to Use

- Multi-domain applications (support, sales, technical)
- Cost optimization (cheap model for simple, expensive for complex)
- Specialized expertise requirements
- Load balancing across capabilities

## Pattern Variants

### 1. LLM-Based Router

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const RouteSchema = z.object({
  route: z.enum(['technical', 'billing', 'general', 'escalate']),
  confidence: z.number().min(0).max(1),
  reasoning: z.string()
});

type Route = z.infer<typeof RouteSchema>['route'];

// Specialized handlers
const handlers: Record<Route, (query: string) => Promise<string>> = {
  technical: async (query) => {
    const { text } = await generateText({
      model: anthropic('claude-sonnet-4-20250514'),
      system: 'You are a technical support specialist. Provide detailed technical solutions.',
      prompt: query
    });
    return text;
  },

  billing: async (query) => {
    const { text } = await generateText({
      model: openai('gpt-4o-mini'), // Cheaper for routine queries
      system: 'You are a billing specialist. Help with payment and subscription issues.',
      prompt: query
    });
    return text;
  },

  general: async (query) => {
    const { text } = await generateText({
      model: openai('gpt-4o-mini'),
      system: 'You are a helpful assistant.',
      prompt: query
    });
    return text;
  },

  escalate: async (query) => {
    return 'This query requires human assistance. Routing to support team...';
  }
};

async function routedAgent(query: string): Promise<string> {
  // Step 1: Classify the query
  const { object: classification } = await generateObject({
    model: openai('gpt-4o-mini'), // Fast, cheap classifier
    schema: RouteSchema,
    prompt: `Classify this customer query:

"${query}"

Routes:
- technical: Code, API, integration, bugs, errors
- billing: Payments, subscriptions, invoices, refunds
- general: Product info, how-to, general questions
- escalate: Complaints, legal, sensitive issues`
  });

  console.log(`Routing to: ${classification.route} (${classification.confidence})`);

  // Step 2: Route to specialized handler
  return handlers[classification.route](query);
}
```

### 2. Model Complexity Router

```typescript
import { generateObject, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const ComplexitySchema = z.object({
  complexity: z.enum(['simple', 'moderate', 'complex']),
  reasoning: z.string()
});

// Model selection based on complexity
const modelMap = {
  simple: openai('gpt-4o-mini'),      // $0.15/1M tokens
  moderate: openai('gpt-4o'),          // $2.50/1M tokens
  complex: anthropic('claude-sonnet-4-20250514') // Best reasoning
};

async function complexityRouter(task: string): Promise<string> {
  // Classify complexity (use cheap model)
  const { object } = await generateObject({
    model: openai('gpt-4o-mini'),
    schema: ComplexitySchema,
    prompt: `Rate task complexity:

"${task}"

- simple: Direct question, single fact, basic formatting
- moderate: Multi-step reasoning, some analysis required
- complex: Deep analysis, creative work, nuanced judgment`
  });

  // Route to appropriate model
  const selectedModel = modelMap[object.complexity];
  console.log(`Complexity: ${object.complexity}, using: ${selectedModel.modelId}`);

  const { text } = await generateText({
    model: selectedModel,
    prompt: task
  });

  return text;
}
```

### 3. Tool-Based Router

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const routingTools = {
  routeToCodeExpert: tool({
    description: 'Route to code expert for programming questions, debugging, code review',
    parameters: z.object({
      query: z.string(),
      language: z.string().optional()
    }),
    execute: async ({ query, language }) => {
      const { text } = await generateText({
        model: openai('gpt-4o'),
        system: `You are an expert ${language || 'software'} developer.`,
        prompt: query
      });
      return { response: text, handler: 'code-expert' };
    }
  }),

  routeToDataAnalyst: tool({
    description: 'Route to data analyst for statistics, data interpretation, charts',
    parameters: z.object({
      query: z.string(),
      dataContext: z.string().optional()
    }),
    execute: async ({ query, dataContext }) => {
      const { text } = await generateText({
        model: openai('gpt-4o'),
        system: 'You are a data analyst expert in statistics and visualization.',
        prompt: dataContext ? `Context: ${dataContext}\n\n${query}` : query
      });
      return { response: text, handler: 'data-analyst' };
    }
  }),

  routeToWriter: tool({
    description: 'Route to writer for content creation, editing, copywriting',
    parameters: z.object({
      query: z.string(),
      style: z.enum(['formal', 'casual', 'technical']).optional()
    }),
    execute: async ({ query, style }) => {
      const { text } = await generateText({
        model: openai('gpt-4o'),
        system: `You are a professional writer. Style: ${style || 'adaptive'}`,
        prompt: query
      });
      return { response: text, handler: 'writer' };
    }
  })
};

async function toolBasedRouter(query: string): Promise<string> {
  const { text, toolResults } = await generateText({
    model: openai('gpt-4o-mini'), // Cheap router
    tools: routingTools,
    toolChoice: 'required', // Must pick a route
    prompt: `Route this query to the appropriate expert:

"${query}"

Choose the most appropriate routing tool.`
  });

  // Extract result from the tool that was called
  const result = toolResults[0]?.result as { response: string; handler: string };
  console.log(`Routed to: ${result?.handler}`);

  return result?.response || text;
}
```

### 4. Semantic Router (Embeddings-Based)

```typescript
import { embed, cosineSimilarity } from 'ai';
import { openai } from '@ai-sdk/openai';

// Pre-computed route embeddings
const routes = [
  {
    name: 'technical',
    examples: [
      'How do I fix this error?',
      'The API is returning 500',
      'Code review needed'
    ],
    embedding: null as number[] | null
  },
  {
    name: 'billing',
    examples: [
      'I need a refund',
      'Update my payment method',
      'Cancel subscription'
    ],
    embedding: null as number[] | null
  },
  {
    name: 'general',
    examples: [
      'What does your product do?',
      'How do I get started?',
      'Tell me about features'
    ],
    embedding: null as number[] | null
  }
];

// Initialize route embeddings (do once at startup)
async function initializeRoutes() {
  const embeddingModel = openai.embedding('text-embedding-3-small');

  for (const route of routes) {
    const combined = route.examples.join(' ');
    const { embedding } = await embed({
      model: embeddingModel,
      value: combined
    });
    route.embedding = embedding;
  }
}

async function semanticRouter(query: string): Promise<string> {
  const embeddingModel = openai.embedding('text-embedding-3-small');

  // Embed the query
  const { embedding: queryEmbedding } = await embed({
    model: embeddingModel,
    value: query
  });

  // Find best matching route
  let bestRoute = routes[0];
  let bestScore = -1;

  for (const route of routes) {
    if (route.embedding) {
      const score = cosineSimilarity(queryEmbedding, route.embedding);
      if (score > bestScore) {
        bestScore = score;
        bestRoute = route;
      }
    }
  }

  console.log(`Semantic route: ${bestRoute.name} (score: ${bestScore.toFixed(3)})`);

  // Route to handler (implement handlers as needed)
  return `Routed to ${bestRoute.name} handler`;
}
```

## Best Practices

1. **Use cheap models for routing** - Classification is simple; save expensive models for execution
2. **Include confidence scores** - Low confidence can trigger fallback or escalation
3. **Log routing decisions** - Essential for debugging and optimization
4. **Pre-compute embeddings** - For semantic routing, embed examples at startup
5. **Define clear route boundaries** - Ambiguous categories cause misrouting
6. **Handle edge cases** - Have a fallback route for unclassifiable inputs

## Anti-Patterns to Avoid

- **Expensive routers**: Don't use GPT-4 just to classify simple queries
- **Too many routes**: 3-7 routes is optimal; more causes confusion
- **Missing fallback**: Always have a "general" or "unknown" route
- **Ignoring confidence**: Low-confidence routes should be handled specially

## Cost Optimization Example

```typescript
// Typical cost savings with routing
// Without routing: All queries → GPT-4 ($2.50/1M)
// With routing:
//   70% simple → GPT-4-mini ($0.15/1M) = $0.105
//   20% moderate → GPT-4 ($2.50/1M) = $0.50
//   10% complex → Claude ($3/1M) = $0.30
// Total: $0.905/1M tokens (64% savings)
```
