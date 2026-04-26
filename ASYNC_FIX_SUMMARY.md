# Async Behavior Fix for Vision Model Operations

## Problem
The AI Pixelizer and Background Remover features were blocking the main UI thread when calling the vision model, causing PySide6 to display "Python may have hung" messages repeatedly until the operation completed.

## Solution
Implemented proper asynchronous behavior using `QThread` with signals for progress updates and results.

## Changes Made

### 1. New File: `src/pixelsmart/vision_worker.py`
Created a dedicated worker thread class that:
- Inherits from `QThread` for proper threading in PySide6
- Emits signals for state changes:
  - `started()` - when operation begins
  - `progress(str)` - progress updates (e.g., "Analyzing image...")
  - `finished(str)` - result when complete
  - `error(str)` - error messages if something fails

### 2. Modified: `src/pixelsmart/main.py`

#### Added imports:
- `QProgressDialog` for showing progress during long operations
- `VisionWorker` from the new module

#### Added instance variable:
- `self.vision_worker = VisionWorker(self)` - worker instance with parent relationship

#### Added signal connections in `__init__`:
```python
self.vision_worker.started.connect(self._on_vision_operation_started)
self.vision_worker.progress.connect(self._on_vision_progress)
self.vision_worker.finished.connect(self._on_vision_operation_finished)
self.vision_worker.error.connect(self._on_vision_operation_error)
```

#### Added handler methods:
- `_on_vision_operation_started()` - Shows a modal progress dialog
- `_on_vision_progress(message)` - Updates progress dialog and increments progress bar
- `_on_vision_operation_finished(result)` - Closes progress dialog, shows results
- `_on_vision_operation_error(error_message)` - Closes progress dialog, shows error

#### Modified methods:
- `run_ai_pixelizer()` - Now calls `self.vision_worker.run_pixelizer(image)` instead of blocking
- `run_background_remover()` - Now calls `self.vision_worker.run_background_remover(image, prompt)` instead of blocking

## How It Works

1. User clicks AI Pixelizer or Background Remover button
2. File dialog opens (non-blocking)
3. After selecting image, worker thread is started with the operation
4. Main UI thread remains responsive - no "hung" messages
5. Progress dialog shows with cancel option and auto-updating progress
6. When complete, results are displayed in a message box

## Benefits

- **No more hung warnings** - UI stays responsive during model processing
- **Progress feedback** - User sees what's happening with a modal progress dialog
- **Cancel option** - User can cancel long operations if needed
- **Proper threading** - Vision model runs in background thread, not blocking Qt event loop

## Testing

To test the fix:
1. Run the application: `python src/pixelsmart/main.py`
2. Load or create an image
3. Click "AI Pixelizer" or "Background Remover"
4. Select an image file
5. Observe that:
   - No "Python may have hung" messages appear
   - Progress dialog shows with updating messages
   - Results display when complete
   - UI remains responsive throughout
