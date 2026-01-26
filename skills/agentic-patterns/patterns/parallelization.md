# Parallelization Pattern

Execute multiple independent tasks concurrently to reduce total latency and improve throughput.

## When to Use

- Multiple independent subtasks
- Batch processing
- Multi-perspective analysis
- Voting/ensemble approaches
- Speed-critical applications

## Pattern Variants

### 1. Simple Parallel Execution

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

interface AnalysisResult {
  technical: string;
  business: string;
  user: string;
}

async function parallelAnalysis(document: string): Promise<AnalysisResult> {
  const model = openai('gpt-4o');

  // Execute all analyses in parallel
  const [technical, business, user] = await Promise.all([
    generateText({
      model,
      system: 'You are a technical architect. Focus on implementation details.',
      prompt: `Analyze this document from a technical perspective:\n\n${document}`
    }),
    generateText({
      model,
      system: 'You are a business analyst. Focus on ROI and market impact.',
      prompt: `Analyze this document from a business perspective:\n\n${document}`
    }),
    generateText({
      model,
      system: 'You are a UX researcher. Focus on user experience impact.',
      prompt: `Analyze this document from a user perspective:\n\n${document}`
    })
  ]);

  return {
    technical: technical.text,
    business: business.text,
    user: user.text
  };
}
```

### 2. Parallel with Aggregation

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const ReviewSchema = z.object({
  score: z.number().min(1).max(10),
  strengths: z.array(z.string()),
  weaknesses: z.array(z.string()),
  recommendation: z.enum(['approve', 'revise', 'reject'])
});

async function parallelCodeReview(code: string): Promise<{
  reviews: z.infer<typeof ReviewSchema>[];
  consensus: string;
}> {
  const model = openai('gpt-4o');

  // Multiple reviewers in parallel
  const reviewPromises = [
    'security expert focusing on vulnerabilities',
    'performance expert focusing on efficiency',
    'maintainability expert focusing on code quality'
  ].map(role =>
    generateObject({
      model,
      schema: ReviewSchema,
      system: `You are a ${role}. Review code thoroughly.`,
      prompt: `Review this code:\n\n${code}`
    })
  );

  const results = await Promise.all(reviewPromises);
  const reviews = results.map(r => r.object);

  // Aggregate reviews
  const avgScore = reviews.reduce((sum, r) => sum + r.score, 0) / reviews.length;
  const allStrengths = reviews.flatMap(r => r.strengths);
  const allWeaknesses = reviews.flatMap(r => r.weaknesses);

  // Generate consensus
  const { text: consensus } = await generateText({
    model,
    prompt: `Synthesize these code reviews into a final recommendation:

Reviews:
${reviews.map((r, i) => `
Reviewer ${i + 1}:
- Score: ${r.score}/10
- Strengths: ${r.strengths.join(', ')}
- Weaknesses: ${r.weaknesses.join(', ')}
- Recommendation: ${r.recommendation}
`).join('\n')}

Provide a balanced final assessment.`
  });

  return { reviews, consensus };
}
```

### 3. Voting/Ensemble Pattern

```typescript
import { generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const ClassificationSchema = z.object({
  category: z.enum(['spam', 'ham', 'uncertain']),
  confidence: z.number().min(0).max(1)
});

async function ensembleClassification(text: string): Promise<{
  finalCategory: string;
  confidence: number;
  votes: Record<string, number>;
}> {
  // Multiple models vote in parallel
  const models = [
    openai('gpt-4o'),
    openai('gpt-4o-mini'),
    anthropic('claude-sonnet-4-20250514')
  ];

  const votes = await Promise.all(
    models.map(model =>
      generateObject({
        model,
        schema: ClassificationSchema,
        prompt: `Classify this text as spam or ham (not spam):

"${text}"

