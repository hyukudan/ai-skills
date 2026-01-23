---
name: mobile-performance
description: |
  Mobile app performance optimization for iOS and Android. Covers startup time,
  app size, memory management, battery optimization, network efficiency, and
  rendering performance.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [mobile, performance, ios, android, optimization]
category: mobile/performance
trigger_phrases:
  - "mobile performance"
  - "app startup"
  - "app size"
  - "battery drain"
  - "mobile memory"
  - "jank"
  - "frame rate"
  - "ANR"
variables:
  platform:
    type: string
    description: Target platform
    enum: [ios, android, cross-platform]
    default: cross-platform
---

# Mobile Performance Guide

## Core Philosophy

**Performance is a feature.** Users will abandon slow apps - 53% leave if load time exceeds 3 seconds.

> "The fastest code is code that doesn't run."

---

## Performance Metrics

### Key Metrics to Track

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **Cold Start** | < 2s | First impression |
| **Warm Start** | < 1s | Returning users |
| **App Size** | < 100MB | Download friction |
| **Frame Rate** | 60 FPS | Smooth scrolling |
| **Memory** | < 150MB | Avoid OOM crashes |
| **Battery** | < 5%/hr active | User trust |

### Measurement Tools

{% if platform == "ios" %}
**iOS:**
- Instruments (Time Profiler, Allocations, Energy Log)
- Xcode Metrics Organizer
- MetricKit for production data
{% endif %}

{% if platform == "android" %}
**Android:**
- Android Studio Profiler (CPU, Memory, Network, Energy)
- Systrace / Perfetto
- Firebase Performance Monitoring
{% endif %}

{% if platform == "cross-platform" %}
**Cross-Platform:**
- Flipper (React Native)
- Firebase Performance Monitoring
- Platform-specific profilers for deep dives
{% endif %}

---

## 1. App Startup Optimization

### Startup Phases

```
COLD START
┌─────────────────────────────────────────────────────────┐
│ Process Creation → App Init → First Frame → Interactive │
└─────────────────────────────────────────────────────────┘
         ~200ms         ~500ms       ~300ms       ~500ms

WARM START (process alive, activity recreated)
┌─────────────────────────────────────────────────────────┐
│ Activity Creation → First Frame → Interactive           │
└─────────────────────────────────────────────────────────┘
              ~300ms          ~200ms       ~300ms

HOT START (activity in background)
┌─────────────────────────────────────────────────────────┐
│ Resume Activity → First Frame                           │
└─────────────────────────────────────────────────────────┘
         ~100ms           ~100ms
```

### Optimization Strategies

```
1. DEFER NON-CRITICAL WORK
   - Analytics initialization
   - Background sync
   - Prefetching
   - Third-party SDK init

2. LAZY LOAD
   - Load features on demand
   - Defer image loading below fold
   - Lazy initialize heavy objects

3. OPTIMIZE CRITICAL PATH
   - Minimize main thread work
   - Reduce layout complexity
   - Use cached data for first render
```

{% if platform == "android" %}
### Android Startup

```kotlin
// Use App Startup library for controlled initialization
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.init(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList() // No dependencies
    }
}

// Defer initialization until needed
class MyApplication : Application() {
    // BAD: Initialize everything at startup
    // override fun onCreate() {
    //     Analytics.init(this)
    //     CrashReporter.init(this)
    //     ImageLoader.init(this)
    // }

    // GOOD: Lazy initialization
    val analytics by lazy { Analytics.init(this) }
    val imageLoader by lazy { ImageLoader.init(this) }
}
```
{% endif %}

{% if platform == "ios" %}
### iOS Startup

```swift
// Measure launch time
class AppDelegate: UIResponder, UIApplicationDelegate {
    let launchTime = CFAbsoluteTimeGetCurrent()

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions...) -> Bool {
        // Critical path only

        // Defer non-critical work
        DispatchQueue.main.async {
            self.setupAnalytics()
            self.setupPushNotifications()
        }

        let elapsed = CFAbsoluteTimeGetCurrent() - launchTime
        print("Launch time: \(elapsed)s")
        return true
    }
}

// Use lazy initialization
class DataManager {
    static let shared = DataManager()
    lazy var database: Database = {
        return Database.open()
    }()
}
```
{% endif %}

---

## 2. App Size Optimization

### Size Breakdown

```
Typical App Size Composition:
├── Code (DEX/binary)     30-40%
├── Resources (images)    30-50%
├── Native libraries      10-20%
└── Assets (fonts, etc)   5-10%
```

### Reduction Strategies

