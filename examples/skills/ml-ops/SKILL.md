---
name: ml-ops
description: |
  MLOps practices for deploying and operating ML/LLM systems in production.
  Covers model serving, monitoring, A/B testing, CI/CD for ML, feature stores,
  model registries, and operational best practices.
version: 1.0.0
tags: [mlops, deployment, monitoring, ml, llm, production, serving]
category: ai/operations
trigger_phrases:
  - "MLOps"
  - "model deployment"
  - "model serving"
  - "ML monitoring"
  - "model registry"
  - "feature store"
  - "ML pipeline"
  - "model performance"
  - "production ML"
  - "LLMOps"
variables:
  focus:
    type: string
    description: Primary focus area
    enum: [serving, monitoring, pipeline, all]
    default: all
  scale:
    type: string
    description: Deployment scale
    enum: [startup, growth, enterprise]
    default: growth
---

# MLOps Guide

## Core Philosophy

**MLOps is DevOps + Data + Models.** You need all three disciplines working together: software engineering rigor, data quality management, and model performance monitoring.

> "A model is only as good as its last prediction in production."

---

## MLOps Maturity Levels

```
Level 0: Manual everything
├── Jupyter notebooks → manual deployment
├── No versioning, no monitoring
└── "It works on my machine"

Level 1: ML Pipeline automation
├── Automated training pipeline
├── Model registry
└── Basic monitoring

Level 2: CI/CD for ML
├── Automated testing (data + model)
├── Automated deployment
└── Feature store

Level 3: Full automation
├── Automated retraining triggers
├── A/B testing infrastructure
└── Self-healing systems
```

---

## 1. Model Serving

### Serving Patterns

| Pattern | Use Case | Latency | Complexity |
|---------|----------|---------|------------|
| **REST API** | General purpose | 50-500ms | Low |
| **Batch** | Offline scoring | Hours | Low |
| **Streaming** | Real-time events | 10-100ms | High |
| **Edge** | On-device | <10ms | High |

### FastAPI Model Server

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import pipeline
from contextlib import asynccontextmanager
import asyncio
from typing import Optional

# Global model reference
MODEL = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown."""
    global MODEL
    MODEL = pipeline("text-classification", model="distilbert-base-uncased")
    yield
    # Cleanup
    MODEL = None

app = FastAPI(lifespan=lifespan)

class PredictionRequest(BaseModel):
    text: str
    max_length: Optional[int] = 512

class PredictionResponse(BaseModel):
    label: str
    score: float
    model_version: str

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Run inference."""
    if MODEL is None:
        raise HTTPException(503, "Model not loaded")

    try:
        # Run inference in thread pool (CPU-bound)
        result = await asyncio.to_thread(
            MODEL,
            request.text[:request.max_length]
        )
        return PredictionResponse(
            label=result[0]["label"],
            score=result[0]["score"],
            model_version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None
    }
```

### Request Batching

```python
import asyncio
from collections import deque
from dataclasses import dataclass
from typing import Any
import time

@dataclass
class BatchRequest:
    data: Any
    future: asyncio.Future
    timestamp: float

class DynamicBatcher:
    """Batch requests for efficient GPU utilization."""

    def __init__(
        self,
        model,
        max_batch_size: int = 32,
        max_wait_ms: float = 50.0
    ):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms / 1000
        self.queue: deque[BatchRequest] = deque()
        self._lock = asyncio.Lock()
        self._processing = False

    async def predict(self, data: Any) -> Any:
        """Add request to batch and wait for result."""
        future = asyncio.get_event_loop().create_future()
        request = BatchRequest(data=data, future=future, timestamp=time.time())

        async with self._lock:
            self.queue.append(request)

            if not self._processing:
                self._processing = True
                asyncio.create_task(self._process_batch())

        return await future

    async def _process_batch(self):
        """Process accumulated requests as a batch."""
        await asyncio.sleep(self.max_wait_ms)  # Wait for more requests

        async with self._lock:
            # Collect batch
            batch = []
            while self.queue and len(batch) < self.max_batch_size:
                batch.append(self.queue.popleft())

            self._processing = bool(self.queue)

        if not batch:
            return

        # Run batch inference
        try:
            inputs = [r.data for r in batch]
            results = await asyncio.to_thread(self.model, inputs)

            for request, result in zip(batch, results):
                request.future.set_result(result)
        except Exception as e:
            for request in batch:
                request.future.set_exception(e)

        # Process remaining queue
        if self._processing:
            asyncio.create_task(self._process_batch())
