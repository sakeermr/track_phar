# 🧬 Integrated Trac-PharmacoNet Drug Discovery Pipeline

**Complete automated workflow combining Trac PDB screening with PharmacoNet pharmacophore modeling**

## 🎯 Overview

This integrated pipeline combines two powerful drug discovery tools:

1. **Trac** - PDB ligand similarity screening to identify potential protein targets
2. **PharmacoNet** - Deep learning-guided pharmacophore modeling and reverse screening

### Pipeline Flow

```
📥 Input Chemicals (SMILES)
    ↓
🎯 Stage 1: Trac PDB Screening
    ↓ (Top 10 PDB targets per chemical)
📋 Stage 2: PDB Extraction
    ↓ (Unique PDB list)
🔬 Stage 3: PharmacoNet Modeling
    ↓ (Pharmacophore models)
🔄 Stage 4: Reverse Screening
    ↓ (Interaction scores)
📊 Stage 5: Integrated Report
    ↓
✅ Final Results Package
```

## 📦 Output Structure

The pipeline generates three main artifact categories:

### 1. **logs/** - Processing Logs
```
logs/
├── modeling/
│   ├── 9PLJ_modeling.json
│   ├── 6MP4_modeling.json
│   └── batch_summary.json
└── screening/
    ├── screening_summary.log
    └── individual_screenings/
```

### 2. **pharmacophore-models/** - Pharmacophore Models
```
pharmacophore-models/
├── 9PLJ_model.pm          # Pharmacophore model
├── 9PLJ_model.pse         # PyMOL visualization
├── 6MP4_model.pm
├── 6MP4_model.pse
└── ... (all PDB models)
```

### 3. **screening-results/** - Screening Data
```
screening-results/
├── master_screening_results.csv
├── per_chemical/
│   ├── THC_results.csv
│   ├── CBD_results.csv
│   └── ...
├── per_pdb/
│   ├── 9PLJ_results.csv
│   ├── 6MP4_results.csv
│   └── ...
└── screening_statistics.json
```

### 4. **Final Reports**
```
final_report/
├── FINAL_INTEGRATED_REPORT.txt
├── integrated_summary.csv
└── top_50_hits.csv
```

## 🚀 Usage

### Option 1: GitHub Actions (Recommended)

1. **Push your input file** to `input/input_chemicals.csv`

2. **Trigger the workflow**:
   - Go to Actions tab
   - Select "Integrated Trac-PharmacoNet Pipeline"
   - Click "Run workflow"
   - Configure options:
     - Input file name
     - Number of targets per chemical (5/10/15/20)
     - Enable CUDA (optional)

3. **Download results**:
   - Wait for workflow to complete (~1-2 hours)
   - Download artifacts from workflow run

### Option 2: Manual Execution

Run each stage sequentially:

```bash
# Stage 1: Trac Screening
python final_optimized_workflow.py \
  --input input/input_chemicals.csv \
  --output output/trac_screening_results.txt

# Stage 2: Extract PDB IDs
python scripts/extract_top_pdbs.py \
  --input output/trac_screening_results.txt \
  --output pharmaconet_input/pdb_list.txt \
  --top_n 10

# Stage 3: PharmacoNet Modeling
python scripts/batch_modeling_parallel.py \
  --pdb_list pharmaconet_input/pdb_list.txt \
  --batch_num 1 \
  --total_batches 1 \
  --output_dir pharmacophore_models/ \
  --log_dir logs/modeling/

# Stage 4: Reverse Screening
python scripts/reverse_screening_batch.py \
  --models_dir pharmacophore_models/ \
  --chemicals_file input/input_chemicals.csv \
  --output_dir screening_results/ \
  --log_dir logs/screening/ \
  --cpus 4

# Stage 5: Generate Report
python scripts/generate_summary_report.py \
  --trac_results output/trac_screening_results.txt \
  --screening_results screening_results/ \
  --output final_report/
```

## 📊 Input Format