```
IMAGES
- Use WebP format (25-35% smaller than PNG)
- Implement responsive images (1x, 2x, 3x)
- Consider vector graphics (SVG) for icons
- Compress with tools (TinyPNG, ImageOptim)

CODE
- Enable minification/obfuscation
- Remove unused code (tree shaking)
- Use ProGuard/R8 (Android)
- Strip debug symbols (iOS release)

NATIVE LIBRARIES
- Use ABI splits (Android)
- Remove unused architectures
- Consider dynamic feature modules

ASSETS
- Subset fonts (only needed characters)
- Compress audio/video
- Load large assets on demand
```

{% if platform == "android" %}
### Android App Bundles

```kotlin
// build.gradle
android {
    bundle {
        language {
            enableSplit = true  // Language-specific resources
        }
        density {
            enableSplit = true  // Screen density resources
        }
        abi {
            enableSplit = true  // CPU architecture
        }
    }
}

// Dynamic feature modules
dynamicFeatures = [':feature_camera', ':feature_ar']
```
{% endif %}

{% if platform == "ios" %}
### iOS App Thinning

```swift
// Xcode settings for App Thinning
// - Enable Bitcode: YES
// - Enable On Demand Resources
// - Asset Catalog: use asset slicing

// On-Demand Resources
if let path = Bundle.main.path(forResource: "LargeVideo",
                                ofType: "mp4",
                                inDirectory: nil,
                                forLocalization: nil) {
    // Resource available
} else {
    // Request resource download
    let request = NSBundleResourceRequest(tags: ["premium_content"])
    request.beginAccessingResources { error in
        // Handle download
    }
}
```
{% endif %}

---

## 3. Memory Management

### Memory Budgets

```
TYPICAL MEMORY LIMITS
├── iOS:     ~150-200MB before warnings
├── Android: Varies by device (128MB-512MB)
└── Target:  < 100MB typical usage

MEMORY TYPES
├── Heap:    Objects, collections
├── Stack:   Local variables
├── Images:  Bitmap memory (often largest)
└── Native:  NDK/JNI allocations
```

### Common Memory Issues

```
1. MEMORY LEAKS
   - Retained references (closures, listeners)
   - Static references to contexts/activities
   - Unregistered observers

2. IMAGE MEMORY
   - Large bitmaps loaded at full resolution
   - Image caching too aggressive
   - Not recycling bitmaps

3. COLLECTION GROWTH
   - Unbounded caches
   - Event listener accumulation
   - History/undo stacks
```

### Memory Optimization

```
IMAGES
- Load at display size, not full resolution
- Use memory-efficient formats (RGB_565 vs ARGB_8888)
- Implement LRU caching with size limits
- Release images when off-screen

OBJECT POOLING
- Reuse expensive objects
- Pool view holders in lists
- Recycle allocations in loops

LIFECYCLE AWARENESS
- Release resources in onPause/onStop
- Clear caches on memory warnings
- Use weak references for callbacks
```

{% if platform == "android" %}
```kotlin
// Detect memory pressure
class MyApplication : Application(), ComponentCallbacks2 {
    override fun onTrimMemory(level: Int) {
        when (level) {
            TRIM_MEMORY_RUNNING_LOW -> {
                imageCache.trimToSize(imageCache.size() / 2)
            }
            TRIM_MEMORY_RUNNING_CRITICAL -> {
                imageCache.evictAll()
            }
        }
    }
}

// Avoid memory leaks with lifecycle
class MyViewModel : ViewModel() {
    private val _data = MutableLiveData<Data>()
    val data: LiveData<Data> = _data

    override fun onCleared() {
        // Clean up resources
    }
}
```
{% endif %}

{% if platform == "ios" %}
```swift
// Handle memory warnings
class ViewController: UIViewController {
    var imageCache = NSCache<NSString, UIImage>()

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        imageCache.removeAllObjects()
    }
}

// Use autorelease pools for loops
func processLargeDataset() {
    for item in largeArray {
        autoreleasepool {
            processItem(item) // Temporary objects released each iteration
        }
    }
}
```
{% endif %}

---

## 4. Rendering Performance

### Frame Rate Targets

```
60 FPS = 16.67ms per frame
90 FPS = 11.11ms per frame
120 FPS = 8.33ms per frame

FRAME BUDGET
├── Input handling:     ~2ms
├── Layout/measure:     ~4ms
├── Draw:               ~6ms
├── GPU render:         ~4ms
└── Buffer:             ~1ms (for jank tolerance)
```

### Common Rendering Issues

```
OVERDRAW
- Drawing pixels multiple times
- Opaque views on top of others
- Fix: Flatten hierarchy, remove backgrounds

LAYOUT THRASHING
- Repeated measure/layout passes
- Nested weights (Android)
- Fix: Use ConstraintLayout, flatten hierarchy

MAIN THREAD BLOCKING
- Heavy computation during scroll
- Synchronous I/O
- Fix: Move to background thread
```

