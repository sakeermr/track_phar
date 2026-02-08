# 🔧 Workflow Troubleshooting Guide

## Common Errors and Solutions

### ❌ Error 1: "No file matched to requirements.txt"

**Full Error:**
```
No file in /home/runner/work/track_phar/track_phar matched to 
[**/requirements.txt or **/pyproject.toml], make sure you have 
checked out the target repository
```

**Cause:**  
The workflow is trying to cache pip dependencies but can't find `requirements.txt`.

**Solutions:**

#### ✅ Solution A: Use Fixed Workflow (Recommended)
Replace your workflow file with `integrated_pipeline_FIXED.yml`:
- Removed pip caching requirement
- Added file verification step
- Better error handling

```bash
# In your repository
cp integrated_pipeline_FIXED.yml .github/workflows/integrated_pipeline.yml
git add .github/workflows/integrated_pipeline.yml
git commit -m "Fix pip cache error"
git push
```

#### ✅ Solution B: Add requirements.txt
Add `requirements.txt` to your repository root:

```bash
# Copy the provided requirements.txt to your repo root
cp requirements.txt /path/to/your/repo/
git add requirements.txt
git commit -m "Add requirements.txt for pip caching"
git push
```

---

### ❌ Error 2: "pdb_ligands.csv not found"

**Error:**
```
FileNotFoundError: pdb_ligands.csv
```

**Solution:**
Ensure `pdb_ligands.csv` is in your repository root:

```bash
# Check if file exists
ls -lh pdb_ligands.csv

# If missing, copy from Trac repo
cp /path/to/Trac/pdb_ligands.csv .

# If file is > 100MB, use Git LFS
git lfs install
git lfs track "pdb_ligands.csv"
git add .gitattributes pdb_ligands.csv
git commit -m "Add PDB ligand database"
git push
```

---

### ❌ Error 3: "final_optimized_workflow.py not found"

**Error:**
```
python: can't open file 'final_optimized_workflow.py'
```

**Solution:**
Ensure the Trac screening script exists:

```bash
# Verify file exists
ls -lh final_optimized_workflow.py

# If missing, copy from Trac repo
cp /path/to/Trac/final_optimized_workflow.py .
git add final_optimized_workflow.py
git commit -m "Add Trac screening script"
git push
```

---

### ❌ Error 4: "Input file not found"

**Error:**
```
FileNotFoundError: input/input_chemicals.csv
```

**Solution:**
Ensure input file exists in `input/` directory:

```bash
# Create input directory if needed
mkdir -p input

# Copy or create input file
cp input_chemicals_template.csv input/input_chemicals.csv

# Or create your own
nano input/my_chemicals.csv

git add input/
git commit -m "Add input chemicals file"
git push
```

---

### ❌ Error 5: "Module 'rdkit' not found"

**Error:**
```
ModuleNotFoundError: No module named 'rdkit'
```

**Solution:**
This should be handled by the workflow automatically. If it persists:

1. Check the workflow install step runs successfully
2. Verify internet connectivity in GitHub Actions
3. Try re-running the workflow

---

### ❌ Error 6: "Permission denied: pharmaconet_input/"

**Error:**
```
Permission denied: Cannot create directory 'pharmaconet_input/'
```

**Solution:**
Add directory creation to workflow:

```yaml
- name: 📁 Create Output Directories
  run: |
    mkdir -p output pharmaconet_input logs pharmacophore_models screening_results
```

---

### ❌ Error 7: PharmacoNet checkout fails

**Error:**
```
Repository not found: sakeermr/Tracmypdb_pharmaconet_new
```

**Solutions:**

1. **If repository is private:**
   - Make it public, OR
   - Add GitHub token to workflow

2. **If repository name changed:**
   - Update workflow with correct repo name

---

### ❌ Error 8: Conda environment fails

**Error:**
```
CondaError: Could not install packages
```

**Solution:**
Try alternative conda channels:

```yaml
- name: 🐍 Setup Conda
  uses: conda-incubator/setup-miniconda@v3
  with:
    python-version: '3.11'
    channels: conda-forge,bioconda,defaults
    channel-priority: flexible
```

---

## 🔍 General Debugging Steps

### 1. Check File Structure
```bash
# Your repo should have:
.
├── .github/workflows/integrated_pipeline.yml
├── scripts/
│   ├── extract_top_pdbs.py
│   ├── batch_modeling_parallel.py
│   ├── reverse_screening_batch.py
│   └── generate_summary_report.py
├── input/
│   └── input_chemicals.csv
├── pdb_ligands.csv
├── final_optimized_workflow.py
└── requirements.txt (optional)
```

### 2. Verify Workflow Syntax
```bash
# Use GitHub's workflow validator
# Go to: Actions → Select workflow → Edit → Check for errors
```

### 3. Enable Workflow Debug Logging
Add to workflow file:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### 4. Test Locally First
```bash
# Test Trac screening locally
python final_optimized_workflow.py \
  --input input/input_chemicals.csv \
  --output output/test_results.txt

# Test PDB extraction
python scripts/extract_top_pdbs.py \
  --input output/test_results.txt \
  --output pdb_list.txt \
  --top_n 10
```

---

## 📊 Pre-Flight Checklist

Before running the workflow, verify:

- [ ] `pdb_ligands.csv` exists in root (50-200 MB)
- [ ] `final_optimized_workflow.py` exists in root
- [ ] `input/input_chemicals.csv` exists with valid SMILES
- [ ] All scripts in `scripts/` directory
- [ ] `requirements.txt` exists (or use fixed workflow)
- [ ] GitHub Actions enabled in repository settings
- [ ] Sufficient GitHub Actions minutes available
- [ ] Repository is public (or PharmacoNet access configured)

---

## 🆘 Still Having Issues?

### Check Workflow Logs
1. Go to Actions tab
2. Click on failed run
3. Click on failed job
4. Expand each step to see detailed logs

### Look for Specific Errors
- **Import errors** → Dependency installation failed
- **File not found** → Missing required files
- **Permission errors** → Directory creation issues
- **Network errors** → GitHub/PyPI connectivity

### Common Log Patterns

**Good:**
```
✅ Screening completed! Found 80 PDB targets
```

**Bad:**
```
❌ Error: FileNotFoundError: pdb_ligands.csv
```

---

## 💡 Quick Fixes Summary

| Error | Quick Fix |
|-------|-----------|
| requirements.txt missing | Use `integrated_pipeline_FIXED.yml` |
| pdb_ligands.csv missing | Copy from Trac repo to root |
| Input file missing | Add to `input/` directory |
| Scripts missing | Copy all `.py` files to `scripts/` |
| Workflow syntax error | Use GitHub editor validator |
| Conda install fails | Check channel configuration |
| Permission denied | Add directory creation steps |

---

## 📞 Getting Help

If you're still stuck:

1. **Check the error message carefully**
   - Read the full error, not just the first line
   - Note which stage failed

2. **Review the logs**
   - Download artifacts if available
   - Check logs/ directory for details

3. **Verify file locations**
   - Use the file verification step in fixed workflow
   - Ensure all paths are correct

4. **Test components individually**
   - Run Trac screening alone first
   - Then test PDB extraction
   - Build up to full pipeline

---

**Most Common Solution:**  
Use `integrated_pipeline_FIXED.yml` - it solves 90% of initial setup issues!
