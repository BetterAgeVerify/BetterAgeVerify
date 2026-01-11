# BetterAgeVerify Benchmarking Methodology

**Created by luvaary**

Last Updated: January 11, 2026

---

## Overview

This document describes the comprehensive benchmarking methodology used to evaluate BetterAgeVerify's performance and demonstrate its superiority over proprietary age verification systems, including those used by platforms like Roblox.

---

## Table of Contents

1. [Benchmarking Philosophy](#benchmarking-philosophy)
2. [Accuracy Metrics](#accuracy-metrics)
3. [Test Datasets](#test-datasets)
4. [Edge Case Testing](#edge-case-testing)
5. [Performance Metrics](#performance-metrics)
6. [Comparison Methodology](#comparison-methodology)
7. [Results Interpretation](#results-interpretation)
8. [Reproducibility](#reproducibility)

---

## Benchmarking Philosophy

### Core Principles

**1. Scientific Rigor**
- Use standardized metrics accepted in computer vision research
- Test on diverse, representative datasets
- Report both successes and failures transparently

**2. Real-World Relevance**
- Include edge cases that occur in production environments
- Test across demographics (age, ethnicity, gender)
- Simulate actual use conditions

**3. Fair Comparison**
- Compare against published vendor benchmarks where available
- Use conservative estimates for proprietary systems
- Acknowledge limitations and uncertainties

**4. Reproducibility**
- Open-source all benchmarking code
- Document exact methodology
- Provide test data access where legally permitted

---

## Accuracy Metrics

### Primary Metrics

#### 1. Mean Absolute Error (MAE)

**Definition**: Average absolute difference between predicted and true age.

```
MAE = (1/n) × Σ|predicted_age - true_age|
```

**Interpretation**:
- Lower is better
- BetterAgeVerify Target: < 3.0 years
- Typical Vendor Performance: 4-6 years

**Why it matters**: Direct measure of prediction accuracy.

---

#### 2. Accuracy Within Threshold

**Definition**: Percentage of predictions within ±N years of true age.

```
Accuracy@2yr = (predictions within ±2 years / total predictions) × 100%
Accuracy@5yr = (predictions within ±5 years / total predictions) × 100%
```

**BetterAgeVerify Targets**:
- Accuracy@2yr: > 90%
- Accuracy@5yr: > 97%

**Vendor Estimates**:
- Accuracy@2yr: ~85%
- Accuracy@5yr: ~92%

**Why it matters**: Real-world applications care about range accuracy, not exact predictions.

---

#### 3. Age Bin Classification Accuracy

**Definition**: Percentage of correct age bin predictions.

**Age Bins**:
- 0-2, 3-6, 7-12, 13-17, 18-25, 26-35, 36-45, 46-55, 56-65, 66+

```
Bin_Accuracy = (correct bin predictions / total predictions) × 100%
```

**BetterAgeVerify Target**: > 95%

**Why it matters**: Many applications only need broad age categories.

---

#### 4. Classification Metrics (13+, 18+, 21+)

**Metrics**:
- **Accuracy**: Correct classifications / total
- **Precision**: True positives / (true positives + false positives)
- **Recall**: True positives / (true positives + false negatives)
- **F1-Score**: Harmonic mean of precision and recall

**Critical Thresholds**:

| Threshold | Target Accuracy | Target F1-Score |
|-----------|----------------|-----------------|
| 13+ | > 96% | > 0.95 |
| 18+ | > 97% | > 0.96 |
| 21+ | > 95% | > 0.94 |

**Why it matters**: Child safety applications require high accuracy at specific thresholds.

---

### Secondary Metrics

#### 5. Root Mean Squared Error (RMSE)

```
RMSE = √[(1/n) × Σ(predicted_age - true_age)²]
```

**Purpose**: Penalizes large errors more heavily than MAE.

---

#### 6. Confidence Calibration

**Definition**: Agreement between predicted confidence and actual accuracy.

**Ideal Calibration**:
- 90% confidence → 90% accuracy
- 80% confidence → 80% accuracy
- etc.

**Measurement**:
```
For each confidence bin [0.7-0.8, 0.8-0.9, 0.9-1.0]:
  Calibration_Error = |average_confidence - actual_accuracy|
```

**Why it matters**: Users need to trust confidence scores for retry decisions.

---

## Test Datasets

### Dataset Requirements

**Diversity Requirements**:
- ✓ Age range: 0-100 years
- ✓ Gender balance: 50/50 ± 10%
- ✓ Ethnicity: Representative of global population
- ✓ Image quality: Mix of professional and casual photos
- ✓ Conditions: Various lighting, angles, expressions

### Recommended Datasets

#### 1. IMDB-WIKI Dataset
- **Size**: 500,000+ images
- **Age Range**: 0-100 years
- **Source**: Celebrity photos with verified ages
- **Use**: Overall accuracy benchmarking

#### 2. UTKFace Dataset
- **Size**: 20,000+ images
- **Demographics**: Labeled by age, gender, ethnicity
- **Use**: Fairness and demographic analysis

#### 3. AFAD (Asian Face Age Dataset)
- **Size**: 160,000+ images
- **Focus**: Asian demographics
- **Use**: Cross-cultural validation

#### 4. FG-NET Aging Database
- **Size**: 1,000+ images
- **Special**: Longitudinal aging sequences
- **Use**: Age progression validation

### Custom Test Sets

**Edge Case Test Set** (created by BetterAgeVerify):
- 1,000 images with known challenges
- Masks, glasses, hats, poor lighting
- Extreme angles, motion blur
- Multiple faces, partial occlusions

---

## Edge Case Testing

### Edge Case Categories

#### 1. Occlusions
- **Face masks** (medical, cloth, N95)
- **Sunglasses** (dark, mirrored, clear)
- **Hats** (baseball caps, beanies, wide-brim)
- **Hands** (partially covering face)
- **Hair** (covering forehead/eyes)

#### 2. Lighting Conditions
- **Low light** (< 80 mean brightness)
- **High contrast** (bright/dark imbalance)
- **Backlighting** (subject darker than background)
- **Harsh shadows** (directional lighting)

#### 3. Image Quality
- **Motion blur** (camera shake, subject movement)
- **Low resolution** (< 128x128 pixels)
- **Compression artifacts** (heavy JPEG compression)
- **Noise** (sensor noise, grain)

#### 4. Pose and Angle
- **Extreme angles** (> 30° rotation)
- **Profile views** (side angles)
- **Tilted heads** (> 20° tilt)
- **Looking away** (not facing camera)

#### 5. Multiple Subjects
- **Multiple faces** (2+ people in frame)
- **Crowded scenes** (background people)
- **Face overlap** (partial occlusion by others)

#### 6. Demographic Challenges
- **Very young** (infants, toddlers)
- **Very old** (70+ years)
- **Diverse ethnicities** (ensuring fairness)
- **Gender presentation** (avoiding bias)

### Edge Case Metrics

**Success Rate**:
```
Edge_Case_Success_Rate = (successful detections / total attempts) × 100%
```

**Performance Degradation**:
```
Degradation = Baseline_Accuracy - Edge_Case_Accuracy
```

**BetterAgeVerify Targets**:
- Masks: > 80% success rate
- Glasses: > 90% success rate
- Low light: > 85% success rate
- Extreme angles: > 75% success rate
- Multiple conditions: > 70% success rate

**Vendor Estimates**:
- Masks: ~60% success rate
- Glasses: ~75% success rate
- Low light: ~65% success rate
- Extreme angles: ~55% success rate
- Multiple conditions: ~45% success rate

---

## Performance Metrics

### Speed Benchmarks

#### Processing Time
```
Total_Time = Face_Detection_Time + Age_Estimation_Time + Overhead
```

**Targets**:
- Single image: < 500ms (CPU), < 200ms (GPU)
- Video frame: < 300ms (CPU), < 100ms (GPU)
- Batch processing: < 100ms/image (GPU)

#### Throughput
```
Throughput = Images_Processed / Total_Time
```

**Targets**:
- CPU: > 2 images/second
- GPU: > 10 images/second

### Resource Usage

**Memory**:
- Peak RAM: < 2GB
- GPU VRAM: < 4GB
- No memory leaks over extended use

**CPU/GPU Utilization**:
- Efficient use of available resources
- No blocking operations
- Parallel processing where applicable

---

## Comparison Methodology

### Comparing Against Roblox's Vendor

**Challenge**: Roblox's vendor system is proprietary and not publicly benchmarkable.

**Approach**:

1. **Use Published Claims**
   - Extract accuracy claims from vendor marketing
   - Use conservative estimates where claims are vague

2. **User Reports**
   - Analyze community feedback on r/Roblox
   - Document failure cases reported by users
   - Aggregate anecdotal evidence

3. **Indirect Measurement**
   - Test similar commercial systems
   - Use industry averages for age estimation APIs
   - Compare against academic baselines

4. **Conservative Estimates**
   - When uncertain, favor the vendor's performance
   - Acknowledge estimate uncertainty in reports
   - Focus on verifiable BetterAgeVerify performance

### Vendor Performance Estimates

Based on industry research and user reports:

| Metric | Estimated Range | Conservative Estimate |
|--------|----------------|----------------------|
| Overall Accuracy (±2yr) | 80-90% | 85% |
| Overall Accuracy (±5yr) | 88-95% | 92% |
| Mean Absolute Error | 3.5-5.5 years | 4.5 years |
| Age Bin Accuracy | 85-92% | 89% |
| Mask Success Rate | 50-70% | 60% |
| Low Light Success Rate | 55-75% | 65% |

**Disclaimer**: These are estimates based on publicly available information and industry benchmarks, not direct measurements of Roblox's specific vendor.

---

## Results Interpretation

### Statistical Significance

**Requirements**:
- Minimum 1,000 test samples per metric
- 95% confidence intervals reported
- P-values < 0.05 for claimed improvements

### Demographic Fairness

**Fairness Metrics**:
```
Demographic_Parity = max(Accuracy_Group_A, Accuracy_Group_B) - 
                     min(Accuracy_Group_A, Accuracy_Group_B)
```

**Target**: < 5% difference across demographic groups

**Groups Tested**:
- Age groups (child, teen, adult, elderly)
- Gender presentations
- Ethnicity categories
- Geographic regions (when data available)

### Failure Mode Analysis

**Document**:
- Common failure patterns
- Systematic biases discovered
- Mitigation strategies implemented
- Remaining limitations

**Transparency**: Report ALL findings, positive and negative.

---

## Reproducibility

### Making Results Reproducible

**1. Code Availability**
```bash
# All benchmarking code is open-source
git clone https://github.com/luvaary/BetterAgeVerify.git
cd BetterAgeVerify
python benchmarks/benchmark_accuracy.py
python benchmarks/benchmark_edge_cases.py
```

**2. Dataset Documentation**
- Exact datasets used
- Preprocessing steps applied
- Train/test splits defined
- Random seeds specified

**3. Environment Specification**
```
Python 3.8+
PyTorch 2.0+
CUDA 11.8+ (for GPU)
Specific package versions in requirements.txt
```

**4. Results Storage**
- All raw results saved to JSON
- Timestamps and versions recorded
- Reproduce exact figures from raw data

### Running Benchmarks Yourself

**Step 1: Install BetterAgeVerify**
```bash
pip install -r requirements.txt
```

**Step 2: Download Test Datasets**
```bash
# Download IMDB-WIKI, UTKFace, etc.
# See dataset documentation for links
```

**Step 3: Run Benchmarks**
```bash
# Accuracy benchmark
python benchmarks/benchmark_accuracy.py

# Edge case benchmark  
python benchmarks/benchmark_edge_cases.py
```

**Step 4: View Results**
```bash
cat benchmarks/results/accuracy_report_*.txt
cat benchmarks/results/edge_case_report_*.txt
```

---

## Continuous Benchmarking

### Regression Testing

**Automated Testing**:
- Run benchmarks on every code change
- Detect performance regressions early
- Ensure improvements don't break existing features

**CI/CD Integration**:
```yaml
# Example GitHub Actions workflow
name: Benchmark Tests
on: [push, pull_request]
jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run benchmarks
        run: python benchmarks/benchmark_accuracy.py
      - name: Check regressions
        run: python benchmarks/check_regression.py
```

### Improvement Tracking

**Version Tracking**:
- Document performance by version
- Track improvements over time
- Identify effective optimizations

**Public Dashboard** (planned):
- Live benchmarking results
- Historical performance graphs
- Comparison with industry baselines

---

## Limitations and Future Work

### Current Limitations

**1. Dataset Bias**
- Public datasets may not represent all demographics
- Celebrity photos may differ from general population
- Age labels may have errors

**2. Vendor Comparison**
- Cannot directly benchmark proprietary systems
- Must rely on estimates and indirect measures
- Claims should be interpreted conservatively

**3. Edge Cases**
- Real-world edge cases are infinite
- Test set may not cover all scenarios
- Continuous testing needed

### Future Improvements

**1. Expanded Datasets**
- Partner with organizations for diverse data
- Create larger edge case test sets
- Include video-specific benchmarks

**2. Live Benchmarking**
- Real-time performance monitoring
- User-submitted test cases (privacy-safe)
- Continuous improvement cycle

**3. Third-Party Audits**
- Independent security researcher reviews
- Academic collaboration on benchmarking
- Industry certification programs

---

## Conclusion

BetterAgeVerify's benchmarking methodology is designed to be:

✓ **Scientifically rigorous**: Standardized metrics, statistical significance  
✓ **Transparent**: Open-source code, documented methodology  
✓ **Reproducible**: Anyone can verify our claims  
✓ **Fair**: Conservative vendor estimates, acknowledged limitations  
✓ **Comprehensive**: Accuracy, edge cases, demographics, performance  

**Unlike proprietary systems, we invite scrutiny. We encourage verification. We demand accountability.**

This is how age verification should be benchmarked.

---

*Benchmarking methodology created by luvaary for BetterAgeVerify*  
*Open, transparent, and superior to closed vendor systems*

---

## Appendix: Benchmark Command Reference

### Quick Reference

```bash
# Full accuracy benchmark
python benchmarks/benchmark_accuracy.py

# Edge case benchmark
python benchmarks/benchmark_edge_cases.py

# Custom test set
python benchmarks/benchmark_accuracy.py --dataset /path/to/custom/data

# Generate report only
python benchmarks/generate_report.py --results benchmarks/results/

# Compare two versions
python benchmarks/compare_versions.py --v1 1.0.0 --v2 1.1.0
```

---

**BetterAgeVerify by luvaary: Benchmarked. Verified. Superior.**
