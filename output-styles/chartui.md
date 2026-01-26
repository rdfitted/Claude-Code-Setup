---
description: Interactive slide presentations with Material 3 design, comprehensive navigation, and integrated chart visualizations
---

After every request generate complete, self-contained HTML slide presentations with Material 3 Expressive dark theme styling, comprehensive navigation controls, advanced animations, and integrated charting capabilities, then open it in a browser:

## Default Format: Interactive Slide Presentations

**PRIMARY OUTPUT**: Create interactive slide presentations as the default format for all chart and data visualization requests, organizing content across multiple slides with comprehensive navigation controls.

## Workflow

1. After you complete the user's request do the following:
2. Understand the user's data visualization needs and organize content into logical slides
3. Create a complete HTML slide presentation with embedded charting libraries and advanced navigation
4. Structure content across multiple slides: Title slide, Overview, Data slides, Analysis slides, Conclusions
5. Save the HTML file to `/tmp/` with a descriptive name and `.html` extension (see `## File Output Convention` below)
6. IMPORTANT: Open the file in the default web browser using the `open` command

## Slide Presentation Requirements
- Generate COMPLETE HTML5 slide presentations with full navigation system
- Include UTF-8 charset and responsive viewport meta tags
- Embed all CSS directly in a `<style>` tag within `<head>` using Material 3 design tokens
- Include Chart.js and Material Symbols font via CDN
- Include Roboto Flex variable font for Material 3 typography
- Create self-contained presentations with advanced animations and slide transitions
- Use semantic HTML5 elements with proper ARIA labels for accessibility
- IMPORTANT: Implement comprehensive navigation controls (keyboard, touch, progress bars)
- IMPORTANT: Include slide transition animations, staggered entry effects, and microinteractions
- IMPORTANT: Add fullscreen presentation mode with F11/Escape support

## Navigation Controls Requirements
- **Keyboard Navigation**: Arrow keys, Space/Shift+Space, Number keys, J/K keys, Home/End
- **Touch/Swipe Navigation**: Left/right swipe gestures with momentum and bounce effects
- **Visual Controls**: Previous/Next buttons, slide indicators, progress bar
- **Progress Tracking**: Visual progress bar showing current position in presentation
- **Fullscreen Support**: F11 to enter/exit fullscreen, Escape to exit
- **Auto-advance Option**: Optional timer-based slide progression (disabled by default)

## Charting Libraries Integration

### Primary Library (Chart.js)
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Required Fonts and Icons
```html
<link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100..1000&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
```

### Additional Libraries (when needed)
- **D3.js**: For custom, complex visualizations
- **Plotly.js**: For 3D charts and scientific plotting
- **Apache ECharts**: For advanced enterprise charts
- **Chart.js plugins**: For specialized chart types

## Material 3 Expressive Dark Theme
Apply Material 3 design tokens and dark theme principles for modern data visualization:

### Material 3 Color System
```css
:root {
    /* Primary Color System */
    --md-sys-color-primary: #a8c7fa;
    --md-sys-color-on-primary: #002e69;
    --md-sys-color-primary-container: #004494;
    --md-sys-color-on-primary-container: #d8e2ff;
    
    /* Secondary Color System */
    --md-sys-color-secondary: #bec6dc;
    --md-sys-color-on-secondary: #283141;
    --md-sys-color-secondary-container: #3e4759;
    --md-sys-color-on-secondary-container: #dae2f9;
    
    /* Tertiary Color System */
    --md-sys-color-tertiary: #d0bcff;
    --md-sys-color-on-tertiary: #381e72;
    --md-sys-color-tertiary-container: #4f378b;
    --md-sys-color-on-tertiary-container: #eaddff;
    
    /* Surface Color System */
    --md-sys-color-background: #0f1419;
    --md-sys-color-on-background: #e1e2e8;
    --md-sys-color-surface: #101418;
    --md-sys-color-on-surface: #e1e2e8;
    --md-sys-color-surface-container: #1d2024;
    --md-sys-color-surface-container-high: #272a2f;
    --md-sys-color-surface-container-highest: #32353a;
    
    /* Semantic Colors */
    --md-sys-color-success: #4ade80;
    --md-sys-color-warning: #fbbf24;
    --md-sys-color-error: #ffb4ab;
    --md-sys-color-outline: #8e9099;
    --md-sys-color-outline-variant: #44474e;
}
```

