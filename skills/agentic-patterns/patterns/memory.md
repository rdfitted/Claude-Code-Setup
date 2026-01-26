# Memory Pattern

Persisting and retrieving context across conversations and agent interactions.

## When to Use

- Long conversations exceeding context windows
- Knowledge that should persist across sessions
- Personalization based on history
- RAG (Retrieval-Augmented Generation) systems
- Multi-turn task execution

## Pattern Variants

### 1. Conversation Memory (Sliding Window)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

class ConversationMemory {
  private messages: Message[] = [];
  private maxMessages: number;

  constructor(maxMessages: number = 20) {
    this.maxMessages = maxMessages;
  }

  add(role: 'user' | 'assistant', content: string): void {
    this.messages.push({ role, content, timestamp: new Date() });

    // Sliding window: remove oldest when limit exceeded
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(-this.maxMessages);
    }
  }

  getContext(): string {
    return this.messages
      .map(m => `${m.role}: ${m.content}`)
      .join('\n');
  }

  getMessages(): Message[] {
    return [...this.messages];
  }
}

async function chatWithMemory(
  memory: ConversationMemory,
  userMessage: string
): Promise<string> {
  memory.add('user', userMessage);

  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: 'You are a helpful assistant with memory of our conversation.',
    prompt: `Conversation history:
${memory.getContext()}

Respond to the latest message.`
  });

  memory.add('assistant', text);
  return text;
}

// Usage
const memory = new ConversationMemory(20);
await chatWithMemory(memory, "My name is Alice");
await chatWithMemory(memory, "What's my name?"); // Should remember Alice
```

### 2. Summary Memory (Compression)

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

class SummaryMemory {
  private summary: string = '';
  private recentMessages: string[] = [];
  private recentLimit: number;
  private summaryThreshold: number;

  constructor(recentLimit: number = 5, summaryThreshold: number = 10) {
    this.recentLimit = recentLimit;
    this.summaryThreshold = summaryThreshold;
  }

  async add(role: string, content: string): Promise<void> {
    this.recentMessages.push(`${role}: ${content}`);

    // Compress when threshold exceeded
    if (this.recentMessages.length >= this.summaryThreshold) {
      await this.compress();
    }
  }

  private async compress(): Promise<void> {
    const toCompress = this.recentMessages.slice(0, -this.recentLimit);
    this.recentMessages = this.recentMessages.slice(-this.recentLimit);

    const { text: newSummary } = await generateText({
      model: openai('gpt-4o-mini'),
      prompt: `Summarize this conversation, preserving key facts and context:

Previous summary: ${this.summary || 'None'}

New messages to summarize:
${toCompress.join('\n')}

Create a concise summary.`
    });

    this.summary = newSummary;
  }

  getContext(): string {
    return `Summary of earlier conversation:
${this.summary || 'No previous history'}

Recent messages:
${this.recentMessages.join('\n')}`;
  }
}

async function chatWithSummaryMemory(
  memory: SummaryMemory,
  userMessage: string
): Promise<string> {
  await memory.add('user', userMessage);

  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: 'You are a helpful assistant.',
    prompt: `${memory.getContext()}

Respond to the latest user message.`
  });

  await memory.add('assistant', text);
  return text;
}
```

### 3. Vector Memory (RAG)