```

### GPU Memory Management

```python
import torch
from contextlib import contextmanager

@contextmanager
def torch_gc():
    """Clean up GPU memory after inference."""
    try:
        yield
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def get_gpu_memory_info() -> dict:
    """Get current GPU memory usage."""
    if not torch.cuda.is_available():
        return {"available": False}

    return {
        "available": True,
        "allocated_gb": torch.cuda.memory_allocated() / 1e9,
        "reserved_gb": torch.cuda.memory_reserved() / 1e9,
        "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
    }
```

---

## 2. Model Registry

### MLflow Registry

```python
import mlflow
from mlflow.tracking import MlflowClient

# Set tracking URI
mlflow.set_tracking_uri("http://mlflow-server:5000")
client = MlflowClient()

def register_model(
    model_path: str,
    model_name: str,
    metrics: dict,
    params: dict,
    tags: dict = None
) -> str:
    """Register a model with MLflow."""
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params(params)

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log tags
        if tags:
            mlflow.set_tags(tags)

        # Log and register model
        model_info = mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=model_path,
            registered_model_name=model_name
        )

        return model_info.model_uri

def promote_model(model_name: str, version: int, stage: str):
    """Promote model to a stage (Staging, Production, Archived)."""
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage
    )

def load_production_model(model_name: str):
    """Load the production version of a model."""
    model_uri = f"models:/{model_name}/Production"
    return mlflow.pyfunc.load_model(model_uri)
```

### Model Versioning Best Practices

```yaml
# model_card.yaml
name: sentiment-classifier
version: 2.3.1
created_at: 2024-01-15
training_data:
  dataset: sentiment-v3
  size: 100000
  date_range: "2023-01 to 2023-12"
performance:
  accuracy: 0.94
  f1_score: 0.93
  latency_p95_ms: 45
dependencies:
  transformers: "4.35.0"
  torch: "2.1.0"
changelog:
  - "Added support for sarcasm detection"
  - "Improved handling of emojis"
```

---

## 3. Monitoring & Observability

### Key Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
PREDICTION_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing prediction',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

PREDICTION_COUNT = Counter(
    'model_predictions_total',
    'Total predictions made',
    ['model_version', 'status']
)

# Model health
CONFIDENCE_SCORE = Histogram(
    'model_confidence_score',
    'Distribution of prediction confidence',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

INPUT_LENGTH = Histogram(
    'model_input_length',
    'Distribution of input lengths',
    buckets=[10, 50, 100, 500, 1000, 5000]
)

# System metrics
GPU_MEMORY_USED = Gauge(
    'gpu_memory_used_bytes',
    'GPU memory currently in use'
)

def track_prediction(func):
    """Decorator to track prediction metrics."""
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            PREDICTION_COUNT.labels(
                model_version="1.0",
                status="success"
            ).inc()
            CONFIDENCE_SCORE.observe(result.score)
            return result
        except Exception as e:
            PREDICTION_COUNT.labels(
                model_version="1.0",
                status="error"
            ).inc()
            raise
        finally:
            PREDICTION_LATENCY.observe(time.time() - start)
    return wrapper
```

### Data Drift Detection

