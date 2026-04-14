# 🧠 Claude like llm from scratch

This project is my implementation of an AI coding assistant inspired by Claude Code, built as part of the CodeCrafters challenge.

Instead of treating it like a black box, this project focuses on understanding how LLM-powered agents actually work internally — including tool calling, reasoning loops, and API interactions.

---

## 🚀 Overview

The goal of this project is to build a minimal but functional coding assistant that can:

- Interact with an LLM via HTTP APIs
- Understand and process user prompts
- Perform tool/function calls
- Run in an agent loop (think → act → observe → repeat)

---

## 🏗️ Architecture

Core components:

- **LLM Interface**  
  Handles API calls and responses from the language model

- **Agent Loop**  
  Controls the reasoning cycle:
