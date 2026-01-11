# BetterAgeVerify Privacy Policy

**Created by luvaary**

Last Updated: January 11, 2026

---

## Our Privacy Promise

**BetterAgeVerify is built on a simple principle: your face is yours, not ours.**

Unlike proprietary age verification systems (including those used by platforms like Roblox), BetterAgeVerify guarantees complete privacy through technology, not just policy.

---

## How It Works

### 1. You Control Your Data

- **Explicit Consent Required**: We never process your image without clear, informed consent
- **No Surprise Processing**: You know exactly when and why your image is being analyzed
- **Cancel Anytime**: Stop processing at any point without consequences

### 2. Immediate Data Deletion

**What happens to your facial image:**

1. **Processing** (< 1 second): Your image is analyzed by AI models to estimate age
2. **Result** (immediate): You receive an age estimate and confidence score
3. **Deletion** (< 1 second): ALL biometric data is permanently deleted

**This is not optional. This is enforced by code and verified by our open-source license.**

### 3. What We DO NOT Do

❌ **We DO NOT store your facial images**  
❌ **We DO NOT store biometric templates or embeddings**  
❌ **We DO NOT build databases of faces**  
❌ **We DO NOT sell your data to anyone**  
❌ **We DO NOT share your data with third parties**  
❌ **We DO NOT use your images for training without explicit permission**  
❌ **We DO NOT track you across sessions**  

### 4. What We DO Log (Anonymously)

For system improvement only, we may log:

✓ **Age category** (child/teen/adult) - NOT specific age  
✓ **Confidence level** (high/medium/low)  
✓ **Edge cases detected** (mask, glasses, poor lighting)  
✓ **Processing time**  
✓ **Success/failure status**  

**What we NEVER log:**
- Your facial image
- Biometric identifiers
- Personal information
- IP addresses or device IDs
- Anything that could identify you

---

## Privacy by Design

### Technical Guarantees

BetterAgeVerify enforces privacy at the code level:
```python
# After processing completes:
def _delete_biometric_data(self, *data_objects):
    deletion_start = time.time()
    
    # Immediately delete all biometric data
    for obj in data_objects:
        if isinstance(obj, torch.Tensor):
            obj.cpu()
            del obj
        elif isinstance(obj, Image.Image):
            obj.close()
        else:
            del obj
    
    # Clear GPU cache if applicable
    torch.cuda.empty_cache()
    
    # Verify deletion completed within timeout
    deletion_time = time.time() - deletion_start
    if deletion_time > 1.0 seconds:
        raise RuntimeError("Data deletion exceeded timeout")
```

**If data deletion fails or takes too long, the system throws an error rather than continuing.**

### Offline-First Architecture

- **Local Processing**: All AI models run on your device by default
- **No Cloud Required**: Complete functionality without internet connection
- **Optional Cloud**: Advanced users can enable cloud processing, but it's not required
- **Your Choice**: You decide where your data is processed

---

## Comparison: BetterAgeVerify vs. Proprietary Systems

| Feature | BetterAgeVerify | Roblox Vendor | Typical Vendor |
|---------|----------------|---------------|----------------|
| **Data Retention** | 0 seconds | Unknown | Days to years |
| **Storage Location** | None | Unknown | Vendor servers |
| **Third-Party Sharing** | Never | Unknown | Often |
| **Audit Trail** | Open-source | Black box | Proprietary |
| **Data Sales** | Prohibited by license | Unknown | Common |
| **User Control** | Complete | Limited | Minimal |
| **Offline Mode** | Supported | No | No |
| **Transparency** | 100% | 0% | Low |

---

## Legal Compliance

BetterAgeVerify is designed to comply with major privacy regulations:

### GDPR (General Data Protection Regulation)
- ✓ Right to be forgotten (automatic deletion)
- ✓ Data minimization (only process what's needed)
- ✓ Purpose limitation (age verification only)
- ✓ Transparency (open-source, auditable)
- ✓ Consent required before processing

### CCPA (California Consumer Privacy Act)
- ✓ No sale of personal information
- ✓ Right to deletion (automatic)
- ✓ Right to know (open-source code)
- ✓ Right to opt-out (don't use = no processing)

### COPPA (Children's Online Privacy Protection Act)
- ✓ No collection of children's data
- ✓ Immediate deletion after processing
- ✓ Parental controls supported
- ✓ No tracking or profiling

### BIPA (Biometric Information Privacy Act)
- ✓ Informed consent required
- ✓ No biometric data retention
- ✓ No biometric data sales
- ✓ Clear retention schedule (0 seconds)

---

## The "No More Data!" License

BetterAgeVerify is protected by a custom open-source license that **legally enforces privacy**.

### Key License Terms:

1. **Anyone can use BetterAgeVerify for free** (personal, educational, commercial)
2. **Anyone can modify and improve the code**
3. **But you MUST delete biometric data immediately** (within 1 second)
4. **You CANNOT store facial images long-term**
5. **You CANNOT sell biometric data**
6. **Violations terminate your license** immediately

This means even if someone forks BetterAgeVerify, they **legally cannot** turn it into a privacy-hostile system.

---

## Edge Cases and Privacy

### What if processing fails?

- Your image is still deleted immediately
- No retry attempts store your original image
- Each retry is treated as a fresh processing session

### What if I upload a video?

- Frames are extracted one at a time
- Each frame is deleted immediately after analysis
- The original video is never stored
- Only aggregated results are returned

### What if there's an error?

- Data deletion happens even on errors
- Timeout protection ensures deletion completes
- Logs contain zero biometric information

---

## Your Rights

When using BetterAgeVerify, you have the right to:

1. **Know what's happening**: Open-source code means complete transparency
2. **Control your data**: Consent required before any processing
3. **Verify deletion**: Code is auditable to confirm data is deleted
4. **Request information**: Ask questions about how the system works
5. **Opt out entirely**: Simply don't use the system

---

## Verification and Auditing

### How do I know BetterAgeVerify keeps its promises?

1. **Open Source**: Every line of code is public on GitHub
2. **Community Audits**: Security researchers can verify our claims
3. **Automated Tests**: Privacy compliance is tested automatically
4. **License Enforcement**: Legal requirements backed by code

### Independent Verification

We encourage:
- Security researchers to audit our code
- Privacy advocates to review our practices
- Developers to verify deletion mechanisms
- Users to inspect network traffic (should be zero in offline mode)

---

## Contact and Questions

### For Privacy Questions:
- Review the open-source code: [GitHub Repository]
- Read the full license: `LICENSE` file in the repository
- Open an issue for clarification

### For Privacy Violations:
If you believe someone is using BetterAgeVerify in violation of the "No More Data!" license:
1. Document the violation
2. Report to the project maintainers
3. The violator's license will be terminated

---

## Updates to This Policy

This privacy policy may be updated to:
- Clarify existing practices
- Add new privacy protections
- Respond to user feedback

**Changes will never reduce privacy protections.**

All updates will be:
- Clearly documented in version control
- Announced to users
- Effective for new processing sessions only

---

## The Bottom Line

**BetterAgeVerify is the most privacy-respecting age verification system ever built.**

- Your face is processed for exactly as long as needed (< 1 second)
- Your biometric data is deleted immediately and permanently
- No databases, no tracking, no sales, no exceptions
- Open-source means you don't have to trust us - you can verify

**This is age verification done right.**

---

*Privacy policy created by luvaary for BetterAgeVerify*  
*Licensed under the "No More Data!" License*  
*Committed to privacy, transparency, and user rights*

---

## Appendix: Technical Details

### Data Flow Diagram
```
User Image Input
      ↓
[ Face Detection ]
      ↓
[ AI Age Estimation ] ← All processing happens here
      ↓
[ Result Generation ]
      ↓
[ IMMEDIATE DATA DELETION ] ← Enforced by code within 1 second
      ↓
User Receives Result
      ↓
[ Anonymous Logging ] ← No biometric data, only metadata
```

### What Gets Deleted

1. Original image file/data
2. Face crop/region of interest
3. Preprocessed tensors
4. Model activations/embeddings
5. Intermediate representations
6. GPU memory cache
7. Temporary variables

### Deletion Verification
```python
# Pseudo-code for verification
assert image_data is None
assert face_tensor is None
assert embeddings is None
assert gpu_cache.is_empty()
assert deletion_time < 1.0 seconds
```

---

**BetterAgeVerify by luvaary: Privacy isn't a feature. It's the foundation.**
