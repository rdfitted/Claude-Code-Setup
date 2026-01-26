# Tool Use Pattern

Extending agent capabilities through external tools, APIs, and functions that the LLM can invoke.

## When to Use

- Accessing external data (APIs, databases, files)
- Performing calculations
- Taking actions in the real world
- Integrating with existing systems
- Any task beyond text generation

## Pattern Variants

### 1. Basic Tool Definition

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// Define tools with clear descriptions and validated parameters
const tools = {
  getWeather: tool({
    description: 'Get current weather for a location. Use when user asks about weather.',
    parameters: z.object({
      location: z.string().describe('City name or zip code'),
      units: z.enum(['celsius', 'fahrenheit']).default('fahrenheit')
    }),
    execute: async ({ location, units }) => {
      // Real implementation would call weather API
      return {
        location,
        temperature: units === 'celsius' ? 22 : 72,
        condition: 'sunny',
        units
      };
    }
  }),

  searchDatabase: tool({
    description: 'Search internal database for records. Use for data lookups.',
    parameters: z.object({
      query: z.string().describe('Search query'),
      table: z.enum(['users', 'orders', 'products']),
      limit: z.number().default(10)
    }),
    execute: async ({ query, table, limit }) => {
      // Real implementation would query database
      return {
        results: [],
        total: 0,
        query
      };
    }
  })
};

async function toolUsingAgent(userQuery: string): Promise<string> {
  const { text, toolCalls, toolResults } = await generateText({
    model: openai('gpt-4o'),
    tools,
    prompt: userQuery
  });

  return text;
}
```

### 2. Multi-Step Tool Execution

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const researchTools = {
  webSearch: tool({
    description: 'Search the web for information',
    parameters: z.object({
      query: z.string(),
      maxResults: z.number().default(5)
    }),
    execute: async ({ query, maxResults }) => {
      return { results: [`Result for: ${query}`], count: maxResults };
    }
  }),

  readUrl: tool({
    description: 'Read and extract content from a URL',
    parameters: z.object({
      url: z.string().url()
    }),
    execute: async ({ url }) => {
      return { content: `Content from ${url}`, wordCount: 500 };
    }
  }),

  summarize: tool({
    description: 'Summarize a piece of text',
    parameters: z.object({
      text: z.string(),
      maxLength: z.number().default(100)
    }),
    execute: async ({ text, maxLength }) => {
      return { summary: text.slice(0, maxLength) + '...' };
    }
  }),

  saveNote: tool({
    description: 'Save a research note for later reference',
    parameters: z.object({
      title: z.string(),
      content: z.string(),
      tags: z.array(z.string())
    }),
    execute: async ({ title, content, tags }) => {
      return { saved: true, noteId: 'note-123' };
    }
  })
};

async function researchAgent(topic: string): Promise<string> {
  const { text, steps } = await generateText({
    model: openai('gpt-4o'),
    tools: researchTools,
    maxSteps: 10, // Allow multiple tool calls
    system: `You are a research assistant. Use tools to:
1. Search for information
2. Read relevant sources
3. Summarize findings
4. Save important notes

Be thorough but efficient.`,
    prompt: `Research this topic: ${topic}`,
    onStepFinish: ({ stepType, toolCalls, toolResults }) => {
      if (stepType === 'tool-result') {
        console.log('Tools called:', toolCalls?.map(t => t.toolName));
      }
    }
  });

  console.log(`Completed in ${steps.length} steps`);
  return text;
}
```

### 3. Tool Choice Control

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const tools = {
  calculator: tool({
    description: 'Perform mathematical calculations',
    parameters: z.object({ expression: z.string() }),
    execute: async ({ expression }) => ({ result: eval(expression) })
  }),
  translator: tool({
    description: 'Translate text between languages',
    parameters: z.object({
      text: z.string(),
      from: z.string(),
      to: z.string()
    }),
    execute: async ({ text, from, to }) => ({ translated: text })
  })
};

// Force tool use
async function forcedToolUse(query: string) {
  return generateText({
    model: openai('gpt-4o'),
    tools,
    toolChoice: 'required', // Must use a tool
    prompt: query
  });
}

// Force specific tool
async function forceSpecificTool(expression: string) {
  return generateText({
    model: openai('gpt-4o'),
    tools,
    toolChoice: { type: 'tool', toolName: 'calculator' }, // Must use calculator
    prompt: `Calculate: ${expression}`
  });
}

// Let model decide
async function autoToolChoice(query: string) {
  return generateText({
    model: openai('gpt-4o'),
    tools,
    toolChoice: 'auto', // Model decides (default)
    prompt: query
  });
}