```typescript
import { embed, embedMany, cosineSimilarity, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

interface MemoryEntry {
  id: string;
  content: string;
  embedding: number[];
  metadata: Record<string, any>;
  timestamp: Date;
}

class VectorMemory {
  private entries: MemoryEntry[] = [];
  private embeddingModel = openai.embedding('text-embedding-3-small');

  async store(content: string, metadata: Record<string, any> = {}): Promise<void> {
    const { embedding } = await embed({
      model: this.embeddingModel,
      value: content
    });

    this.entries.push({
      id: crypto.randomUUID(),
      content,
      embedding,
      metadata,
      timestamp: new Date()
    });
  }

  async storeBatch(items: { content: string; metadata?: Record<string, any> }[]): Promise<void> {
    const { embeddings } = await embedMany({
      model: this.embeddingModel,
      values: items.map(i => i.content)
    });

    for (let i = 0; i < items.length; i++) {
      this.entries.push({
        id: crypto.randomUUID(),
        content: items[i].content,
        embedding: embeddings[i],
        metadata: items[i].metadata || {},
        timestamp: new Date()
      });
    }
  }

  async search(query: string, topK: number = 5): Promise<MemoryEntry[]> {
    const { embedding: queryEmbedding } = await embed({
      model: this.embeddingModel,
      value: query
    });

    // Calculate similarities
    const scored = this.entries.map(entry => ({
      entry,
      score: cosineSimilarity(queryEmbedding, entry.embedding)
    }));

    // Return top K
    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)
      .map(s => s.entry);
  }
}

async function ragChat(
  memory: VectorMemory,
  query: string
): Promise<string> {
  // Retrieve relevant memories
  const relevantMemories = await memory.search(query, 5);

  const context = relevantMemories
    .map(m => m.content)
    .join('\n\n');

  // Generate response with context
  const { text } = await generateText({
    model: openai('gpt-4o'),
    prompt: `Use this context to answer the question:

Context:
${context}

Question: ${query}

Answer based on the context provided.`
  });

  // Optionally store the interaction
  await memory.store(`Q: ${query}\nA: ${text}`, { type: 'qa' });

  return text;
}
```

### 4. Episodic Memory (Structured Events)

```typescript
import { generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const EpisodeSchema = z.object({
  summary: z.string(),
  entities: z.array(z.string()),
  topics: z.array(z.string()),
  sentiment: z.enum(['positive', 'neutral', 'negative']),
  importance: z.number().min(1).max(10)
});

interface Episode {
  id: string;
  raw: string;
  parsed: z.infer<typeof EpisodeSchema>;
  timestamp: Date;
}

class EpisodicMemory {
  private episodes: Episode[] = [];

  async addEpisode(rawContent: string): Promise<Episode> {
    const { object: parsed } = await generateObject({
      model: openai('gpt-4o-mini'),
      schema: EpisodeSchema,
      prompt: `Extract structured information from this conversation segment:

${rawContent}

Identify key entities, topics, sentiment, and importance (1-10).`
    });

    const episode: Episode = {
      id: crypto.randomUUID(),
      raw: rawContent,
      parsed,
      timestamp: new Date()
    };

    this.episodes.push(episode);
    return episode;
  }

  searchByEntity(entity: string): Episode[] {
    return this.episodes.filter(ep =>
      ep.parsed.entities.some(e =>
        e.toLowerCase().includes(entity.toLowerCase())
      )
    );
  }

  searchByTopic(topic: string): Episode[] {
    return this.episodes.filter(ep =>
      ep.parsed.topics.some(t =>
        t.toLowerCase().includes(topic.toLowerCase())
      )
    );
  }

  getImportantEpisodes(minImportance: number = 7): Episode[] {
    return this.episodes
      .filter(ep => ep.parsed.importance >= minImportance)
      .sort((a, b) => b.parsed.importance - a.parsed.importance);
  }

  getRecent(count: number = 5): Episode[] {
    return this.episodes
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, count);
  }
}
```

### 5. Working Memory (Task Context)

```typescript
import { generateText, generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const WorkingMemorySchema = z.object({
  currentGoal: z.string(),
  subGoals: z.array(z.string()),
  completedSteps: z.array(z.string()),
  keyFacts: z.array(z.string()),
  blockers: z.array(z.string()),
  nextAction: z.string()
});

class WorkingMemory {
  private state: z.infer<typeof WorkingMemorySchema>;

  constructor(goal: string) {
    this.state = {
      currentGoal: goal,
      subGoals: [],
      completedSteps: [],
      keyFacts: [],
      blockers: [],
      nextAction: ''
    };
  }

  async updateFromInteraction(interaction: string): Promise<void> {
    const { object: update } = await generateObject({
      model: openai('gpt-4o-mini'),
      schema: WorkingMemorySchema,
      prompt: `Update working memory based on this interaction:

Current state:
${JSON.stringify(this.state, null, 2)}

New interaction:
${interaction}

Update the working memory state.`
    });

    this.state = update;
  }

  getState(): z.infer<typeof WorkingMemorySchema> {
    return { ...this.state };
  }

  addFact(fact: string): void {
    this.state.keyFacts.push(fact);
  }

  completeStep(step: string): void {
    this.state.completedSteps.push(step);
    this.state.subGoals = this.state.subGoals.filter(g => g !== step);
  }

  addBlocker(blocker: string): void {
    this.state.blockers.push(blocker);
  }

  getContext(): string {
    return `Goal: ${this.state.currentGoal}

Progress:
- Completed: ${this.state.completedSteps.join(', ') || 'None'}
- Remaining: ${this.state.subGoals.join(', ') || 'None'}

Key facts: ${this.state.keyFacts.join('; ') || 'None'}
Blockers: ${this.state.blockers.join('; ') || 'None'}
Next action: ${this.state.nextAction}`;
  }
}
```

### 6. Persistent Memory (Database-Backed)

```typescript
import { embed, cosineSimilarity, generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

// Interface for database operations (implement with your DB)
interface MemoryStore {
  save(entry: { content: string; embedding: number[]; metadata: any }): Promise<string>;
  search(embedding: number[], limit: number): Promise<any[]>;
  getByUser(userId: string, limit: number): Promise<any[]>;
}

class PersistentMemory {
  private store: MemoryStore;
  private embeddingModel = openai.embedding('text-embedding-3-small');

  constructor(store: MemoryStore) {
    this.store = store;
  }

  async remember(content: string, userId: string, metadata: any = {}): Promise<void> {
    const { embedding } = await embed({
      model: this.embeddingModel,
      value: content
    });

    await this.store.save({
      content,
      embedding,
      metadata: { ...metadata, userId, timestamp: new Date().toISOString() }
    });
  }

  async recall(query: string, limit: number = 5): Promise<string[]> {
    const { embedding } = await embed({
      model: this.embeddingModel,
      value: query
    });

    const results = await this.store.search(embedding, limit);
    return results.map(r => r.content);
  }

  async getUserHistory(userId: string, limit: number = 10): Promise<string[]> {
    const results = await this.store.getByUser(userId, limit);
    return results.map(r => r.content);
  }
}

// Example with PostgreSQL + pgvector (conceptual)
/*
CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops);

-- Search query
SELECT content, 1 - (embedding <=> $1) as similarity
FROM memories
ORDER BY embedding <=> $1
LIMIT $2;
*/
```

## Best Practices

1. **Choose right memory type** - Sliding window for short, vector for knowledge
2. **Compress proactively** - Don't wait until context is full
3. **Index embeddings** - Use vector databases for large-scale RAG
4. **Include metadata** - Timestamps, sources, importance scores
5. **Test retrieval quality** - Wrong memories = wrong responses
6. **Handle stale data** - Some memories should expire

## Anti-Patterns to Avoid

- **Unbounded memory**: Will eventually hit context limits
- **No relevance filtering**: Retrieving irrelevant context hurts quality
- **Missing timestamps**: Can't prioritize recent vs. old
- **No compression strategy**: Full conversations don't scale
- **Ignoring token costs**: Embedding/retrieval has costs too

## Memory Selection Guide

| Memory Type | Use Case | Persistence | Scalability |
|-------------|----------|-------------|-------------|
| Sliding Window | Short conversations | Session | Low |
| Summary | Long conversations | Session | Medium |
| Vector (RAG) | Knowledge bases | Persistent | High |
| Episodic | Event tracking | Persistent | Medium |
| Working | Task execution | Task duration | Low |