### List Performance

```
VIRTUALIZATION
- Only render visible items
- Recycle off-screen views
- Prefetch upcoming items

VIEW RECYCLING
- Reuse view holders
- Avoid allocation in bind methods
- Use stable IDs for animations

OPTIMIZATIONS
- Fixed item heights (skip measure)
- Precompute item layouts
- Avoid nested scrolling
```

{% if platform == "android" %}
```kotlin
// Efficient RecyclerView
class MyAdapter : RecyclerView.Adapter<ViewHolder>() {
    init {
        setHasStableIds(true) // Enable item animations
    }

    override fun getItemId(position: Int) = items[position].id

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        // AVOID: Creating objects in bind
        // holder.icon.setImageDrawable(ContextCompat.getDrawable(...))

        // GOOD: Reuse/cache drawables
        holder.icon.setImageResource(R.drawable.icon)
    }
}

// Use DiffUtil for efficient updates
val diffResult = DiffUtil.calculateDiff(MyDiffCallback(old, new))
diffResult.dispatchUpdatesTo(adapter)
```
{% endif %}

---

## 5. Network Optimization

### Network Best Practices

```
REQUEST OPTIMIZATION
├── Batch requests where possible
├── Use appropriate cache headers
├── Compress request/response bodies
├── Use HTTP/2 or HTTP/3
└── Implement retry with exponential backoff

CACHING STRATEGY
├── Cache-First: Return cache, then update
├── Network-First: Try network, fallback to cache
├── Stale-While-Revalidate: Return stale, update async
└── Cache-Only: Offline support

DATA EFFICIENCY
├── Request only needed fields (GraphQL, sparse fields)
├── Paginate large lists
├── Use delta sync for updates
└── Compress images server-side
```

### Offline Support

```
OFFLINE-FIRST ARCHITECTURE
┌─────────────────────────────────────────────────────────┐
│  UI ←→ Local Cache ←→ Sync Engine ←→ Network          │
└─────────────────────────────────────────────────────────┘

1. Always read from local cache
2. UI updates immediately (optimistic)
3. Sync engine handles network in background
4. Resolve conflicts when back online
```

---

## 6. Battery Optimization

### Battery Drains

```
TOP BATTERY CONSUMERS
├── GPS/Location:     Very High
├── Network:          High
├── CPU (active):     High
├── Screen:           High
├── Sensors:          Medium
└── Bluetooth:        Low-Medium
```

### Optimization Strategies

```
LOCATION
- Use coarse location when possible
- Batch location updates
- Stop updates when not needed
- Use geofencing instead of polling

NETWORK
- Batch network requests
- Defer non-urgent syncs
- Use push instead of polling
- Respect connectivity changes

BACKGROUND WORK
- Use job schedulers (WorkManager/BGTaskScheduler)
- Respect battery saver mode
- Minimize wake locks
- Batch background operations
```

{% if platform == "android" %}
```kotlin
// Use WorkManager for battery-efficient background work
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.UNMETERED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS
)
    .setConstraints(constraints)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync", ExistingPeriodicWorkPolicy.KEEP, syncWork
)
```
{% endif %}

{% if platform == "ios" %}
```swift
// Use BGTaskScheduler for background work
BGTaskScheduler.shared.register(
    forTaskWithIdentifier: "com.app.refresh",
    using: nil
) { task in
    self.handleAppRefresh(task: task as! BGAppRefreshTask)
}

func scheduleAppRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)
    try? BGTaskScheduler.shared.submit(request)
}
```
{% endif %}

---

## Quick Reference

### Performance Checklist

- [ ] Startup time < 2 seconds
- [ ] App size < 100MB (or use app bundles)
- [ ] Memory usage < 150MB typical
- [ ] 60 FPS during scrolling
- [ ] No ANRs (Android) or watchdog kills (iOS)
- [ ] Battery drain < 5%/hour active use
- [ ] Network requests are batched and cached
- [ ] Images are properly sized and compressed

### Profiling Workflow

```
1. MEASURE
   - Profile before optimizing
   - Use production-like data
   - Test on low-end devices

2. IDENTIFY
   - Find the bottleneck
   - Focus on biggest impact

3. OPTIMIZE
   - One change at a time
   - Measure improvement

4. VALIDATE
   - Test on multiple devices
   - Monitor in production
```

---

## Related Skills

- `react-native-patterns` - Cross-platform development
- `ios-development` - iOS-specific patterns
- `android-development` - Android-specific patterns
