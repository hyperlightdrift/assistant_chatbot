# assistant_chatbot
## Work in Progress

This project is a work in progress and currently serves as the foundation for a broader AI-powered assistant.

### Current Capabilities

- Modular command-handling architecture
- Google Calendar integration with:
  - Event creation via natural language input
  - OAuth 2.0 authentication and credential reuse
- Joke module using external APIs
- Natural language date/time parsing with `dateparser` and `parsedatetime`

### Long-Term Vision

The goal of this project is to serve as a **comprehensive showcase of applied AI**. Over time, this assistant will incorporate technologies from across the AI spectrum, including:

| Domain | Planned Features |
|--------|------------------|
| Natural Language Processing | Intent recognition, entity extraction, text classification, sentiment analysis |
| Task Automation | Multi-step scheduling, reminders, Google Workspace integration |
| Conversational AI | Contextual dialogue with retrieval-augmented generation (RAG), LLM assistance |
| Generative AI | Image generation with prompts, text-to-image tools (e.g., DALL·E, Stable Diffusion) |
| Machine Learning | Personalized recommendations, pattern recognition, adaptive behavior |
| Computer Vision | Webcam-based interaction, image tagging, basic object recognition |
| Multimodal AI | Combine text, image, and audio inputs/outputs |
| Plugin Architecture | Dynamic loading of capabilities (via tools, agents, or commands) |

### Roadmap (Short-Term Goals)

- [ ] Add viewing and deleting of calendar events
- [ ] Expand natural language command parser
- [ ] Add tasks and appointment schedule support for Google Calendar
- [ ] Add initial NLP features (entity extraction using spaCy or Hugging Face)
- [ ] Modular plugin-style loading system for assistant capabilities
- [ ] Begin LLM experimentation (prompt routing, memory, chat UI)

---

This roadmap will evolve as I continue developing and experimenting. The long-term goal is to create a unified, AI-powered assistant that not only automates but intelligently adapts to user needs.
