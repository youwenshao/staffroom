class DiagramTool {
    constructor() {
        this.canvas = null;
        this.currentTool = null;
        this.gridSize = 20;
        this.showGrid = true;
        this.zoomLevel = 1;
        
        this.init();
    }

    init() {
        this.setupCanvas();
        this.bindEvents();
        this.drawGrid();
    }

    setupCanvas() {
        this.canvas = new fabric.Canvas('diagramCanvas', {
            width: 800,
            height: 600,
            selection: true,
            preserveObjectStacking: true
        });

        // Enable resizing and rotation for all objects
        this.canvas.on('object:selected', (e) => {
            this.showProperties(e.target);
        });

        this.canvas.on('selection:cleared', () => {
            this.hideProperties();
        });
    }

    bindEvents() {
        // Tool selection
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setCurrentTool(e.currentTarget.dataset.type);
            });
        });

        // Canvas click for adding objects
        this.canvas.on('mouse:down', (e) => {
            if (this.currentTool && !e.target) {
                this.addObject(e.pointer.x, e.pointer.y);
            }
        });

        // Action buttons
        document.getElementById('clearCanvas').addEventListener('click', () => this.clearCanvas());
        document.getElementById('downloadPNG').addEventListener('click', () => this.downloadPNG());
        document.getElementById('backToForm').addEventListener('click', () => window.history.back());

        // Canvas controls
        document.getElementById('toggleGrid').addEventListener('click', () => this.toggleGrid());
        document.getElementById('zoomIn').addEventListener('click', () => this.zoom(0.1));
        document.getElementById('zoomOut').addEventListener('click', () => this.zoom(-0.1));
        document.getElementById('resetZoom').addEventListener('click', () => this.resetZoom());
    }

    setCurrentTool(toolType) {
        this.currentTool = toolType;
        
        // Update UI
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-type="${toolType}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Clear selection when switching tools
        this.canvas.discardActiveObject();
        this.canvas.requestRenderAll();
    }

    addObject(x, y) {
        let newObject;
        
        switch(this.currentTool) {
            case 'teacher':
                newObject = this.createTeacher(x, y);
                break;
            case 'student':
                newObject = this.createStudent(x, y);
                break;
            case 'facing-arrow':
                newObject = this.createFacingArrow(x, y);
                break;
            case 'movement-arrow':
                newObject = this.createMovementArrow(x, y);
                break;
            case 'area':
                newObject = this.createArea(x, y);
                break;
            case 'obstacle':
                newObject = this.createObstacle(x, y);
                break;
            case 'equipment':
                newObject = this.createEquipment(x, y);
                break;
        }

        if (newObject) {
            this.canvas.add(newObject);
            this.canvas.setActiveObject(newObject);
            this.canvas.requestRenderAll();
        }
    }

    createTeacher(x, y) {
        const group = new fabric.Group([], {
            left: x,
            top: y,
            hasControls: true,
            hasBorders: true,
            lockScalingFlip: true
        });

        // Outer circle
        const circle = new fabric.Circle({
            radius: 20,
            fill: 'transparent',
            stroke: 'blue',
            strokeWidth: 3,
            originX: 'center',
            originY: 'center'
        });

        // Smiley face
        const smile = new fabric.Path('M -10 5 Q 0 15 10 5', {
            fill: 'transparent',
            stroke: 'blue',
            strokeWidth: 2,
            originX: 'center',
            originY: 'center'
        });

        const leftEye = new fabric.Circle({
            radius: 2,
            left: -6,
            top: -5,
            fill: 'blue',
            originX: 'center',
            originY: 'center'
        });

        const rightEye = new fabric.Circle({
            radius: 2,
            left: 6,
            top: -5,
            fill: 'blue',
            originX: 'center',
            originY: 'center'
        });

        group.addWithUpdate(circle, smile, leftEye, rightEye);
        return group;
    }

    createStudent(x, y) {
        return new fabric.Circle({
            left: x,
            top: y,
            radius: 15,
            fill: 'transparent',
            stroke: 'black',
            strokeWidth: 2,
            originX: 'center',
            originY: 'center',
            hasControls: true,
            hasBorders: true
        });
    }

    createFacingArrow(x, y) {
        const line = new fabric.Line([x, y, x + 50, y], {
            stroke: 'black',
            strokeWidth: 3,
            fill: 'black',
            strokeLineCap: 'round',
            hasControls: true,
            hasBorders: true
        });

        // Add arrowhead
        const arrowHead = new fabric.Triangle({
            left: x + 50,
            top: y,
            width: 10,
            height: 10,
            fill: 'black',
            angle: 0,
            originX: 'center',
            originY: 'center'
        });

        const group = new fabric.Group([line, arrowHead], {
            hasControls: true,
            hasBorders: true
        });

        return group;
    }

    createMovementArrow(x, y) {
        const line = new fabric.Line([x, y, x + 50, y], {
            stroke: 'black',
            strokeWidth: 2,
            strokeDashArray: [5, 5],
            fill: 'black',
            strokeLineCap: 'round',
            hasControls: true,
            hasBorders: true
        });

        // Add arrowhead
        const arrowHead = new fabric.Triangle({
            left: x + 50,
            top: y,
            width: 8,
            height: 8,
            fill: 'black',
            angle: 0,
            originX: 'center',
            originY: 'center'
        });

        const group = new fabric.Group([line, arrowHead], {
            hasControls: true,
            hasBorders: true
        });

        return group;
    }

    createArea(x, y) {
        return new fabric.Rect({
            left: x,
            top: y,
            width: 100,
            height: 60,
            fill: 'transparent',
            stroke: '#666',
            strokeWidth: 1,
            strokeDashArray: [5, 5],
            hasControls: true,
            hasBorders: true,
            lockUniScaling: false
        });
    }

    createObstacle(x, y) {
        return new fabric.Triangle({
            left: x,
            top: y,
            width: 30,
            height: 30,
            fill: 'transparent',
            stroke: '#666',
            strokeWidth: 2,
            hasControls: true,
            hasBorders: true,
            originX: 'center',
            originY: 'center'
        });
    }

    createEquipment(x, y) {
        // Create diamond shape by rotating a square
        const rect = new fabric.Rect({
            width: 25,
            height: 25,
            fill: 'transparent',
            stroke: '#666',
            strokeWidth: 2,
            originX: 'center',
            originY: 'center'
        });

        const group = new fabric.Group([rect], {
            left: x,
            top: y,
            angle: 45,
            hasControls: true,
            hasBorders: true
        });

        return group;
    }

    drawGrid() {
        if (!this.showGrid) return;

        const gridGroup = new fabric.Group([], {
            selectable: false,
            evented: false,
            excludeFromExport: true
        });

        const width = this.canvas.getWidth();
        const height = this.canvas.getHeight();

        // Vertical lines
        for (let x = 0; x <= width; x += this.gridSize) {
            const line = new fabric.Line([x, 0, x, height], {
                stroke: '#e0e0e0',
                strokeWidth: 1,
                selectable: false,
                evented: false
            });
            gridGroup.addWithUpdate(line);
        }

        // Horizontal lines
        for (let y = 0; y <= height; y += this.gridSize) {
            const line = new fabric.Line([0, y, width, y], {
                stroke: '#e0e0e0',
                strokeWidth: 1,
                selectable: false,
                evented: false
            });
            gridGroup.addWithUpdate(line);
        }

        this.canvas.add(gridGroup);
        this.canvas.sendToBack(gridGroup);
    }

    toggleGrid() {
        this.showGrid = !this.showGrid;
        this.canvas.getObjects().forEach(obj => {
            if (obj.excludeFromExport) {
                this.canvas.remove(obj);
            }
        });
        
        if (this.showGrid) {
            this.drawGrid();
        }
        this.canvas.requestRenderAll();
    }

    zoom(delta) {
        this.zoomLevel += delta;
        this.zoomLevel = Math.max(0.1, Math.min(3, this.zoomLevel)); // Clamp between 0.1 and 3
        
        this.canvas.setZoom(this.zoomLevel);
        this.canvas.requestRenderAll();
    }

    resetZoom() {
        this.zoomLevel = 1;
        this.canvas.setZoom(1);
        this.canvas.requestRenderAll();
    }

    downloadPNG() {
        // Temporarily hide grid for export
        const gridObjects = this.canvas.getObjects().filter(obj => obj.excludeFromExport);
        gridObjects.forEach(obj => obj.visible = false);

        const dataURL = this.canvas.toDataURL({
            format: 'png',
            quality: 1,
            multiplier: 2 // Higher resolution for download
        });

        // Restore grid visibility
        gridObjects.forEach(obj => obj.visible = true);
        this.canvas.requestRenderAll();

        const link = document.createElement('a');
        link.download = `class-diagram-${new Date().getTime()}.png`;
        link.href = dataURL;
        link.click();
    }

    clearCanvas() {
        if (confirm('Are you sure you want to clear the canvas? This cannot be undone.')) {
            const objects = this.canvas.getObjects().filter(obj => !obj.excludeFromExport);
            objects.forEach(obj => this.canvas.remove(obj));
            this.canvas.requestRenderAll();
        }
    }

    showProperties(object) {
        const panel = document.getElementById('propertiesPanel');
        panel.innerHTML = '';

        if (!object) return;

        const type = this.getObjectType(object);
        const properties = document.createElement('div');
        
        properties.innerHTML = `
            <h6>${type} Properties</h6>
            <div class="form-group">
                <label>Color:</label>
                <input type="color" id="objectColor" value="${this.getObjectColor(object)}" class="form-control form-control-sm">
            </div>
            ${type === 'Area' ? `
            <div class="form-group">
                <label>Width:</label>
                <input type="number" id="objectWidth" value="${Math.round(object.width * object.scaleX)}" class="form-control form-control-sm">
            </div>
            <div class="form-group">
                <label>Height:</label>
                <input type="number" id="objectHeight" value="${Math.round(object.height * object.scaleY)}" class="form-control form-control-sm">
            </div>
            ` : ''}
            <button id="deleteObject" class="btn btn-danger btn-sm btn-block">Delete</button>
        `;

        panel.appendChild(properties);

        // Bind property change events
        document.getElementById('objectColor').addEventListener('change', (e) => {
            this.updateObjectColor(object, e.target.value);
        });

        if (type === 'Area') {
            document.getElementById('objectWidth').addEventListener('change', (e) => {
                this.updateObjectSize(object, 'width', parseInt(e.target.value));
            });
            document.getElementById('objectHeight').addEventListener('change', (e) => {
                this.updateObjectSize(object, 'height', parseInt(e.target.value));
            });
        }

        document.getElementById('deleteObject').addEventListener('click', () => {
            this.canvas.remove(object);
            this.canvas.requestRenderAll();
            this.hideProperties();
        });
    }

    hideProperties() {
        const panel = document.getElementById('propertiesPanel');
        panel.innerHTML = '<p class="text-muted">Select an object to edit properties</p>';
    }

    getObjectType(object) {
        if (object instanceof fabric.Circle) return 'Student';
        if (object instanceof fabric.Group) {
            if (object._objects.some(obj => obj.stroke === 'blue')) return 'Teacher';
            if (object._objects.some(obj => obj.strokeDashArray)) return 'Movement Arrow';
            return 'Facing Arrow';
        }
        if (object instanceof fabric.Rect) return 'Area';
        if (object instanceof fabric.Triangle) return 'Obstacle';
        return 'Equipment';
    }

    getObjectColor(object) {
        if (object.stroke) return object.stroke;
        if (object._objects && object._objects[0].stroke) return object._objects[0].stroke;
        return '#000000';
    }

    updateObjectColor(object, color) {
        if (object instanceof fabric.Group) {
            object._objects.forEach(obj => {
                if (obj.stroke) obj.set('stroke', color);
                if (obj.fill && obj.fill !== 'transparent') obj.set('fill', color);
            });
        } else {
            if (object.stroke) object.set('stroke', color);
        }
        this.canvas.requestRenderAll();
    }

    updateObjectSize(object, dimension, value) {
        if (dimension === 'width') {
            object.set('scaleX', value / object.width);
        } else {
            object.set('scaleY', value / object.height);
        }
        this.canvas.requestRenderAll();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new DiagramTool();
});

