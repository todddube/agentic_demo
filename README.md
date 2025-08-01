# 🚗 CarMax Store Team Demo with Ollama 3.2

A sophisticated CarMax store simulation featuring AI-powered team members working together using Ollama's llama3.2 model. Experience real-time visualization of store operations with animated graphics, resizable windows, and responsive font scaling that adapts to your display.

## ✨ Latest Improvements

- **🔧 Python Best Practices**: Enhanced code with proper type hints, docstrings, and PEP 8 compliance
- **📏 Window Resizing**: Fully resizable pygame window with intelligent layout adaptation
- **🔤 Responsive Fonts**: Auto-scaling fonts that adapt to window size and panel layout
- **⚡ Performance Optimized**: Improved rendering and animation systems
- **📚 Better Documentation**: Comprehensive type hints and docstrings throughout

## 🎮 Live Store Visualization

✨ **Real-time CarMax store interface:**
- **Team Network** - Circular layout showing all team members and their status
- **Live Animations** - Pulsing effects and particles when team members are helping customers
- **Customer Requests** - Current tasks displayed in real-time
- **Performance Metrics** - Live counters showing completed customer interactions
- **Status Indicators** - Visual feedback for available, busy, and completed states
- **Resizable Interface** - Fully resizable window with adaptive layout and font scaling
- **Professional Design** - Clean, modern display that adapts to any screen size

🏪 **CarMax Store Team:**
- **Mike Rodriguez** 🏆 - Sales Consultant who helps customers find vehicles
- **Sarah Chen** 📊 - Appraisal Manager who evaluates vehicle values  
- **David Williams** � - Finance Manager who structures payment deals
- **Jennifer Thompson** � - Store Manager who oversees operations

## 🚀 Running the Demo

### Cross-Platform Launcher (RECOMMENDED)
Use the smart launcher with automatic dependency checking:
```bash
python launch_demo.py
```

### Direct Launch
Run the main demo directly:
```bash
python simple_demo.py
```

### Windows Users
Double-click `run_carmax_demo.bat` for a guided Windows experience.

The demo opens a fully resizable pygame window showing:
- **Graphics Panel:** Animated team network with live status updates
- **Text Panel:** Scrollable output with responsive fonts
- **Interactive Controls:** Full mouse and keyboard navigation

## Prerequisites

1. **Ollama Installation:**
   ```bash
   # Download and install Ollama from https://ollama.ai
   # Or use package manager (Windows/Mac/Linux)
   ```

2. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

3. **Download llama3.2 Model:**
   ```bash
   ollama pull llama3.2
   ```

## Prerequisites

1. **Ollama Installation:**
   ```bash
   # Download and install Ollama from https://ollama.ai
   # Or use package manager (Windows/Mac/Linux)
   ```

2. **Start Ollama Service:**
   ```bash
   ollama serve
   ```

3. **Download llama3.2 Model:**
   ```bash
   ollama pull llama3.2
   ```

4. **Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

```bash
# Smart launcher with dependency checking (recommended)
python launch_demo.py

# Or run directly
python simple_demo.py
```

## What the Demo Does

1. **Connection Check** - Verifies Ollama is running and llama3.2 is available
2. **Team Initialization** - Sets up CarMax store team members with specialized roles
3. **Store Interface** - Opens pygame window with real-time team visualization  
4. **Customer Requests** - Creates 8 realistic CarMax scenarios for the team
5. **Task Processing** - Each team member handles their assigned customer requests
6. **Visual Feedback** - Shows working animations, status changes, and completion effects
7. **Results Display** - Shows detailed results and team performance metrics

## 🎮 Interface Controls

**Graphics Panel (Resizable 40-80%):**
- **🏪 Team Network** - Circular layout showing all CarMax team members
- **⚫ Status Indicators** - Color-coded circles showing availability/busy status
- **💫 Work Animations** - Pulsing effects when helping customers
- **✨ Completion Effects** - Animated particles when tasks are finished
- **📊 Live Stats** - Real-time task counts and performance metrics
- **🖱️ Drag & Drop** - Move and resize agent nodes interactively

**Text Panel (Auto-adjusting):**
- **📝 System Output** - Scrollable log of all team activities with responsive fonts
- **⏰ Timestamps** - Track when each customer interaction occurred
- **📋 Interactive Controls** - Scroll, auto-scroll, and view options
- **🎮 Keyboard Controls:** ↑↓ to scroll, Space for auto-scroll, D for details
- **🔤 Font Scaling** - Ctrl+/- to adjust font size, Ctrl+0 to reset
- **📏 Panel Resizing** - Drag the panel divider to adjust layout

**Window Controls:**
- **📏 Resizable Window** - Drag window edges to resize, layout adapts automatically
- **🔤 Auto Font Scaling** - Fonts automatically scale with window size
- **R Key** - Reset agent positions to default circular layout
- **ESC** - Exit the application

## Sample Customer Requests

