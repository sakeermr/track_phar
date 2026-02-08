#!/usr/bin/env python3
"""
Reverse Screening with PharmacoNet
Screen chemical library against all pharmacophore models
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import pandas as pd
from datetime import datetime
import concurrent.futures
from tqdm import tqdm


try:
    from pmnet import PharmacophoreModel
except ImportError:
    print("❌ Error: PharmacoNet not installed")
    print("Run: pip install git+https://github.com/SeonghwanSeo/PharmacoNet.git")
    sys.exit(1)


class ReverseScreener:
    """Handle reverse screening of chemicals against pharmacophore models"""
    
    def __init__(self, models_dir: Path, output_dir: Path, log_dir: Path, n_cpus: int = 4):
        self.models_dir = models_dir
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.n_cpus = n_cpus
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.models = {}
        self.chemicals = []
    
    def load_pharmacophore_models(self):
        """Load all pharmacophore models from directory"""
        print("\n📦 Loading pharmacophore models...")
        
        model_files = list(self.models_dir.glob("**/*.pm"))
        
        if not model_files:
            print(f"❌ No .pm model files found in {self.models_dir}")
            return False
        
        print(f"Found {len(model_files)} pharmacophore models")
        
        for model_file in tqdm(model_files, desc="Loading models"):
            try:
                pdb_id = model_file.stem.split('_')[0]  # Extract PDB ID from filename
                model = PharmacophoreModel.load(str(model_file))
                self.models[pdb_id] = {
                    'model': model,
                    'file': model_file,
                }
                
            except Exception as e:
                print(f"⚠️ Warning: Failed to load {model_file.name}: {str(e)}")
        
        print(f"✅ Successfully loaded {len(self.models)} models")
        return len(self.models) > 0
    
    def load_chemicals(self, chemicals_file: Path) -> bool:
        """
        Load chemical library from CSV file
        
        Args:
            chemicals_file: CSV file with columns: Name, SMILES, Plant, Category
        
        Returns:
            True if successful
        """
        print("\n📦 Loading chemical library...")
        
        try:
            df = pd.read_csv(chemicals_file)
            
            # Validate required columns
            required_cols = ['Name', 'SMILES']
            if not all(col in df.columns for col in required_cols):
                print(f"❌ Error: CSV must contain {required_cols}")
                return False
            
            self.chemicals = df.to_dict('records')
            print(f"✅ Loaded {len(self.chemicals)} chemicals")
            
            # Display chemical names
            for i, chem in enumerate(self.chemicals, 1):
                print(f"   {i}. {chem['Name']}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error loading chemicals: {str(e)}")
            return False
    
    def screen_chemical_against_model(self, chemical: dict, pdb_id: str) -> dict:
        """
        Screen a single chemical against a pharmacophore model
        
        Args:
            chemical: Dictionary with Name, SMILES, etc.
            pdb_id: PDB identifier for the model
        
        Returns:
            Dictionary with screening results
        """
        result = {
            'chemical_name': chemical['Name'],
            'pdb_id': pdb_id,
            'smiles': chemical['SMILES'],
        }
        
        try:
            model_info = self.models[pdb_id]
            model = model_info['model']
            
            # Score the chemical (with conformer generation)
            score = model.scoring_smiles(chemical['SMILES'], num_conf=10)
            
            result['score'] = score
            result['status'] = 'success'
        
        except Exception as e:
            result['score'] = None
            result['status'] = 'failed'
            result['error'] = str(e)
        
        return result
    
    def screen_all(self):
        """Screen all chemicals against all models"""
        print("\n🎯 Starting reverse screening...")
        print(f"   Chemicals: {len(self.chemicals)}")
        print(f"   Models: {len(self.models)}")
        print(f"   Total screenings: {len(self.chemicals) * len(self.models)}")
        print(f"   CPUs: {self.n_cpus}")
        
        all_results = []
        
        # Create screening tasks
        tasks = []
        for chemical in self.chemicals:
            for pdb_id in self.models.keys():
                tasks.append((chemical, pdb_id))
        
        # Parallel screening
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.n_cpus) as executor:
            futures = {
                executor.submit(self.screen_chemical_against_model, chem, pdb): (chem, pdb)
                for chem, pdb in tasks
            }
            
            for future in tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Screening progress"
            ):
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    chem, pdb = futures[future]
                    print(f"\n⚠️ Error screening {chem['Name']} vs {pdb}: {str(e)}")
        
        return all_results
    
    def save_results(self, results: List[dict]):
        """
        Save screening results to CSV files
        
        Args:
            results: List of screening result dictionaries
        """
        print("\n💾 Saving results...")
        
        # Create main results DataFrame
        df = pd.DataFrame(results)
        
        # Save master results
        master_file = self.output_dir / "master_screening_results.csv"
        df.to_csv(master_file, index=False)
        print(f"✅ Saved master results: {master_file}")
        
        # Save per-chemical results
        per_chem_dir = self.output_dir / "per_chemical"
        per_chem_dir.mkdir(exist_ok=True)
        
        for chemical_name in df['chemical_name'].unique():
            chem_df = df[df['chemical_name'] == chemical_name].copy()
            chem_df = chem_df.sort_values('score', ascending=False, na_position='last')
            
            safe_name = chemical_name.replace('/', '_').replace(' ', '_')
            chem_file = per_chem_dir / f"{safe_name}_results.csv"
            chem_df.to_csv(chem_file, index=False)
        
        print(f"✅ Saved {len(df['chemical_name'].unique())} per-chemical files")
        
        # Save per-PDB results
        per_pdb_dir = self.output_dir / "per_pdb"
        per_pdb_dir.mkdir(exist_ok=True)
        
        for pdb_id in df['pdb_id'].unique():
            pdb_df = df[df['pdb_id'] == pdb_id].copy()
            pdb_df = pdb_df.sort_values('score', ascending=False, na_position='last')
            
            pdb_file = per_pdb_dir / f"{pdb_id}_results.csv"
            pdb_df.to_csv(pdb_file, index=False)
        
        print(f"✅ Saved {len(df['pdb_id'].unique())} per-PDB files")
        
        # Generate summary statistics
        self.generate_statistics(df)
    
    def generate_statistics(self, df: pd.DataFrame):
        """Generate and save screening statistics"""
        
        stats = {
            'total_screenings': len(df),
            'total_chemicals': df['chemical_name'].nunique(),
            'total_models': df['pdb_id'].nunique(),
            'successful_screenings': (df['status'] == 'success').sum(),
            'failed_screenings': (df['status'] == 'failed').sum(),
            'success_rate': (df['status'] == 'success').sum() / len(df) * 100,
        }
        
        # Score statistics (only successful screenings)
        successful_df = df[df['status'] == 'success']
        if len(successful_df) > 0:
            stats['mean_score'] = successful_df['score'].mean()
            stats['median_score'] = successful_df['score'].median()
            stats['max_score'] = successful_df['score'].max()
            stats['min_score'] = successful_df['score'].min()
            stats['std_score'] = successful_df['score'].std()
        
        # Save statistics
        stats_file = self.output_dir / "screening_statistics.json"
        import json
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Display statistics
        print("\n" + "="*80)
        print("📊 SCREENING STATISTICS")
        print("="*80)
        print(f"Total screenings: {stats['total_screenings']}")
        print(f"Chemicals: {stats['total_chemicals']}")
        print(f"Models: {stats['total_models']}")
        print(f"✅ Successful: {stats['successful_screenings']}")
        print(f"❌ Failed: {stats['failed_screenings']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        if 'mean_score' in stats:
            print(f"\nScore Statistics:")
            print(f"  Mean: {stats['mean_score']:.4f}")
            print(f"  Median: {stats['median_score']:.4f}")
            print(f"  Range: {stats['min_score']:.4f} - {stats['max_score']:.4f}")
            print(f"  Std Dev: {stats['std_score']:.4f}")
        
        print("="*80)
        
        # Find top hits
        if len(successful_df) > 0:
            print("\n🏆 TOP 10 HITS (Highest Scores):")
            top_hits = successful_df.nlargest(10, 'score')
            for i, row in enumerate(top_hits.itertuples(), 1):
                print(f"  {i}. {row.chemical_name} vs {row.pdb_id}: {row.score:.4f}")


def main():
    parser = argparse.ArgumentParser(
        description='Reverse screening with PharmacoNet'
    )
    parser.add_argument(
        '--models_dir',
        type=Path,
        required=True,
        help='Directory containing pharmacophore models (.pm files)'
    )
    parser.add_argument(
        '--chemicals_file',
        type=Path,
        required=True,
        help='CSV file with chemical library (columns: Name, SMILES)'
    )
    parser.add_argument(
        '--output_dir',
        type=Path,
        required=True,
        help='Output directory for screening results'
    )
    parser.add_argument(
        '--log_dir',
        type=Path,
        required=True,
        help='Output directory for logs'
    )
    parser.add_argument(
        '--cpus',
        type=int,
        default=4,
        help='Number of CPUs for parallel screening (default: 4)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🎯 PharmacoNet Reverse Screening")
    print("="*80)
    
    # Initialize screener
    screener = ReverseScreener(
        args.models_dir,
        args.output_dir,
        args.log_dir,
        args.cpus
    )
    
    # Load models
    if not screener.load_pharmacophore_models():
        return 1
    
    # Load chemicals
    if not screener.load_chemicals(args.chemicals_file):
        return 1
    
    # Run screening
    results = screener.screen_all()
    
    # Save results
    screener.save_results(results)
    
    print("\n🎉 Reverse screening complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