### Input Chemicals CSV
```csv
Name,SMILES,Plant,Category
THC,CCCCCC1=CC(=C2[C@@H]3C=C(CC[C@H]3C(OC2=C1)(C)C)C)O,Cannabis sativa,Cannabinoid
CBD,CCCCCC1=CC(=C(C(=C1)O)[C@@H]2C=C(CC[C@H]2C(=C)C)C)O,Cannabis sativa,Cannabinoid
```

**Required columns:**
- `Name` - Chemical name
- `SMILES` - SMILES string
- `Plant` - Source plant (optional)
- `Category` - Chemical category (optional)

## 📈 Understanding Results

### 1. Trac Screening Results
- **Tanimoto Score**: Molecular similarity (0-1)
  - 1.0 = Perfect match
  - >0.7 = High similarity
  - 0.3-0.7 = Moderate similarity

### 2. PharmacoNet Scores
- **Pharmacophore Score**: Binding potential
  - Higher = Better predicted binding
  - Based on pharmacophore matching

### 3. Combined Rankings
- Integrates both Tanimoto and PharmacoNet scores
- Identifies most promising chemical-target pairs

## 🔧 Configuration

### Workflow Parameters

**Input Chemicals**: Path to input CSV file
- Default: `input_chemicals.csv`

**Targets Per Chemical**: Number of top PDB targets
- Options: 5, 10, 15, 20
- Default: 10
- More targets = longer runtime but more comprehensive

**CUDA Acceleration**: Enable GPU for PharmacoNet
- Default: Disabled
- Speeds up modeling significantly if GPU available

### Advanced Configuration

Edit `.github/workflows/integrated_pipeline.yml` to customize:

- **Parallel batches**: Adjust `matrix.batch` for more/fewer parallel jobs
- **CPU allocation**: Change `--cpus` parameter
- **Timeout limits**: Modify job timeout values
- **Artifact retention**: Change `retention-days`

## 📋 Requirements

### For Trac (Stage 1)
```
python >= 3.9
rdkit
pandas
numpy
requests
tqdm
```

### For PharmacoNet (Stages 3-4)
```
python >= 3.11
torch
rdkit
biopython
omegaconf
tqdm
numba
molvoxel
pymol-open-source
```

## 🐛 Troubleshooting

### Common Issues

**1. No PDB models generated**
- Check if PDB IDs are valid
- Verify network connectivity (PDB download)
- Review modeling logs in artifacts

**2. Screening fails**
- Ensure pharmacophore models exist
- Verify SMILES strings are valid
- Check memory availability

**3. Workflow timeout**
- Reduce targets per chemical
- Enable CUDA acceleration
- Split into smaller batches

### Debug Mode

Enable verbose logging:
```bash
export DEBUG=1
python scripts/batch_modeling_parallel.py --verbose
```

## 📚 Citations

### Trac
Standard Seed Corporation - Internal Tool

### PharmacoNet
```bibtex
@article{seo2024pharmaconet,
  title={PharmacoNet: deep learning-guided pharmacophore modeling 
         for ultra-large-scale virtual screening},
  author={Seo, Seonghwan and Kim, Woo Youn},
  journal={Chemical Science},
  year={2024},
  publisher={Royal Society of Chemistry}
}
```

## 📝 License

- **Workflow Scripts**: MIT License
- **Trac**: Apache 2.0 (Internal Use Only)
- **PharmacoNet**: MIT License

## 🤝 Support

For issues or questions:
1. Check workflow logs in GitHub Actions
2. Review artifact files for error details
3. Open an issue in the repository

## 🎯 Example Results

From a typical run with 8 cannabinoids:

- **Input**: 8 chemicals
- **Trac**: 80 PDB targets identified (10 per chemical)
- **Modeling**: 80 pharmacophore models generated
- **Screening**: 640 chemical-target screenings (8 × 80)
- **Runtime**: ~1.5 hours
- **Top Hit**: THC vs 9PLJ (Score: 1.0000)

## 🔬 Next Steps

After completing the pipeline:

1. **Analyze top hits** from `top_50_hits.csv`
2. **Visualize models** using PyMOL (.pse files)
3. **Validate promising pairs** with molecular docking
4. **Conduct experimental validation** for highest-ranked targets

---

**Version**: 2.0  
**Last Updated**: 2026-02-08  
**Maintained by**: Standard Seed Corporation