The demo includes realistic CarMax scenarios such as:
- Helping customers find reliable family SUVs under budget
- Appraising trade-in vehicles with accurate market evaluations  
- Explaining financing options for different credit profiles
- Training new sales consultants on CarMax procedures
- Analyzing electric vehicle market trends
- Reviewing and improving customer service approaches

## 📁 Project Structure

```
agentic_demo/
├── 📄 README.md                    # Project documentation  
├── 📄 requirements.txt             # Python dependencies
├── 🐍 agent_system.py              # CarMax team classes and orchestrator
├── 🐍 unified_visualizer.py        # Real-time pygame visualization engine
├── 🐍 simple_demo.py               # Main CarMax store demo
├── 🐍 launch_demo.py               # Cross-platform launcher with dependency checking
├── 🪟 run_carmax_demo.bat          # Windows convenience launcher
├── 📄 agent_positions.json         # Saved agent positions and customizations
└── 📁 .gitignore                   # Git ignore file (excludes __pycache__)
```

## ✨ Key Features

✅ **Real-time CarMax Store Visualization** with animated team members
✅ **Specialized Team Roles** - Sales, Appraisal, Finance, Management
✅ **Live Status Updates** showing available, busy, and completed states  
✅ **Animated Effects** around active team members
✅ **Performance Monitoring** with live customer service metrics
✅ **Interactive Interface** with customer request progress
✅ **Ollama Integration** using llama3.2 model for realistic responses
✅ **Fully Resizable Window** - adapts to any screen size with intelligent scaling
✅ **Responsive Font System** - fonts auto-scale with window size and panel layout
✅ **Python Best Practices** - type hints, proper documentation, PEP 8 compliance
✅ **Draggable Agent Nodes** - customize team layout by dragging agents
✅ **Professional UI** with adaptive design and smooth animations
✅ **Clean Codebase** - removed redundant files, optimized structure
✅ **Cross-Platform Launcher** - smart dependency checking and installation

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check if llama3.2 is installed: `ollama list`
   - Verify Ollama is accessible at http://localhost:11434

2. **Import Errors**
   - Install missing packages: `pip install -r requirements.txt`
   - Ensure pygame is installed: `pip install pygame`

3. **Model Not Found**
   - Download the model: `ollama pull llama3.2`
   - Wait for download to complete (model is ~2GB)

4. **Window Size Issues**
   - The interface is fully resizable - drag window edges to adjust size
   - Fonts automatically scale with window size for optimal readability
   - Minimum recommended resolution: 1024x768
   - Use Ctrl+/- to manually adjust font sizes if needed

### Performance Tips

- Use GPU acceleration if available with Ollama
- Adjust response length in agent system prompts
- Close other resource-intensive applications
- Use smaller model variants like `llama3.2:1b` for testing
- **Window Size**: Smaller windows render faster - resize as needed
- **Font Scaling**: Lower font scales (Ctrl+-) can improve text rendering performance
- **Panel Layout**: Adjust graphics/text panel ratio for optimal performance

## Example Output

```
🚗 CARMAX STORE DEMO 🚗
Multi-Agent CarMax Store System
Team: Sales 🏆 | Appraisal 📊 | Finance 💰 | Manager 👔

✅ Ollama connection successful!
👥 Agent Team Ready:
   • Mike Rodriguez - Sales - CarMax Sales Consultant
   • Sarah Chen - Appraisal - CarMax Appraisal Manager  
   • David Williams - Finance - CarMax Finance Manager
   • Jennifer Thompson - Store Manager - CarMax Store Manager

📋 Creating 8 tasks for the team...
✨ Processing customer requests...

[1/8] Mike Rodriguez - Sales is working...
Task: Help a customer find a reliable family SUV under $25,000
✅ Completed at 14:32:15

[2/8] Sarah Chen - Appraisal is working...
Task: Appraise a 2018 Honda Civic with 45,000 miles  
✅ Completed at 14:32:28

🎉 All tasks completed successfully!
🎮 CarMax Store System is running!
```

---

**🚗 Experience the CarMax difference with AI-powered team simulation!**

## 🛠️ Technical Implementation

### Code Quality
- **Type Hints**: Comprehensive type annotations throughout
- **Documentation**: Detailed docstrings for all classes and methods
- **PEP 8 Compliance**: Consistent code formatting and style
- **Error Handling**: Robust exception handling and logging

### UI Features
- **Responsive Layout**: Window resizing with proportional scaling
- **Font Management**: Dynamic font sizing based on window dimensions
- **Interactive Elements**: Draggable agents, resizable panels
- **Animation System**: Smooth visual effects and state transitions

### Architecture
- **Agent System**: Modular agent classes with clear interfaces
- **Event Handling**: Comprehensive pygame event processing
- **State Management**: Clean separation of UI and business logic
- **Callback System**: Decoupled communication between components

## License

This is a demonstration project for educational purposes showcasing modern Python development practices, pygame GUI design, and AI agent orchestration. Feel free to modify and extend for your own projects.
