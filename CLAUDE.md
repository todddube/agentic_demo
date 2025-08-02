# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CarMax store simulation system featuring multi-agent AI collaboration using Ollama's llama3.2 model with an advanced real-time pygame visualization interface.

## Core Architecture

### Agent System (`app/agent_system.py`)
- **BaseAgent**: Abstract base class with common agent functionality
- **Specialized Agents**: SalesConsultantAgent, AppraisalManagerAgent, FinanceManagerAgent, StoreManagerAgent
- **AgentOrchestrator**: Central coordinator managing task distribution and visualization callbacks
- **OllamaClient**: HTTP client for Ollama API communication with interaction tracking
- All agents follow a task-based processing model with status management (IDLE, WORKING, COMPLETED, ERROR)

### Visualization System (`app/unified_visualizer.py`)
- Single pygame window with resizable graphics and text panels
- Real-time animations: pulsing effects, particles, lightning strikes, matrix rain
- Interactive elements: draggable agent nodes, resizable panels
- Responsive design with auto-scaling fonts and adaptive layout
- Position persistence via `app/agent_positions.json`

### Integration Pattern
The system uses an observer pattern where the AgentOrchestrator communicates with the visualizer through callbacks:
- `start_callback()`, `complete_callback()`, `log_callback()`
- Decoupled architecture allowing independent development of agents and UI

## Development Commands

```bash
# Recommended startup (includes dependency checking)
python launch_demo.py

# Direct execution of main demo (from app directory)
cd app && python simple_demo.py

# Windows convenience launcher (from app directory)
cd app && run_carmax_demo.bat

# Install dependencies
pip install -r app/requirements.txt
```

## Prerequisites

1. **Ollama Setup**:
   - Install Ollama from https://ollama.ai
   - Start service: `ollama serve`
   - Download model: `ollama pull llama3.2`

2. **Python Dependencies**: Enhanced requirements with modern async libraries
   - `pip install -r app/requirements.txt`
   - Includes: aiohttp, pydantic, pygame, rich, ollama client

## Key Files and Entry Points

- **`launch_demo.py`**: Cross-platform launcher with dependency validation (root directory)
- **`app/simple_demo.py`**: Main demo with 8 CarMax scenarios and complete visualization
- **`app/agent_system.py`**: Core agent classes and orchestration logic
- **`app/unified_visualizer.py`**: Pygame interface with advanced animations
- **`app/agent_positions.json`**: UI layout persistence (auto-generated)

## Code Patterns and Conventions

### Agent Development
- Inherit from `BaseAgent` for new agent types
- Override `get_system_prompt()` for role-specific behavior
- Use type hints and comprehensive docstrings (PEP 8 compliant)
- Implement proper error handling with detailed logging

### UI Integration
- Use callback functions for agent-to-UI communication
- Maintain separation between business logic and visualization
- Follow responsive design patterns for window resizing
- Persist UI state through JSON configuration

### Testing and Validation
- The system includes automatic Ollama connection testing
- Dependency validation with guided installation
- Error recovery mechanisms with user guidance
- Performance monitoring for agent task completion

## Architecture Notes

The codebase follows a modular MVC-like pattern:
- **Model**: Agent system with specialized roles and task processing
- **View**: Pygame visualizer with animations and interactive elements  
- **Controller**: AgentOrchestrator managing coordination and callbacks

This design enables independent development of agents, UI features, and orchestration logic while maintaining clean integration points.