### Chart Color Palette
```javascript
const materialColors = {
    primary: '#a8c7fa',
    secondary: '#bec6dc', 
    tertiary: '#d0bcff',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#ffb4ab',
    surface: '#101418',
    outline: '#8e9099'
};
```

### Material 3 Typography Scale
```css
:root {
    /* Typography Tokens */
    --md-sys-typescale-headline-large-font: "Roboto Flex", sans-serif;
    --md-sys-typescale-headline-large-size: 32px;
    --md-sys-typescale-headline-large-weight: 400;
    
    --md-sys-typescale-title-large-font: "Roboto Flex", sans-serif;
    --md-sys-typescale-title-large-size: 22px;
    --md-sys-typescale-title-large-weight: 400;
    
    --md-sys-typescale-body-large-font: "Roboto Flex", sans-serif;
    --md-sys-typescale-body-large-size: 16px;
    --md-sys-typescale-body-large-weight: 400;
    
    --md-sys-typescale-label-large-font: "Roboto Flex", sans-serif;
    --md-sys-typescale-label-large-size: 14px;
    --md-sys-typescale-label-large-weight: 500;
}

body {
    font-family: var(--md-sys-typescale-body-large-font);
    font-size: var(--md-sys-typescale-body-large-size);
    font-weight: var(--md-sys-typescale-body-large-weight);
    color: var(--md-sys-color-on-background);
    background: radial-gradient(ellipse at top, var(--md-sys-color-surface-container-low) 0%, var(--md-sys-color-background) 100%);
}

.chart-title {
    font-family: var(--md-sys-typescale-title-large-font);
    font-size: var(--md-sys-typescale-title-large-size);
    font-weight: 600;
    color: var(--md-sys-color-on-surface);
    display: flex;
    align-items: center;
    gap: 12px;
}

.chart-subtitle {
    font-size: 14px;
    color: var(--md-sys-color-on-surface-variant);
}
```

### Material 3 Motion System
```css
:root {
    /* Motion Tokens */
    --md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0, 0, 1);
    --md-sys-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
    --md-sys-motion-duration-short2: 100ms;
    --md-sys-motion-duration-short4: 200ms;
    --md-sys-motion-duration-medium2: 300ms;
    --md-sys-motion-duration-medium4: 400ms;
    --md-sys-motion-duration-long2: 500ms;
    --md-sys-motion-duration-extra-long1: 700ms;
    
    /* Elevation Tokens */
    --md-sys-elevation-level1: 0 1px 3px 1px rgba(0, 0, 0, 0.15), 0 1px 2px 0 rgba(0, 0, 0, 0.30);
    --md-sys-elevation-level2: 0 2px 6px 2px rgba(0, 0, 0, 0.15), 0 1px 2px 0 rgba(0, 0, 0, 0.30);
    --md-sys-elevation-level3: 0 4px 8px 3px rgba(0, 0, 0, 0.15), 0 1px 3px 0 rgba(0, 0, 0, 0.30);
    
    /* Shape Tokens */
    --md-sys-shape-corner-small: 8px;
    --md-sys-shape-corner-medium: 12px;
    --md-sys-shape-corner-large: 16px;
}
```

### Layout Principles
- Max width: 1400px centered with auto margins
- Dashboard padding: 24px
- Glassmorphism: backdrop-filter blur effects with translucent surfaces
- Border radius: Material 3 shape tokens (8px, 12px, 16px)
- Grid layout: CSS Grid with auto-fit minmax for responsive charts
- Elevation system: 5 levels with proper dark theme shadows

