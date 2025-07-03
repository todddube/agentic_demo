# 🚗 CarMax Store Team Demo with Ollama 3.2

A CarMax store simulation featuring AI-powered team members working together using Ollama's llama3.2 model. Experience real-time visualization of store operations with animated graphics showing team interactions and customer service activities!

## 🎮 Live Store Visualization

✨ **Real-time CarMax store interface:**
- **Team Network** - Circular layout showing all team members and their status
- **Live Animations** - Pulsing effects and particles when team members are helping customers
- **Customer Requests** - Current tasks displayed in real-time
- **Performance Metrics** - Live counters showing completed customer interactions
- **Status Indicators** - Visual feedback for available, busy, and completed states
- **Professional Interface** - Clean, modern display sized to 75% of your screen

🏪 **CarMax Store Team:**
- **Mike Rodriguez** 🏆 - Sales Consultant who helps customers find vehicles
- **Sarah Chen** 📊 - Appraisal Manager who evaluates vehicle values  
- **David Williams** � - Finance Manager who structures payment deals
- **Jennifer Thompson** � - Store Manager who oversees operations

## 🚀 Running the Demo

### CarMax Store Interface (RECOMMENDED)
Real-time pygame visualization with animated team:
```bash
python simple_demo.py
```

This opens a large, beautifully designed pygame window showing:
- **Left Panel:** Animated team network with live status updates
- **Right Panel:** Scrollable text output with all system messages
- **Interactive Controls:** Mouse and keyboard navigation

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
# Run the CarMax store demo
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

**Graphics Panel (Left 60%):**
- **🏪 Team Network** - Circular layout showing all CarMax team members
- **⚫ Status Indicators** - Color-coded circles showing availability/busy status
- **💫 Work Animations** - Pulsing effects when helping customers
- **✨ Completion Effects** - Animated particles when tasks are finished
- **📊 Live Stats** - Real-time task counts and performance metrics

**Text Panel (Right 40%):**
- **� System Output** - Scrollable log of all team activities
- **⏰ Timestamps** - Track when each customer interaction occurred
- **📋 Interactive Controls** - Scroll, auto-scroll, and view options
- **🎮 Keyboard Controls:** ↑↓ to scroll, Space for auto-scroll, D for details
- **Status Indicators** - Real-time visual feedback
- **Task Information** - Current task details and progress
- **Performance Stats** - Live counters and metrics

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
ollama/
├── 📄 README.md                    # Project documentation  
├── 📄 requirements.txt             # Python dependencies (pygame, requests)
├── 🐍 agent_system.py              # CarMax team classes and orchestrator
├── 🐍 unified_visualizer.py        # Real-time pygame visualization
├── 🐍 simple_demo.py               # Main CarMax store demo
└── �️ __pycache__/                 # Python cache (auto-generated)
```

## ✨ Key Features

✅ **Real-time CarMax Store Visualization** with animated team members
✅ **Specialized Team Roles** - Sales, Appraisal, Finance, Management
✅ **Live Status Updates** showing available, busy, and completed states  
✅ **Animated Effects** around active team members
✅ **Performance Monitoring** with live customer service metrics
✅ **Interactive Interface** with customer request progress
✅ **Ollama Integration** using llama3.2 model for realistic responses
✅ **Automatic Screen Sizing** - adapts to 75% of your screen resolution
✅ **Professional UI** with readable fonts and clean design

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
   - The interface automatically sizes to 75% of your screen
   - Ensure your screen resolution is at least 1024x768

### Performance Tips

- Use GPU acceleration if available with Ollama
- Adjust response length in agent system prompts
- Close other resource-intensive applications
- Use smaller model variants like `llama3.2:1b` for testing

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

## License

This is a demonstration project for educational purposes. Feel free to modify and extend for your own projects.
