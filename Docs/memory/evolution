# 🧠 Memory Module Evolution: From "Turn-Based" to "Token-Aware"

> "In the context of Document Agents, the essence of memory is maintaining task trajectory coherence, not merely echoing dialogues."

### 📅 Project Milestones

#### **v3.0 - Dynamic Token Window Management (Current)** `2026-01-18`

* **Core Philosophy:** Real-time actuarial calculation based on model capacity to ensure core instructions are never lost.
* **Key Improvements:**
* **Differential Retention:** Permanently anchor the `System Prompt`; retain **Full Text** only for the most recent 2 turns to preserve immediate context.
* **Semantic Compression (Summary):** Apply **Summarization** to ultra-long Markdown parsing results and raw tool outputs from intermediate turns.
* **Granular Pruning:** Automatically identify and filter out noise, such as retrieval debug logs or error messages (e.g., "Search failed").


* **Value:** Completely resolves **Context Overflow** in long-document RAG scenarios, significantly enhancing Agent decision stability.

#### **v2.0 - Fixed K-Turn Memory (Window-based)** `2026-01-04`

* **Approach:** Implemented a fixed sliding window (e.g., ) to keep the last 6 dialogue exchanges.
* **Pain Points:** When encountering massive Markdown fragments, fixed turn counts fail to limit total tokens. This frequently triggered **Context Overflow**, causing the Agent to suffer "instant amnesia."

#### **v1.0 - Raw Data Persistence (Naive Storage)** `2025-12-22`

* **Approach:** Full persistence of all raw tool outputs directly into the context.
* **Pain Points:** **Severe Context Pollution**. Massive amounts of irrelevant document snippets, intermediate debugging info, and redundant error prompts polluted the prompt, often misleading the model.

---

## ⚖️ Architecture Comparison

| Feature | v1.0 Raw Persistence | v2.0 Fixed K-Turns | v3.0 Dynamic Token Management |
| --- | --- | --- | --- |
| **Criteria** | Unrestricted | Number of turns (e.g., K=6) | **Available Token Space** |
| **Long-Doc Tolerance** | Extremely Low (Immediate Overflow) | Low (Prone to Overflow) | **Extremely High (Auto-Summarization)** |
| **Data Purity** | High Noise / Debug Info | Contains Redundant Raw Data | **Refined (Trajectory Summaries Only)** |
| **Stability** | Poor | Unstable | **Robust (Core Instructions Anchored)** |

---

## 💡 Insights

* **Distinguishing "User Corpus" from "Tool Artifacts":** The failure of v1.0 stemmed from treating "intermediate processes" as "dialogue content." In RAG scenarios, tool-returned data requires **secondary processing** before entering memory.
* **Ephemeral Memory vs. Retrieval Trajectory:** A memory system should act as a **filter**, not just storage. The v3.0 transition taught me that an efficient Agent must dynamically balance "historical breadth" and "informational depth" in every turn.

---

## 🔮 Roadmap & Future Challenges

* [ ] **Semantic Importance Scoring:** Introduce model-based scoring to prioritize the retention of memory fragments that contribute most to the current task.
* [ ] **Long-term Memory Mounting:** Integrate vector databases to implement "Long-term Memory Retrieval" triggered by semantic relevance.
