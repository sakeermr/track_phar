# 🚀 Quick Start Guide - Integrated Pipeline

## Get Started in 5 Minutes!

### Step 1: Prepare Your Input File

Create `input/input_chemicals.csv` with your cannabinoids:

```csv
Name,SMILES,Plant,Category
THC,CCCCCC1=CC(=C2[C@@H]3C=C(CC[C@H]3C(OC2=C1)(C)C)C)O,Cannabis sativa,Cannabinoid
CBD,CCCCCC1=CC(=C(C(=C1)O)[C@@H]2C=C(CC[C@H]2C(=C)C)C)O,Cannabis sativa,Cannabinoid
```

**Or use the template:**
```bash
cp input/input_chemicals_template.csv input/my_chemicals.csv
# Edit my_chemicals.csv with your compounds
```

### Step 2: Run the Pipeline

**Via GitHub Actions (Easiest):**

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **"Integrated Trac-PharmacoNet Pipeline"**
4. Click **"Run workflow"** button
5. Configure:
   - Input file: `my_chemicals.csv`
   - Top targets: `10`
   - CUDA: Leave unchecked unless you have GPU
6. Click **"Run workflow"**

**Expected Runtime:** 1-2 hours for 8 chemicals

### Step 3: Monitor Progress

Watch the workflow progress through 5 stages:

```
✅ Stage 1: Trac Screening           (~5 min)
✅ Stage 2: PDB Extraction           (~1 min)
✅ Stage 3: PharmacoNet Modeling     (~45 min)
✅ Stage 4: Reverse Screening        (~15 min)
✅ Stage 5: Report Generation        (~2 min)
```

### Step 4: Download Results

Once complete, download these artifacts:

1. **complete-pipeline-results-XXX** ← Download this!
   - Contains everything in organized folders

Inside you'll find:

```
📁 complete-pipeline-results/
├── 📁 logs/                          ← Processing logs
├── 📁 pharmacophore-models/          ← .pm and .pse files
├── 📁 screening-results/             ← Interaction scores
├── 📄 FINAL_INTEGRATED_REPORT.txt    ← Read this first!
├── 📄 integrated_summary.csv         ← All data combined
└── 📄 top_50_hits.csv                ← Best results
```

### Step 5: Analyze Results

**Priority Files to Check:**

1. **`FINAL_INTEGRATED_REPORT.txt`**
   - Complete overview
   - Top 20 hits highlighted
   - Per-chemical summaries

2. **`top_50_hits.csv`**
   - Ranked by combined score
   - Includes both Trac and PharmacoNet scores

3. **`per_chemical/` folder**
   - Individual CSV for each chemical
   - All targets ranked by score

## 📊 Understanding Your Results

### Example Top Hit:
```
Rank: 1
Chemical: THC
PDB ID: 9PLJ
Tanimoto Score: 1.0000 (perfect match!)
PharmacoNet Score: 0.9875 (excellent binding)
Combined Rank: 1
```

**What this means:**
- THC shows perfect structural similarity to a ligand in PDB 9PLJ
- Pharmacophore modeling predicts strong binding
- This is your #1 candidate for further investigation!

### Score Interpretation:

**Tanimoto Score (Molecular Similarity):**
- 1.0 = Identical structure
- 0.7-1.0 = Very similar
- 0.5-0.7 = Moderately similar
- <0.5 = Different structures

**PharmacoNet Score (Binding Prediction):**
- Higher = Better predicted binding
- Based on pharmacophore feature matching

## 🎯 What To Do Next

### Immediate Actions:
1. ✅ Review top 10-20 hits
2. ✅ Check organism (Homo sapiens preferred)
3. ✅ Look up PDB IDs on RCSB PDB database
4. ✅ Visualize models in PyMOL using .pse files

### Further Validation:
1. 🔬 Molecular docking with AutoDock Vina
2. 🧪 Molecular dynamics simulations
3. 📚 Literature review of PDB targets
4. 🧬 Experimental validation planning

## 💡 Tips & Tricks

### Get Better Results:
- **Use 15-20 targets** per chemical for comprehensive coverage
- **Enable CUDA** if you have a GPU (10x faster!)
- **Run multiple times** with different parameters

### Visualize Pharmacophore Models:
```bash
# Install PyMOL
conda install pymol-open-source

# Open model
pymol pharmacophore-models/9PLJ_model.pse
```

### Filter Results:
```python
import pandas as pd

# Load results
df = pd.read_csv('top_50_hits.csv')

# Filter for human targets only
human = df[df['organism'].str.contains('Homo sapiens')]

# Filter by high scores
high_score = df[
    (df['tanimoto_score'] > 0.7) & 
    (df['pharmaconet_score'] > 0.5)
]
```

## 🆘 Need Help?

### Common Questions:

**Q: How long does it take?**
A: ~1-2 hours for 8 chemicals with 10 targets each

**Q: Can I run more chemicals?**
A: Yes! Up to 100 chemicals recommended

**Q: What if a stage fails?**
A: Check the logs in the artifacts. Most failures are due to:
- Invalid SMILES strings
- Network issues (PDB download)
- Memory limitations

**Q: Can I customize parameters?**
A: Yes! Edit `.github/workflows/integrated_pipeline.yml`

### Still Stuck?

1. Check workflow logs in GitHub Actions
2. Download the `logs/` artifact
3. Look for error messages in JSON files
4. Open a GitHub issue with:
   - Error message
   - Input file
   - Workflow run number

## 🎉 Success Checklist

- [ ] Input file prepared
- [ ] Workflow triggered successfully
- [ ] All 5 stages completed ✅
- [ ] Artifacts downloaded
- [ ] Results reviewed
- [ ] Top hits identified
- [ ] Next steps planned

**Ready to discover new cannabinoid-protein interactions!** 🧬🔬

---

*For detailed documentation, see `INTEGRATED_PIPELINE_README.md`*