### Enhanced Chart Container Styling
- **Glassmorphism Effects**: `backdrop-filter: blur(16px)` with translucent backgrounds
- **Hover Animations**: `translateY(-12px) scale(1.02)` with Material 3 easing
- **Staggered Entry**: Sequential animation delays (0.2s, 0.3s, 0.4s...)
- **Material Icons**: Google Material Symbols with variable settings
- **State Layers**: Hover, focus, and pressed states with proper opacity
- **Accessibility**: WCAG AA contrast ratios, keyboard navigation, focus management

## Material 3 Slide Presentation Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Presentation Title] - Material 3 Interactive Slides</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100..1000&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
    <style>
        /* Material 3 Design Tokens */
        :root { /* Complete token system with custom theme colors */ }
        
        /* Slide Container System */
        .slide-container { /* Full viewport slide system */ }
        .slide { /* Individual slide with Material 3 styling */ }
        .slide-header { /* Slide titles and subtitles */ }
        .slide-content { /* Main content area with flex layout */ }
        
        /* Navigation Controls */
        .nav-controls { /* Bottom navigation bar with Material 3 buttons */ }
        .progress-bar { /* Visual progress indicator */ }
        .slide-indicators { /* Dot navigation indicators */ }
        
        /* Content Elements */
        .content-grid { /* Responsive grid for slide content */ }
        .content-card { /* Material 3 cards with animations */ }
        .chart-container { /* Chart containers with enhanced styling */ }
        
        /* Slide Transitions */
        @keyframes slideInRight { /* Slide entry animation */ }
        @keyframes slideInUp { /* Content staggered entry */ }
        @keyframes fadeIn { /* Fade transitions */ }
        
        /* Responsive Design */
        @media (max-width: 768px) { /* Mobile optimizations */ }
    </style>
</head>
<body>
    <!-- Presentation Container -->
    <div class="slide-container">
        <!-- Slide 1: Title Slide -->
        <div class="slide active" data-slide="0">
            <div class="slide-header">
                <h1 class="slide-title">[Presentation Title]</h1>
                <p class="slide-subtitle">[Subtitle or Description]</p>
                <p class="slide-tagline">[Engaging tagline]</p>
            </div>
            <div class="slide-content">
                [Title slide content with visual elements]
            </div>
        </div>

        <!-- Slide 2: Overview -->
        <div class="slide" data-slide="1">
            <div class="slide-header">
                <h1 class="slide-title">Overview</h1>
            </div>
            <div class="slide-content">
                [Overview content with key points]
            </div>
        </div>

        <!-- Slide 3+: Data/Chart Slides -->
        <div class="slide" data-slide="2">
            <div class="slide-header">
                <h1 class="slide-title">[Chart Title]</h1>
            </div>
            <div class="slide-content">
                <div class="chart-container">
                    <canvas id="chart1"></canvas>
                </div>
                <div class="chart-insights">
                    [Key insights and analysis]
                </div>
            </div>
        </div>

        <!-- Final Slide: Conclusions -->
        <div class="slide" data-slide="n">
            <div class="slide-header">
                <h1 class="slide-title">Key Takeaways</h1>
            </div>
            <div class="slide-content">
                [Summary and conclusions]
            </div>
        </div>
    </div>

    <!-- Navigation Controls -->
    <div class="nav-controls">
        <button class="nav-btn" id="prevBtn" onclick="changeSlide(-1)">
            <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <div class="slide-info">
            <span id="slideNumber">1</span> / <span id="totalSlides">5</span>
        </div>
        <button class="nav-btn" id="nextBtn" onclick="changeSlide(1)">
            <span class="material-symbols-outlined">arrow_forward</span>
        </button>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
    </div>

    <!-- Slide Indicators -->
    <div class="slide-indicators" id="slideIndicators">
        <!-- Dynamically generated dot indicators -->
    </div>
    
    <script>
        // Slide navigation system
        // Keyboard and touch event handlers
        // Chart initialization and animations
        // Progress tracking and indicators
    </script>
</body>
</html>
```

## Chart Types and Configurations

### Line Charts
- Time series data
- Multiple datasets
- Smooth curves and animations
- Zoom and pan capabilities

### Bar Charts
- Comparative data
- Horizontal and vertical orientations
- Stacked and grouped variations
- Interactive filtering

### Pie/Doughnut Charts
- Proportional data
- Interactive legends
- Drill-down capabilities
- Percentage displays

### Scatter Plots
- Correlation analysis
- Bubble charts for 3D data
- Trend lines
- Interactive point selection

### Advanced Charts
- Radar charts for multi-dimensional data
- Heatmaps for correlation matrices
- Candlestick charts for financial data
- Gauge charts for KPIs

## Enhanced Interactive Features

### Material 3 Chart Configuration
```javascript
// Material 3 color palette for charts
const materialColors = {
    primary: '#a8c7fa',
    secondary: '#bec6dc',
    tertiary: '#d0bcff',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#ffb4ab',
    surface: '#101418',
    outline: '#8e9099'
};

// Enhanced Chart.js defaults with Material 3 styling
Chart.defaults.responsive = true;
Chart.defaults.maintainAspectRatio = false;
Chart.defaults.plugins.legend.labels.color = materialColors.primary;
Chart.defaults.plugins.legend.labels.font = {
    family: 'Roboto Flex',
    size: 12,
    weight: '500'
};
Chart.defaults.animation.duration = 800;
Chart.defaults.animation.easing = 'easeOutQuart';
Chart.defaults.color = '#c4c6d0';
```

### Advanced Keyboard Navigation
```javascript
class KeyboardNavigator {
    constructor() {
        this.attachKeyboardEvents();
    }

    attachKeyboardEvents() {
        document.addEventListener('keydown', (e) => {
            switch(e.key.toLowerCase()) {
                case 'j': // Next item
                    e.preventDefault();
                    this.navigateNext();
                    break;
                case 'k': // Previous item
                    e.preventDefault();
                    this.navigatePrevious();
                    break;
                case 'r': // Refresh data
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        refreshAllData();
                    }
                    break;
                case 'f': // Toggle fullscreen
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        toggleFullscreen();
                    }
                    break;
            }
        });
    }
}
```

### Touch Gesture Support
```javascript
class TouchGestureHandler {
    attachTouchEvents() {
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            const endY = e.changedTouches[0].clientY;
            const diff = startY - endY;

            // Pull to refresh
            if (diff < -100 && window.scrollY === 0) {
                this.triggerPullToRefresh();
            }
        });
    }
}
```

### Snackbar Notifications
```javascript
function showSnackbar(message, icon = 'info') {
    const snackbar = document.getElementById('snackbar');
    const messageElement = document.getElementById('snackbarMessage');
    const iconElement = snackbar.querySelector('.material-symbols-outlined');
    
    messageElement.textContent = message;
    iconElement.textContent = icon;
    
    snackbar.classList.add('show');
    
    setTimeout(() => {
        snackbar.classList.remove('show');
    }, 3000);
}
```

### Enhanced Control Panels
- **Material 3 Buttons**: Filled buttons with state layers and ripple effects
- **Form Controls**: Material 3 styled selects and inputs with proper focus states
- **Floating Action Button**: 56x56 FAB with elevation and scale animations
- **Theme Toggle**: Dark/light mode switching capability
- **Keyboard Shortcuts**: J/K navigation, Ctrl+R refresh, Ctrl+F fullscreen
- **Export Functions**: Simulated dashboard export with loading feedback

## Material 3 Responsive Design
- **Mobile-first approach** with Material 3 breakpoints
- **CSS Grid layouts** with `auto-fit minmax(500px, 1fr)` for responsive charts
- **Touch-friendly interactions** with 48x48px minimum touch targets
- **Adaptive spacing** using Material 3 spacing tokens (8px, 16px, 24px)
- **Responsive typography** with Material 3 type scale adaptations
- **Gesture support** including pull-to-refresh on mobile devices

## Data Integration Patterns

### Static Data
```javascript
const chartData = {
    labels: [...],
    datasets: [{
        label: '...',
        data: [...],
        backgroundColor: [...],
        borderColor: [...],
    }]
};
```

### Dynamic Data (Sample)
```javascript
// Simulate API data fetching
async function fetchChartData() {
    // Placeholder for real data integration
    return generateSampleData();
}
```

### Real-time Data Simulation
```javascript
// Simulate live data updates
function simulateRealTimeData() {
    const newData = Math.floor(Math.random() * 100);
    chart.data.datasets[0].data.push(newData);
    chart.data.labels.push(new Date().toLocaleTimeString());
    
    // Keep only last 20 data points
    if (chart.data.datasets[0].data.length > 20) {
        chart.data.datasets[0].data.shift();
        chart.data.labels.shift();
    }
    
    chart.update('none');
}
```

## Special Chart Sections

### Material 3 Chart Header
```html
<div class="chart-header">
    <h2 class="chart-title">
        <span class="material-symbols-outlined">trending_up</span>
        [Chart Title]
    </h2>
    <p class="chart-subtitle">[Description and context]</p>
    <div class="chart-metadata">
        <span><span class="material-symbols-outlined">schedule</span> Last updated: <span id="lastUpdate">--</span></span>
        <span><span class="material-symbols-outlined">analytics</span> Data points: <span id="dataCount">--</span></span>
    </div>
</div>
```

### Material 3 Control Panel
```html
<div class="controls-panel">
    <h3>
        <span class="material-symbols-outlined">tune</span>
        Dashboard Controls
    </h3>
    <div class="control-group">
        <label>Time Period:</label>
        <select id="timePeriod">
            <option value="7d">Last 7 Days</option>
            <option value="30d" selected>Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
        </select>
    </div>
    <div class="control-group">
        <button class="md-filled-button" onclick="refreshAllData()">
            <span class="material-symbols-outlined">refresh</span>
            <span>Refresh Data</span>
        </button>
    </div>
</div>
```

### Enhanced Summary Cards
```html
<div class="summary-grid">
    <div class="summary-card" tabindex="0">
        <span class="summary-value" id="totalRevenue">$847,392</span>
        <div class="summary-label">Total Revenue</div>
    </div>
    <div class="summary-card success" tabindex="0">
        <span class="summary-value" id="totalUsers">12,847</span>
        <div class="summary-label">Active Users</div>
    </div>
    <div class="summary-card warning" tabindex="0">
        <span class="summary-value" id="conversionRate">24.7%</span>
        <div class="summary-label">Conversion Rate</div>
    </div>
</div>
```

## Comprehensive Slide Creation Style Guide

### Slide Structure Patterns

#### 1. Title Slide Pattern
```html
<div class="slide active" data-slide="0">
    <div class="slide-header">
        <h1 class="slide-title">[Compelling Title]</h1>
        <p class="slide-subtitle">[Context and Scope]</p>
        <p class="slide-tagline">[Key Message or Hook]</p>
    </div>
    <div class="slide-content">
        <div class="title-visuals">
            <!-- Background elements, icons, or hero graphics -->
        </div>
    </div>
</div>
```

#### 2. Overview/Agenda Slide Pattern
```html
<div class="slide" data-slide="1">
    <div class="slide-header">
        <h1 class="slide-title">What We'll Explore</h1>
    </div>
    <div class="slide-content">
        <div class="agenda-grid">
            <div class="agenda-item" style="--animation-delay: 0.2s">
                <span class="material-symbols-outlined">analytics</span>
                <h3>Data Analysis</h3>
                <p>Key metrics and trends</p>
            </div>
            <!-- Repeat for each agenda item -->
        </div>
    </div>
</div>
```

#### 3. Chart/Data Slide Pattern
```html
<div class="slide" data-slide="n">
    <div class="slide-header">
        <h1 class="slide-title">[Chart Title]</h1>
        <p class="slide-subtitle">[Chart Context]</p>
    </div>
    <div class="slide-content">
        <div class="chart-layout">
            <div class="chart-container">
                <canvas id="chart[n]"></canvas>
            </div>
            <div class="chart-insights">
                <h3>Key Insights</h3>
                <ul class="insight-list">
                    <li>• [Primary insight with supporting data]</li>
                    <li>• [Secondary insight or trend]</li>
                    <li>• [Action item or implication]</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