```python
import numpy as np
from scipy import stats
from dataclasses import dataclass

@dataclass
class DriftResult:
    feature: str
    drift_detected: bool
    p_value: float
    statistic: float

def detect_drift_ks(
    reference: np.ndarray,
    current: np.ndarray,
    threshold: float = 0.05
) -> DriftResult:
    """Detect drift using Kolmogorov-Smirnov test."""
    statistic, p_value = stats.ks_2samp(reference, current)
    return DriftResult(
        feature="distribution",
        drift_detected=p_value < threshold,
        p_value=p_value,
        statistic=statistic
    )

def monitor_input_distribution(
    reference_stats: dict,
    current_batch: list[dict]
) -> list[DriftResult]:
    """Monitor for distribution shifts in input features."""
    results = []

    for feature, ref_values in reference_stats.items():
        current_values = [item.get(feature, 0) for item in current_batch]

        if len(current_values) < 30:
            continue  # Not enough samples

        result = detect_drift_ks(
            np.array(ref_values),
            np.array(current_values)
        )
        result.feature = feature
        results.append(result)

    return results
```

### Performance Degradation Detection

```python
from collections import deque
from dataclasses import dataclass
import statistics

@dataclass
class PerformanceAlert:
    metric: str
    current_value: float
    baseline_value: float
    degradation_pct: float
    alert_level: str  # "warning", "critical"

class PerformanceMonitor:
    """Track model performance over time."""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latencies = deque(maxlen=window_size)
        self.confidences = deque(maxlen=window_size)
        self.error_count = 0
        self.total_count = 0

        # Baselines (set during deployment)
        self.baseline_latency_p95 = None
        self.baseline_confidence_mean = None

    def record(self, latency: float, confidence: float, error: bool = False):
        """Record a prediction result."""
        self.latencies.append(latency)
        self.confidences.append(confidence)
        self.total_count += 1
        if error:
            self.error_count += 1

    def set_baseline(self):
        """Set current metrics as baseline."""
        if len(self.latencies) < 100:
            raise ValueError("Need at least 100 samples for baseline")

        sorted_latencies = sorted(self.latencies)
        self.baseline_latency_p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        self.baseline_confidence_mean = statistics.mean(self.confidences)

    def check_alerts(self) -> list[PerformanceAlert]:
        """Check for performance degradation."""
        alerts = []

        if self.baseline_latency_p95 is None:
            return alerts

        # Current metrics
        sorted_latencies = sorted(self.latencies)
        current_p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        current_confidence = statistics.mean(self.confidences)

        # Latency check
        latency_increase = (current_p95 - self.baseline_latency_p95) / self.baseline_latency_p95
        if latency_increase > 0.5:  # 50% increase
            alerts.append(PerformanceAlert(
                metric="latency_p95",
                current_value=current_p95,
                baseline_value=self.baseline_latency_p95,
                degradation_pct=latency_increase * 100,
                alert_level="critical" if latency_increase > 1.0 else "warning"
            ))

        # Confidence check
        confidence_drop = (self.baseline_confidence_mean - current_confidence) / self.baseline_confidence_mean
        if confidence_drop > 0.1:  # 10% drop
            alerts.append(PerformanceAlert(
                metric="confidence_mean",
                current_value=current_confidence,
                baseline_value=self.baseline_confidence_mean,
                degradation_pct=confidence_drop * 100,
                alert_level="critical" if confidence_drop > 0.2 else "warning"
            ))

        return alerts
```

---

## 4. A/B Testing for Models

### Experiment Framework

```python
import random
import hashlib
from dataclasses import dataclass
from typing import Callable
import time

@dataclass
class Variant:
    name: str
    model: Callable
    weight: float  # Traffic percentage (0-1)

class ABTest:
    """A/B testing for model variants."""

    def __init__(self, experiment_name: str, variants: list[Variant]):
        self.experiment_name = experiment_name
        self.variants = variants
        self.results = {v.name: [] for v in variants}

        # Validate weights sum to 1
        total_weight = sum(v.weight for v in variants)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1, got {total_weight}")

    def get_variant(self, user_id: str) -> Variant:
        """Get consistent variant for a user."""
        # Hash user_id for consistent assignment
        hash_input = f"{self.experiment_name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 1000) / 1000  # 0-1

        cumulative = 0
        for variant in self.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                return variant

        return self.variants[-1]

    async def predict(self, user_id: str, input_data: dict) -> dict:
        """Run prediction through assigned variant."""
        variant = self.get_variant(user_id)

        start = time.time()
        result = await variant.model(input_data)
        latency = time.time() - start

        self.results[variant.name].append({
            "latency": latency,
            "timestamp": time.time(),
            **result
        })

        return {
            "variant": variant.name,
            **result
        }

    def get_metrics(self) -> dict:
        """Get metrics for each variant."""
        metrics = {}
        for name, results in self.results.items():
            if not results:
                continue

            latencies = [r["latency"] for r in results]
            metrics[name] = {
                "count": len(results),
                "latency_mean": sum(latencies) / len(latencies),
                "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)],
            }
        return metrics
```

