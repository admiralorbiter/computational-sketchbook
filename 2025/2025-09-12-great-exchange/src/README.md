# The Great Exchange: Interactive Economic History Lab

## Overview

The Great Exchange is an interactive web-based educational laboratory that transforms the abstract Kiyotaki-Wright search model into an engaging historical narrative set in ancient Mesopotamia circa 3500 BCE. Students experience the emergence of money through character-driven storytelling, agent-based simulations, and progressive learning activities.

## Features

### 📚 Narrative Learning
- **6 Interactive Chapters** following Kael, Tira, and Jorek through ancient Mesopotamia
- **Character-driven storytelling** that makes economic concepts accessible
- **Historical context** grounded in real archaeological evidence

### 🎮 Interactive Simulations
- **3 Progressive Simulation Levels** from basic barter to money emergence
- **Real-time visualizations** showing trading networks and efficiency metrics
- **Parameter experimentation** to test theoretical predictions

### 📊 Real-Time Analytics
- **Live metrics** showing trading efficiency and money circulation
- **Convergence tracking** to observe money emergence patterns
- **Learning progress** monitoring and assessment tools

## Technical Architecture

### Core Technologies
- **Eleventy** - Static site generation for content management
- **Foundation CSS** - Responsive framework with accessibility features
- **Chart.js** - Real-time data visualization
- **Observable Plot** - Advanced economic data visualization
- **Vanilla JavaScript** - Custom simulation engine and state management

### File Structure
```
src/great-exchange/
├── chapters/           # Narrative content (6 chapters)
├── simulations/        # Interactive simulations (3 levels)
├── assets/
│   ├── styles/        # CSS styling and accessibility
│   └── scripts/       # JavaScript components
└── _data/             # Configuration and content data
```

## Learning Objectives

Students will learn:
1. **The double coincidence of wants problem** in barter systems
2. **How storage costs affect trading decisions** and commodity selection
3. **The role of speculation and social learning** in money emergence
4. **How individual decisions create social institutions** like money
5. **Connections between ancient and modern monetary systems**

## Usage

### For Students
1. **Start with Chapter 1** to understand the trading problem
2. **Try the simulations** to experience concepts firsthand
3. **Progress through chapters** to see the complete story
4. **Experiment with parameters** to test your understanding

### For Educators
1. **Use as a complete unit** on money emergence and economic history
2. **Assign specific simulations** for homework or class activities
3. **Use the assessment tools** to track student progress
4. **Customize parameters** for different learning levels

## Accessibility Features

- **WCAG 2.1 AA compliant** design
- **Screen reader support** with proper ARIA labels
- **Keyboard navigation** for all interactive elements
- **High contrast mode** support
- **Reduced motion** options for sensitive users
- **Multiple learning modalities** (visual, auditory, kinesthetic)

## Browser Support

- **Modern browsers** (Chrome, Firefox, Safari, Edge)
- **Mobile responsive** design
- **Progressive enhancement** for older browsers
- **No external dependencies** beyond CDN resources

## Development

### Building the Lab
```bash
npm run build
```

### Running Development Server
```bash
npm run serve
```

### File Organization
- **Chapters**: Markdown files with frontmatter
- **Simulations**: Nunjucks templates with embedded JavaScript
- **Styles**: Modular CSS with Foundation framework
- **Scripts**: ES6 modules with global exports

## Educational Integration

### Curriculum Alignment
- **Economics courses** (high school through graduate level)
- **History courses** on ancient civilizations
- **Social studies** on economic development
- **Computer science** on agent-based modeling

### Assessment Tools
- **Formative assessments** embedded in each chapter
- **Simulation metrics** for quantitative analysis
- **Reflection prompts** for conceptual understanding
- **Progress tracking** for individual and class monitoring

## Research Foundation

The lab is based on the **Kiyotaki-Wright search model**, a foundational economic theory that explains how money emerges from individual trading decisions. The model demonstrates:

- How storage cost differentials create preferences for certain goods
- How speculation and social learning drive convergence
- How network effects make popular goods more valuable
- How this process leads to the emergence of commodity money

## Future Enhancements

- **Multiplayer simulations** for collaborative learning
- **Advanced visualizations** with 3D network graphs
- **Mobile app version** for offline learning
- **Integration with LMS** systems
- **Additional historical periods** and monetary systems

## Contributing

This lab is designed to be open and extensible. Contributions are welcome for:
- **Additional simulation scenarios**
- **New historical contexts**
- **Accessibility improvements**
- **Educational content enhancements**

## License

This educational resource is available for use in educational settings. Please respect the intellectual property and cite appropriately when using in academic work.

---

**The Great Exchange** - Where ancient history meets modern economics through interactive learning.