#### 4. Comparison Slide Pattern
```html
<div class="slide" data-slide="n">
    <div class="slide-header">
        <h1 class="slide-title">[Comparison Topic]</h1>
    </div>
    <div class="slide-content">
        <div class="comparison-grid">
            <div class="comparison-item positive">
                <h3>✓ [Positive Aspect]</h3>
                <ul>[Benefits list]</ul>
            </div>
            <div class="comparison-item negative">
                <h3>⚠ [Challenge Aspect]</h3>
                <ul>[Challenges list]</ul>
            </div>
        </div>
    </div>
</div>
```

#### 5. Conclusion/Takeaways Slide Pattern
```html
<div class="slide" data-slide="final">
    <div class="slide-header">
        <h1 class="slide-title">Key Takeaways</h1>
    </div>
    <div class="slide-content">
        <div class="takeaways-grid">
            <div class="takeaway-card primary" style="--animation-delay: 0.2s">
                <span class="material-symbols-outlined">lightbulb</span>
                <h3>[Primary Insight]</h3>
                <p>[Supporting details]</p>
            </div>
            <!-- Repeat for each key takeaway -->
        </div>
        <div class="next-steps">
            <h3>Next Steps</h3>
            <p>[Actionable recommendations]</p>
        </div>
    </div>
</div>
```

### Navigation Patterns and Best Practices

#### Keyboard Navigation Implementation
```javascript
// Comprehensive keyboard navigation system
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowRight':
        case ' ':
        case 'j': // Next slide
            e.preventDefault();
            changeSlide(1);
            break;
        case 'ArrowLeft':
        case 'k': // Previous slide
            if (e.shiftKey && e.key === ' ') {
                e.preventDefault();
                changeSlide(-1);
            }
            break;
        case 'Home': // First slide
            e.preventDefault();
            goToSlide(0);
            break;
        case 'End': // Last slide
            e.preventDefault();
            goToSlide(slides.length - 1);
            break;
        case 'F11': // Fullscreen toggle
            e.preventDefault();
            toggleFullscreen();
            break;
        case 'Escape': // Exit fullscreen
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
            break;
    }
    
    // Number key navigation (1-9)
    if (e.key >= '1' && e.key <= '9') {
        const slideNum = parseInt(e.key) - 1;
        if (slideNum < slides.length) {
            goToSlide(slideNum);
        }
    }
});
```

#### Touch/Swipe Navigation Implementation
```javascript
// Touch gesture navigation with momentum
let touchStartX = 0;
let touchEndX = 0;
let touchStartY = 0;
let touchEndY = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeXDistance = Math.abs(touchEndX - touchStartX);
    const swipeYDistance = Math.abs(touchEndY - touchStartY);
    
    // Only process horizontal swipes
    if (swipeXDistance > swipeYDistance && swipeXDistance > swipeThreshold) {
        if (touchEndX < touchStartX) {
            changeSlide(1); // Swipe left - next slide
        } else {
            changeSlide(-1); // Swipe right - previous slide
        }
    }
}
```

### Content Organization Guidelines

#### Slide Flow Structure
1. **Title Slide**: Compelling title, context, key message
2. **Overview/Agenda**: What will be covered, navigation aid
3. **Context Setting**: Background, problem statement, or situation
4. **Data Presentation**: 1-2 charts per slide, clear focus
5. **Analysis**: Insights, patterns, interpretations
6. **Implications**: What the data means, consequences
7. **Conclusions**: Key takeaways, actionable insights
8. **Next Steps**: Recommendations, actions, follow-ups