Be confident in your classification.`
      })
    )
  );

  // Count votes
  const voteCounts: Record<string, number> = {};
  let weightedConfidence = 0;

  for (const { object } of votes) {
    voteCounts[object.category] = (voteCounts[object.category] || 0) + 1;
    weightedConfidence += object.confidence;
  }

  // Find winner
  const winner = Object.entries(voteCounts)
    .sort((a, b) => b[1] - a[1])[0];

  return {
    finalCategory: winner[0],
    confidence: weightedConfidence / votes.length,
    votes: voteCounts
  };
}
```

### 4. Chunked Parallel Processing

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

function chunkArray<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  return chunks;
}

async function parallelBatchProcessing(
  items: string[],
  concurrencyLimit: number = 5
): Promise<string[]> {
  const model = openai('gpt-4o-mini');
  const results: string[] = [];

  // Process in chunks to avoid rate limits
  const chunks = chunkArray(items, concurrencyLimit);

  for (const chunk of chunks) {
    const chunkResults = await Promise.all(
      chunk.map(item =>
        generateText({
          model,
          prompt: `Summarize: ${item}`
        })
      )
    );

    results.push(...chunkResults.map(r => r.text));
  }

  return results;
}
```

### 5. Parallel with Timeout and Fallback

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

async function withTimeout<T>(
  promise: Promise<T>,
  ms: number,
  fallback: T
): Promise<T> {
  const timeout = new Promise<T>((resolve) =>
    setTimeout(() => resolve(fallback), ms)
  );
  return Promise.race([promise, timeout]);
}

async function resilientParallel(queries: string[]): Promise<string[]> {
  const model = openai('gpt-4o');
  const TIMEOUT_MS = 10000;
  const FALLBACK = 'Response unavailable';

  const results = await Promise.all(
    queries.map(query =>
      withTimeout(
        generateText({ model, prompt: query }).then(r => r.text),
        TIMEOUT_MS,
        FALLBACK
      )
    )
  );

  return results;
}
```

### 6. Map-Reduce Pattern

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

async function mapReduceSummarization(documents: string[]): Promise<string> {
  const model = openai('gpt-4o');

  // MAP: Summarize each document in parallel
  const summaries = await Promise.all(
    documents.map(doc =>
      generateText({
        model,
        prompt: `Summarize this document in 2-3 sentences:\n\n${doc}`
      })
    )
  );

  // REDUCE: Combine summaries into final summary
  const { text: finalSummary } = await generateText({
    model,
    prompt: `Synthesize these summaries into one coherent summary:

${summaries.map((s, i) => `Document ${i + 1}: ${s.text}`).join('\n\n')}

Create a unified summary covering all key points.`
  });

  return finalSummary;
}
```

## Best Practices

1. **Identify true independence** - Only parallelize genuinely independent tasks
2. **Respect rate limits** - Use chunking to avoid API throttling
3. **Add timeouts** - Prevent slow tasks from blocking everything
4. **Handle partial failures** - Use Promise.allSettled for resilience
5. **Aggregate thoughtfully** - Combining results often needs its own LLM call
6. **Monitor costs** - Parallel = multiplied API calls

## Anti-Patterns to Avoid

- **Parallelizing dependent tasks**: If B needs A's output, they're not parallel
- **Ignoring rate limits**: Will cause 429 errors and backoff delays
- **No error handling**: One failure shouldn't crash everything
- **Over-parallelization**: 100 parallel calls will hit limits

## Performance Comparison

```typescript
// Sequential: 3 calls × 2s each = 6s total
// Parallel: 3 calls simultaneously = 2s total (3x faster)

// But watch for rate limits:
// 100 parallel calls might hit 429s
// Better: 10 chunks of 10 = still fast, no throttling
```

## Promise.allSettled for Resilience

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

async function resilientParallelProcessing(tasks: string[]): Promise<{
  successes: string[];
  failures: number;
}> {
  const model = openai('gpt-4o');

  const results = await Promise.allSettled(
    tasks.map(task =>
      generateText({ model, prompt: task })
    )
  );

  const successes = results
    .filter((r): r is PromiseFulfilledResult<any> => r.status === 'fulfilled')
    .map(r => r.value.text);

  const failures = results.filter(r => r.status === 'rejected').length;

  return { successes, failures };
}
```