class DiagramTool {
    constructor() {
        console.log('DiagramTool constructor called');
        this.canvas = null;
        this.currentTool = null;
        this.gridSize = 20;
        this.showGrid = true;
        this.zoomLevel = 1;
        
        this.init();
    }

    init() {
        console.log('Initializing DiagramTool...');
        console.log('Fabric loaded:', typeof fabric !== 'undefined');
        console.log('Canvas element:', document.getElementById('diagramCanvas'));
        
        this.setupCanvas();
        this.bindEvents();
        this.drawGrid();
        console.log('DiagramTool initialization complete');
    }

    setupCanvas() {
        console.log('Setting up canvas...');
        const canvasEl = document.getElementById('diagramCanvas');
        if (!canvasEl) {
            console.error('Canvas element not found!');
            return;
        }

        try {
            this.canvas = new fabric.Canvas('diagramCanvas', {
                width: 800,
                height: 600,
                selection: true,
                preserveObjectStacking: true
            });
            console.log('Canvas created successfully:', this.canvas);
        } catch (error) {
            console.error('Error creating canvas:', error);
        }

        // Enable resizing and rotation for all objects
        this.canvas.on('object:selected', (e) => {
            this.showProperties(e.target);
        });

        this.canvas.on('selection:cleared', () => {
            this.hideProperties();
        });
    }
    // ... rest of the code remains the same
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing DiagramTool...');
    new DiagramTool();
});