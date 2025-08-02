# 🚗 CarMax Store Team Demo with Ollama

A modern CarMax store simulation featuring AI-powered team collaboration using Ollama's llama3.2 model. Experience real-time visualization of store operations with enhanced performance, async patterns, and optimized console readability.

## ✨ Latest Updates (v0.8.0)

### 🚀 **Modern Agentic Patterns**
- **Async Ollama Client** with aiohttp and structured outputs
- **Enhanced Agent Tools** - each agent has specialized tool sets and knowledge bases
- **Retry & Resilience** - exponential backoff and error recovery
- **Structured Task Models** using Pydantic for better validation

### 🎮 **Pygame Optimizations** 
- **Smart Font System** - automatic detection of JetBrains Mono, Fira Code, etc.
- **Dynamic Console Text** - responsive line heights and anti-aliasing
- **Better Readability** - smaller, denser console font with improved spacing
- **Performance Improvements** - optimized text rendering and wrapping

### 📱 **Enhanced User Experience**
- **Improved Error Handling** - comprehensive task tracking and status management
- **Better Console Output** - word-aware text truncation and dynamic spacing
- **Modern Dependencies** - updated to latest async libraries and patterns

## 🎮 Live Store Visualization

✨ **Real-time CarMax store interface:**
- **Team Network** - Interactive agent nodes with drag & drop
- **Live Animations** - Visual effects for task processing and completion  
- **Readable Console** - Optimized font rendering with smart text wrapping
- **Performance Metrics** - Real-time counters and status indicators
- **Resizable Interface** - Fully adaptive layout with font scaling

🏪 **Enhanced CarMax Team:**
- **🚗 Mike Rodriguez** - Sales Pro with inventory search & price calculator tools
- **📊 Sarah Chen** - Vehicle Expert with market analyzer & condition assessor
- **💰 David Williams** - Finance Wizard with loan calculator & credit analyzer  
- **🏆 Jennifer Thompson** - Team Leader with performance dashboard & process optimizer

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Ollama from https://ollama.ai
ollama serve
ollama pull llama3.2

# Install Python dependencies 
pip install -r app/requirements.txt
```

### 2. Launch Demo
```bash
# Smart launcher (recommended)
python launch_demo.py

# Or run directly from app folder
cd app && python simple_demo.py
```

## 📁 Project Structure

```
agentic_demo/
├── launch_demo.py              # Cross-platform launcher
├── app/                        # Main application folder
│   ├── agent_system.py         # Enhanced agent classes with async patterns
│   ├── unified_visualizer.py   # Optimized pygame interface  
│   ├── simple_demo.py          # Main demo with 8 CarMax scenarios
│   ├── requirements.txt        # Modern dependencies (aiohttp, pydantic, etc.)
│   └── agent_positions.json    # UI layout persistence
├── CLAUDE.md                   # Development guidelines
└── README.md                   # This file
```

## 🎮 Interface Controls

**Console Panel (Enhanced Readability):**
- **📝 Smart Text Display** - Optimized fonts with better line spacing
- **🔤 Font Controls** - Ctrl+/- to scale, Ctrl+0 to reset
- **📏 Dynamic Layout** - Intelligent text wrapping and truncation
- **⌨️ Keyboard Nav** - ↑↓ scroll, Space auto-scroll, D details

**Graphics Panel (Interactive):**
- **🖱️ Drag Agents** - Customize team layout
- **📊 Live Status** - Color-coded agent states and animations
- **✨ Visual Effects** - Particles, pulses, and completion animations
- **📏 Resizable** - Drag panel divider to adjust layout

## ✨ Key Technical Features

✅ **Modern Async Architecture** - aiohttp client with structured outputs  
✅ **Enhanced Agent Tools** - specialized capabilities per role  
✅ **Smart Error Handling** - retry logic and graceful degradation  
✅ **Optimized Console** - better fonts, spacing, and readability  
✅ **Performance Tuned** - efficient rendering and text processing  
✅ **Responsive Design** - adaptive layout and font scaling  
✅ **Professional UI** - smooth animations and interactive elements  

## 🛠️ Troubleshooting

### Common Issues
1. **Ollama Connection**: Ensure `ollama serve` is running on port 11434
2. **Dependencies**: Run `pip install -r app/requirements.txt` 
3. **Font Issues**: The system auto-detects best available monospace fonts
4. **Performance**: Resize window smaller or adjust font scaling for better performance

### Performance Tips
- Use GPU acceleration with Ollama if available
- Smaller window sizes render faster
- Lower font scales (Ctrl+-) improve text rendering
- Try `llama3.2:1b` for faster responses during testing

## Example Output

```
🚗 CARMAX STORE DEMO 🚗
Enhanced with modern async patterns and optimized UI

✅ Ollama connection successful!
👥 Enhanced Agent Team Ready:
   • 🚗 Mike Rodriguez - Sales Pro (inventory_search, price_calculator)
   • 📊 Sarah Chen - Vehicle Expert (market_analyzer, condition_assessor)  
   • 💰 David Williams - Finance Wizard (loan_calculator, credit_analyzer)
   • 🏆 Jennifer Thompson - Team Leader (performance_dashboard)

📋 Processing 8 customer scenarios with enhanced tools...
✨ [ASSIGN] Task 001 → Mike Rodriguez - Sales Pro
   [COMPLETE] Comprehensive vehicle recommendation with pricing

🎉 All tasks completed with improved error handling!
🎮 Optimized CarMax Store System running!
```

---

**🚗 Experience the enhanced CarMax difference with modern AI-powered team simulation!**

## License

Educational demonstration project showcasing modern Python async patterns, pygame optimization, and enhanced AI agent orchestration.