// Disable tools
async function noTools(query: string) {
  return generateText({
    model: openai('gpt-4o'),
    tools,
    toolChoice: 'none', // Tools available but won't be used
    prompt: query
  });
}
```

### 4. Tools with Side Effects (Actions)

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// Action tools that modify state
const actionTools = {
  sendEmail: tool({
    description: 'Send an email to a recipient',
    parameters: z.object({
      to: z.string().email(),
      subject: z.string(),
      body: z.string(),
      urgent: z.boolean().default(false)
    }),
    execute: async ({ to, subject, body, urgent }) => {
      // Real implementation would send email
      console.log(`Sending email to ${to}: ${subject}`);
      return { sent: true, messageId: 'msg-123' };
    }
  }),

  createTask: tool({
    description: 'Create a task in the task management system',
    parameters: z.object({
      title: z.string(),
      description: z.string(),
      assignee: z.string().optional(),
      dueDate: z.string().optional(),
      priority: z.enum(['low', 'medium', 'high']).default('medium')
    }),
    execute: async (params) => {
      return { created: true, taskId: 'task-456', ...params };
    }
  }),

  updateDatabase: tool({
    description: 'Update a record in the database',
    parameters: z.object({
      table: z.string(),
      recordId: z.string(),
      updates: z.record(z.any())
    }),
    execute: async ({ table, recordId, updates }) => {
      return { updated: true, table, recordId };
    }
  })
};

async function actionAgent(instruction: string): Promise<{
  result: string;
  actionsTaken: string[];
}> {
  const actionsTaken: string[] = [];

  const { text } = await generateText({
    model: openai('gpt-4o'),
    tools: actionTools,
    maxSteps: 5,
    prompt: instruction,
    onStepFinish: ({ toolCalls }) => {
      if (toolCalls) {
        for (const call of toolCalls) {
          actionsTaken.push(`${call.toolName}: ${JSON.stringify(call.args)}`);
        }
      }
    }
  });

  return { result: text, actionsTaken };
}
```

### 5. Composable Tool Chains

```typescript
import { tool } from 'ai';
import { z } from 'zod';

// Base tools
const fetchData = tool({
  description: 'Fetch data from an API endpoint',
  parameters: z.object({ endpoint: z.string() }),
  execute: async ({ endpoint }) => ({ data: {} })
});

const transformData = tool({
  description: 'Transform data using a transformation function',
  parameters: z.object({
    data: z.any(),
    transformation: z.enum(['filter', 'map', 'reduce', 'sort'])
  }),
  execute: async ({ data, transformation }) => ({ transformed: data })
});

const storeData = tool({
  description: 'Store data in a destination',
  parameters: z.object({
    data: z.any(),
    destination: z.enum(['database', 'file', 'cache'])
  }),
  execute: async ({ data, destination }) => ({ stored: true })
});

// Composed tool (ETL pipeline)
const etlPipeline = tool({
  description: 'Run full ETL pipeline: extract, transform, load',
  parameters: z.object({
    source: z.string(),
    transformations: z.array(z.enum(['filter', 'map', 'reduce', 'sort'])),
    destination: z.enum(['database', 'file', 'cache'])
  }),
  execute: async ({ source, transformations, destination }) => {
    // Extract
    const { data } = await fetchData.execute({ endpoint: source });

    // Transform (chain transformations)
    let current = data;
    for (const t of transformations) {
      const { transformed } = await transformData.execute({
        data: current,
        transformation: t
      });
      current = transformed;
    }

    // Load
    const { stored } = await storeData.execute({
      data: current,
      destination
    });

    return { success: stored, recordsProcessed: 100 };
  }
});
```

### 6. Error Handling in Tools

```typescript
import { generateText, tool, NoSuchToolError, InvalidToolArgumentsError } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const riskyTools = {
  divideNumbers: tool({
    description: 'Divide two numbers',
    parameters: z.object({
      numerator: z.number(),
      denominator: z.number()
    }),
    execute: async ({ numerator, denominator }) => {
      if (denominator === 0) {
        throw new Error('Division by zero');
      }
      return { result: numerator / denominator };
    }
  }),

  fetchExternalApi: tool({
    description: 'Fetch data from external API',
    parameters: z.object({ url: z.string().url() }),
    execute: async ({ url }) => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      return { data: await response.json() };
    }
  })
};

async function robustToolAgent(query: string): Promise<string> {
  try {
    const { text } = await generateText({
      model: openai('gpt-4o'),
      tools: riskyTools,
      maxSteps: 5,
      prompt: query
    });
    return text;
  } catch (error) {
    if (error instanceof NoSuchToolError) {
      console.error(`Tool not found: ${error.toolName}`);
      return 'I tried to use a tool that doesn\'t exist. Let me try a different approach.';
    }
    if (error instanceof InvalidToolArgumentsError) {
      console.error(`Invalid arguments for ${error.toolName}: ${error.message}`);
      return 'I provided invalid parameters. Let me correct that.';
    }
    // Tool execution error
    console.error('Tool execution failed:', error);
    return 'I encountered an error while executing a tool. Please try again.';
  }
}
```

## Best Practices

1. **Clear descriptions** - LLM uses descriptions to decide which tool to use
2. **Validate parameters** - Use Zod for runtime validation
3. **Descriptive parameter names** - `userEmail` better than `email`
4. **Handle errors gracefully** - Tools can fail; plan for it
5. **Idempotent when possible** - Safe to retry on failure
6. **Log tool usage** - Essential for debugging and auditing
7. **Rate limit external calls** - Protect against runaway agents

## Anti-Patterns to Avoid

- **Vague descriptions**: "Does stuff with data" won't help the LLM choose correctly
- **Overly broad tools**: One tool that does everything is hard to use correctly
- **No error handling**: Tools will fail; handle it
- **Unbounded execution**: Always set maxSteps
- **Sensitive data in parameters**: Don't pass API keys through tool params

## Tool Description Guidelines

```typescript
// BAD: Vague
const badTool = tool({
  description: 'Gets data',
  // ...
});

// GOOD: Specific and actionable
const goodTool = tool({
  description: 'Fetch user profile by ID. Returns name, email, and preferences. Use when you need user details.',
  parameters: z.object({
    userId: z.string().describe('The unique user identifier (UUID format)')
  }),
  // ...
});
```
