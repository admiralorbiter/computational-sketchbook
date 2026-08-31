export class CameraControls {
    constructor(camera, domElement) {
        this.camera = camera;
        this.domElement = domElement;
        
        // Movement settings
        this.moveSpeed = 0.1;
        this.runMultiplier = 2.0;
        this.jumpHeight = 1.0;
        
        // Physics and collision
        this.gravity = 0.01;
        this.playerHeight = 1.7;
        this.isJumping = false;
        this.verticalVelocity = 0;
        
        // Keyboard state
        this.keys = {
            forward: false,
            backward: false,
            left: false,
            right: false,
            run: false,
            jump: false
        };
        
        // Mouse look properties
        this.mouseSensitivity = 0.002;
        this.pitchObject = new THREE.Object3D(); // Vertical rotation
        this.yawObject = new THREE.Object3D();   // Horizontal rotation
        this.yawObject.add(this.pitchObject);
        this.pitchObject.add(this.camera);
        
        // Lock vertical look angle
        this.pitchMin = -Math.PI / 2 + 0.1; // Slightly less than looking straight up
        this.pitchMax = Math.PI / 2 - 0.1;  // Slightly less than looking straight down
        
        // Pointer lock variables
        this.isLocked = false;
        
        // Set up event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Click to lock pointer
        this.domElement.addEventListener('click', () => {
            if (!this.isLocked) {
                this.domElement.requestPointerLock();
            }
        });
        
        // Pointer lock change event
        document.addEventListener('pointerlockchange', () => {
            this.isLocked = document.pointerLockElement === this.domElement;
            console.log('Pointer lock changed. Is locked:', this.isLocked);
        });
        
        // Mouse movement event
        document.addEventListener('mousemove', (event) => {
            if (this.isLocked) {
                const movementX = event.movementX || 0;
                const movementY = event.movementY || 0;
                
                this.yawObject.rotation.y -= movementX * this.mouseSensitivity;
                this.pitchObject.rotation.x -= movementY * this.mouseSensitivity;
                
                // Clamp vertical look angle
                this.pitchObject.rotation.x = Math.max(
                    this.pitchMin,
                    Math.min(this.pitchMax, this.pitchObject.rotation.x)
                );
            }
        });
        
        // Keyboard events
        document.addEventListener('keydown', (event) => {
            this.updateKeyState(event, true);
        });
        
        document.addEventListener('keyup', (event) => {
            this.updateKeyState(event, false);
        });
    }
    
    updateKeyState(event, isPressed) {
        switch(event.code) {
            case 'KeyW':
            case 'ArrowUp':
                this.keys.forward = isPressed;
                break;
            case 'KeyS':
            case 'ArrowDown':
                this.keys.backward = isPressed;
                break;
            case 'KeyA':
            case 'ArrowLeft':
                this.keys.left = isPressed;
                break;
            case 'KeyD':
            case 'ArrowRight':
                this.keys.right = isPressed;
                break;
            case 'ShiftLeft':
            case 'ShiftRight':
                this.keys.run = isPressed;
                break;
            case 'Space':
                this.keys.jump = isPressed;
                
                // Start jump if not already jumping
                if (isPressed && !this.isJumping) {
                    this.isJumping = true;
                    this.verticalVelocity = this.jumpHeight;
                }
                break;
        }
    }
    
    update() {
        if (!this.isLocked) return;
        
        // Calculate movement speed based on run state
        const speed = this.keys.run 
            ? this.moveSpeed * this.runMultiplier 
            : this.moveSpeed;
        
        // Get camera direction for movement
        const direction = new THREE.Vector3();
        const rotation = this.yawObject.rotation.y;
        
        // Handle forward/backward movement
        if (this.keys.forward) {
            direction.z = -1;
        } else if (this.keys.backward) {
            direction.z = 1;
        }
        
        // Handle left/right movement
        if (this.keys.left) {
            direction.x = -1;
        } else if (this.keys.right) {
            direction.x = 1;
        }
        
        // Normalize direction if moving diagonally
        if (direction.length() > 0) {
            direction.normalize();
        }
        
        // Rotate direction by camera yaw
        direction.applyAxisAngle(new THREE.Vector3(0, 1, 0), rotation);
        
        // Apply movement
        this.yawObject.position.x += direction.x * speed;
        this.yawObject.position.z += direction.z * speed;
        
        // Apply gravity and jumping
        if (this.isJumping) {
            this.yawObject.position.y += this.verticalVelocity;
            this.verticalVelocity -= this.gravity;
            
            // Check if landed
            if (this.yawObject.position.y <= this.playerHeight) {
                this.yawObject.position.y = this.playerHeight;
                this.isJumping = false;
                this.verticalVelocity = 0;
            }
        }
    }
    
    getPosition() {
        return this.yawObject.position;
    }
    
    getDirection() {
        const direction = new THREE.Vector3(0, 0, -1);
        direction.applyQuaternion(this.pitchObject.quaternion);
        direction.applyQuaternion(this.yawObject.quaternion);
        return direction;
    }
    
    updateAspect(aspect) {
        this.camera.aspect = aspect;
        this.camera.updateProjectionMatrix();
    }
    
    // Set camera position directly (e.g., for teleporting)
    setPosition(position) {
        this.yawObject.position.copy(position);
    }
    
    // Set camera rotation (e.g., for looking at a specific target)
    setRotation(yaw, pitch) {
        this.yawObject.rotation.y = yaw;
        this.pitchObject.rotation.x = Math.max(
            this.pitchMin,
            Math.min(this.pitchMax, pitch)
        );
    }
}