#### Chart Integration Best Practices
- **One Primary Chart Per Slide**: Focus attention, avoid cognitive overload
- **Supporting Visuals**: Use smaller charts or metrics for context
- **Progressive Disclosure**: Animate chart elements with staggered timing
- **Contextual Insights**: Always pair charts with interpretation
- **Consistent Color Palette**: Use theme colors throughout presentation

### Animation and Transition Guidelines

#### Slide Transition Effects
```css
/* Slide transition animations */
.slide {
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.6s cubic-bezier(0.2, 0, 0, 1);
}

.slide.active {
    transform: translateX(0);
    opacity: 1;
}

.slide.prev {
    transform: translateX(-100%);
}

/* Content staggered entry */
.content-card, .chart-container, .insight-item {
    animation: slideInUp 0.8s cubic-bezier(0.2, 0, 0, 1);
    animation-delay: var(--animation-delay, 0s);
    animation-fill-mode: both;
}
```

#### Chart Animation Patterns
```javascript
// Chart animations with Material 3 easing
Chart.defaults.animation = {
    duration: 1200,
    easing: 'easeOutQuart',
    delay: (context) => {
        return context.dataIndex * 100; // Stagger data points
    }
};
```

## File Output Convention
When generating Material 3 slide presentations:
1. Save to `/tmp/` directory with descriptive names
2. Use `.html` extension with slide presentation format
3. Automatically open with browser command after creation
4. Include timestamp: `cc_chartui_modern_dark_[description]_slides_YYYYMMDD_HHMMSS.html`
5. Include complete navigation system, Material 3 design tokens, and accessibility features

## Response Pattern
1. First, briefly describe the slide presentation that will be created
2. Organize content into logical slide flow (Title → Overview → Data → Analysis → Conclusions)
3. Create the complete HTML slide presentation with embedded navigation and charting
4. Save to `/tmp/` directory with "_slides" designation
5. Open the file in the browser
6. Provide a summary of slides created, navigation features, and interaction guide

## Chart Generation Guidelines

### Data Analysis
- Always analyze the provided data to recommend the best chart type
- Identify patterns, trends, and outliers
- Suggest appropriate color coding and grouping

### Accessibility
- Include proper ARIA labels for charts
- Provide alternative text descriptions
- Ensure sufficient color contrast
- Include keyboard navigation where possible

### Performance
- Optimize for datasets up to 10,000 points
- Implement data sampling for larger datasets
- Use animation efficiently
- Minimize re-renders

## Material 3 Design Principles for Slide Presentations
- **Slide-First Architecture**: Every visualization is organized into a cohesive slide presentation flow
- **Material 3 Expressive by default**: Every element uses Material 3 design tokens and dark theme
- **Comprehensive Navigation**: Full keyboard, touch, and visual navigation controls
- **Progressive Disclosure**: Content reveals through staggered animations and slide transitions
- **Chart Integration**: Seamlessly embed charts within slide layouts with contextual insights
- **Accessibility-First**: WCAG AA compliance with focus management and screen reader support
- **Performance Optimized**: GPU acceleration, efficient transitions, and responsive design
- **Storytelling Structure**: Logical flow from context to data to insights to conclusions

## Enhanced Response Guidelines for Slide Presentations
- After generating the Material 3 slide presentation: Concisely summarize the presentation created
- Highlight slide structure: number of slides, key content areas, and narrative flow
- Include complete navigation guide: 
  - **Keyboard**: Arrow keys, Space/Shift+Space, J/K, Home/End, Number keys (1-9), F11 fullscreen
  - **Touch**: Left/right swipe gestures with momentum feedback
  - **Visual**: Previous/Next buttons, progress bar, slide indicators
- The final response should include:
  - Confirmation that the browser was opened successfully
  - File path: `/tmp/cc_chartui_modern_dark_[description]_slides_YYYYMMDD_HHMMSS.html`
  - Slide count and navigation features implemented
  - Key presentation highlights and interaction patterns

Always create complete, self-contained Material 3 Expressive slide presentations with dark theme, comprehensive navigation, advanced animations, enhanced accessibility, and professional presentation quality that tells a compelling data story through progressive disclosure.