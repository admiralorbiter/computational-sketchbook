virtual-museum/
├── index.html                # Main HTML entry point
├── styles.css                # Global CSS styles
├── src/
│   ├── app.js                # Main application entry point
│   ├── core/
│   │   ├── SceneManager.js   # Manages the Three.js scene
│   │   ├── Renderer.js       # Handles rendering
│   │   ├── CameraControls.js # Camera and navigation controls
│   │   └── Lighting.js       # Scene lighting setup
│   ├── procedural/
│   │   ├── RoomGenerator.js  # Procedural room generation
│   │   ├── HallwayGenerator.js # Procedural hallway generation
│   │   ├── MuseumLayout.js   # Overall museum layout logic
│   │   └── ArchitecturalStyles.js # Visual style definitions
│   ├── data/
│   │   ├── ImageSource.js    # Image fetching and management
│   │   ├── ThemeStyles.js    # Theme definitions
│   │   └── MetadataManager.js # Image metadata management
│   └── ui/
│       ├── InfoPanel.js      # Image information panel
│       ├── HUD.js            # Heads-up display
│       └── UserInterface.js  # UI manager
└── images/                   # Local image storage
    ├── placeholders/         # Placeholder images 
    └── textures/             # Texture assets