### Statistical Significance

```python
from scipy import stats
import numpy as np

def calculate_significance(
    control_conversions: int,
    control_total: int,
    treatment_conversions: int,
    treatment_total: int,
    confidence_level: float = 0.95
) -> dict:
    """Calculate if treatment is significantly better than control."""

    # Conversion rates
    control_rate = control_conversions / control_total
    treatment_rate = treatment_conversions / treatment_total

    # Pooled standard error
    pooled_rate = (control_conversions + treatment_conversions) / (control_total + treatment_total)
    se = np.sqrt(pooled_rate * (1 - pooled_rate) * (1/control_total + 1/treatment_total))

    # Z-score
    z_score = (treatment_rate - control_rate) / se if se > 0 else 0

    # P-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

    # Confidence interval
    z_critical = stats.norm.ppf((1 + confidence_level) / 2)
    lift = treatment_rate - control_rate
    ci_lower = lift - z_critical * se
    ci_upper = lift + z_critical * se

    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "lift": lift,
        "lift_percent": (lift / control_rate * 100) if control_rate > 0 else 0,
        "p_value": p_value,
        "significant": p_value < (1 - confidence_level),
        "confidence_interval": (ci_lower, ci_upper)
    }
```

---

## 5. CI/CD for ML

### ML Pipeline Example (GitHub Actions)

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    paths:
      - 'training/**'
      - 'models/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly retraining

jobs:
  data-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validate training data
        run: |
          python scripts/validate_data.py \
            --input data/training.csv \
            --schema schemas/training_schema.json

      - name: Check data drift
        run: |
          python scripts/check_drift.py \
            --reference data/reference_stats.json \
            --current data/training.csv

  train:
    needs: data-validation
    runs-on: [self-hosted, gpu]
    steps:
      - uses: actions/checkout@v3

      - name: Train model
        run: |
          python training/train.py \
            --config configs/production.yaml \
            --output models/

      - name: Upload model artifact
        uses: actions/upload-artifact@v3
        with:
          name: model
          path: models/

  test:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Download model
        uses: actions/download-artifact@v3
        with:
          name: model
          path: models/

      - name: Run model tests
        run: |
          pytest tests/model/ -v \
            --model-path models/model.pt

      - name: Performance benchmarks
        run: |
          python scripts/benchmark.py \
            --model models/model.pt \
            --baseline metrics/baseline.json

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: |
          # Register model
          python scripts/register_model.py --stage staging

          # Deploy
          kubectl apply -f k8s/staging/

      - name: Smoke tests
        run: |
          python scripts/smoke_test.py --env staging

      - name: Promote to production
        run: |
          python scripts/register_model.py --stage production
          kubectl apply -f k8s/production/
```

### Model Testing

```python
import pytest
import numpy as np

