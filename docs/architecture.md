# Architecture Overview

## System Goal

The Personal Continuity Agent is designed to preserve long-term coherence across user interactions.

It is not just a memory store. It is a continuity system that transforms raw events into evolving models of goals, identity, behavior, and unresolved trajectories.

## Core Pipeline

```txt
User Event
   ↓
Event Memory
   ↓
Salience Engine
   ↓
Identity Model
   ↓
Temporal Reasoning
   ↓
Reflection Engine
   ↓
Continuity Policies
```

## 1. Event Memory

Captures structured events such as:

- conversations
- goals
- decisions
- commitments
- routines
- emotional signals
- behavioral traces

Each event should include timestamp, source, content, tags, importance, and optional links to related events.

## 2. Salience Engine

Scores events based on:

- recurrence
- emotional intensity
- goal relevance
- identity relevance
- novelty
- unresolved tension

The purpose is to prevent the system from treating all memories equally.

## 3. Identity Model

Maintains an evolving model of the user, including:

- values
- beliefs
- motivations
- behavioral tendencies
- contradictions
- aspirations

The identity model should be evidence-backed, probabilistic, and revision-friendly.

## 4. Temporal Reasoning Engine

Tracks patterns across time:

- goal drift
- abandoned intentions
- recurring loops
- behavior changes
- unresolved commitments
- momentum and decay

## 5. Reflection Engine

Periodically converts raw memory into higher-order synthesis:

- weekly summaries
- identity updates
- pattern detection
- contradiction detection
- continuity recovery briefs

## 6. Continuity Policies

Defines what to remember, compress, forget, reinforce, or escalate.

Example policy categories:

- permanent identity memories
- time-decaying operational memories
- recurring pattern memories
- low-value conversational noise
- high-salience unresolved loops

## Design Principle

Memory is storage.

Continuity is structured change across time.
