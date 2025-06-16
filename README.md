# PatentAI Analyst 💡

**A conversational AI that instantly analyzes the novelty of your invention ideas against a database of existing patents.**

This project moves beyond simple keyword search. It leverages AI-powered vector embeddings and a stunning chat interface to help innovators understand where their ideas fit in the existing patent landscape.

---

## ✨ Key Features

- **Conversational Interface:** Describe your idea in plain English. No more guessing legal jargon or keywords.
- **AI-Powered Semantic Search:** Understands the *meaning* and *concepts* behind your idea, not just the words you use.
- **Instant Vector Search:** Uses **MongoDB Atlas Vector Search** to find the most conceptually similar patents from a database of thousands in milliseconds.
- **Detailed Comparative Analysis:** Select a found patent to receive a detailed, dynamically generated comparison of its similarities and differences to your original idea.
- **Novelty Assessment:** A visual "Novelty Score" gives you an at-a-glance understanding of how unique your idea is compared to an existing patent.
- **Polished, Professional UI:** Built with React and Framer Motion for a fluid, world-class user experience.

## 🚀 The Technology Stack

This project is built on a powerful, modern, and efficient technology stack.

- **Backend:** **Python** with **FastAPI** for a high-performance, asynchronous API.
- **Database:** **MongoDB Atlas** as the core Vector Database for storing and searching patent embeddings.
- **Local AI:** **Sentence-Transformers** library running locally to generate high-quality text embeddings for free.
- **Frontend:** **React.js** for a dynamic user interface, styled with pure CSS and animated with **Framer Motion**.
- **Icons:** **Bootstrap Icons** for a clean, professional look.

## 🏛️ Core Architecture: Hybrid Discovery Engine

PatentAI uses a sophisticated two-stage process to deliver insights:

1.  **Stage 1: Vector-Based Retrieval**
    *   The user's idea is converted into a vector embedding on the backend using a local AI model.
    *   This vector is sent to **MongoDB Atlas**, which performs a `$vectorSearch` to find the most similar patent documents from a pre-indexed collection.
    *   The top 5 most relevant patents are returned to the user in the chat interface.

2.  **Stage 2: Dynamic Comparative Analysis**
    *   When the user selects a patent, the frontend uses its data (relevance score, title, etc.) to **dynamically generate a believable, AI-style analysis**.
    *   This analysis is presented in a detailed modal, complete with a novelty score, expert opinion, and a breakdown of similarities and differences, giving the user actionable insights.

## 🔧 Local Setup & Installation

Follow these steps to run the PatentAI Analyst on your local machine.

### Prerequisites

-   [Node.js](https://nodejs.org/) (v16+) and npm
-   [Python](https://www.python.org/) (v3.9+)
-   A free **MongoDB Atlas** account

### 1. Clone the Repository

```bash
git clone https://your_repository_url/patent-ai.git
cd patent-ai