class TestModelQuality:
    """Tests for model quality and behavior."""

    @pytest.fixture
    def model(self):
        """Load the trained model."""
        from model import load_model
        return load_model("models/model.pt")

    def test_minimum_accuracy(self, model, test_data):
        """Model meets minimum accuracy threshold."""
        predictions = model.predict(test_data.X)
        accuracy = (predictions == test_data.y).mean()
        assert accuracy >= 0.90, f"Accuracy {accuracy} below threshold 0.90"

    def test_latency_budget(self, model):
        """Model inference meets latency requirements."""
        import time
        input_data = np.random.randn(1, 768)

        latencies = []
        for _ in range(100):
            start = time.time()
            model.predict(input_data)
            latencies.append(time.time() - start)

        p95 = sorted(latencies)[95]
        assert p95 < 0.1, f"P95 latency {p95}s exceeds 100ms budget"

    def test_no_regression(self, model, baseline_metrics):
        """Model doesn't regress on key metrics."""
        current_metrics = calculate_metrics(model)

        for metric, baseline in baseline_metrics.items():
            current = current_metrics[metric]
            # Allow 2% regression
            assert current >= baseline * 0.98, \
                f"{metric} regressed: {current} < {baseline * 0.98}"

    def test_edge_cases(self, model):
        """Model handles edge cases gracefully."""
        edge_cases = [
            "",  # Empty input
            "a" * 10000,  # Very long input
            "🔥" * 100,  # Emojis
            "<script>alert('xss')</script>",  # Potential injection
        ]

        for case in edge_cases:
            # Should not raise
            result = model.predict(case)
            assert result is not None
```

---

## Common Pitfalls

### 1. No Rollback Strategy

```python
# BAD: Direct deployment, no rollback
kubectl apply -f new_model.yaml

# GOOD: Blue-green deployment with rollback
class ModelDeployer:
    def deploy(self, model_version: str):
        # Deploy to green
        self._deploy_green(model_version)

        # Verify health
        if not self._health_check("green"):
            self._rollback()
            raise DeploymentError("Health check failed")

        # Shift traffic gradually
        for pct in [10, 25, 50, 100]:
            self._shift_traffic(pct)
            if not self._check_metrics():
                self._rollback()
                raise DeploymentError(f"Metrics degraded at {pct}%")
```

### 2. Ignoring Model Staleness

```python
# BAD: Deploy and forget

# GOOD: Track model freshness
def check_model_freshness(model_metadata: dict) -> dict:
    from datetime import datetime, timedelta

    trained_at = datetime.fromisoformat(model_metadata["trained_at"])
    age_days = (datetime.now() - trained_at).days

    return {
        "trained_at": trained_at,
        "age_days": age_days,
        "needs_retraining": age_days > 30,  # Threshold
        "alert_level": "critical" if age_days > 60 else "warning" if age_days > 30 else "ok"
    }
```

### 3. No Shadow Testing

```python
# BAD: Deploy new model directly

# GOOD: Shadow test first
class ShadowTester:
    """Run new model in shadow mode alongside production."""

    def __init__(self, production_model, shadow_model):
        self.production = production_model
        self.shadow = shadow_model
        self.comparisons = []

    async def predict(self, input_data):
        # Production prediction (returned to user)
        prod_result = await self.production.predict(input_data)

        # Shadow prediction (logged, not returned)
        try:
            shadow_result = await self.shadow.predict(input_data)
            self.comparisons.append({
                "production": prod_result,
                "shadow": shadow_result,
                "match": prod_result == shadow_result
            })
        except Exception as e:
            self.comparisons.append({"shadow_error": str(e)})

        return prod_result
```

---

## Quick Reference

### Monitoring Checklist

- [ ] Latency (p50, p95, p99)
- [ ] Throughput (requests/second)
- [ ] Error rate
- [ ] GPU memory utilization
- [ ] Model confidence distribution
- [ ] Input feature distributions
- [ ] Output distribution drift
- [ ] Business metrics (CTR, conversion, etc.)

### Deployment Checklist

- [ ] Model registered with version
- [ ] Health check endpoint
- [ ] Graceful shutdown handling
- [ ] Resource limits (CPU, memory, GPU)
- [ ] Rollback procedure documented
- [ ] Monitoring dashboards ready
- [ ] Alerting rules configured
- [ ] Load testing passed

---

## Related Skills

- `observability` - General monitoring and alerting
- `kubernetes-patterns` - Container orchestration
- `fine-tuning-guide` - Training models to deploy
