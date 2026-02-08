#!/usr/bin/env python3
"""
Batch Pharmacophore Modeling with PharmacoNet
Processes multiple PDB IDs in parallel batches for pharmacophore generation
"""

import argparse
import sys
from pathlib import Path
from typing import List
import subprocess
import json
from datetime import datetime


class BatchModeler:
    """Handle batch pharmacophore modeling for multiple PDB structures"""
    
    def __init__(self, output_dir: Path, log_dir: Path, cuda: bool = False):
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.cuda = cuda
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def load_pdb_list(self, pdb_file: Path, batch_num: int, total_batches: int) -> List[str]:
        """
        Load PDB list and return subset for this batch
        
        Args:
            pdb_file: File containing PDB IDs (one per line)
            batch_num: Current batch number (1-indexed)
            total_batches: Total number of batches
        
        Returns:
            List of PDB IDs for this batch
        """
        with open(pdb_file, 'r') as f:
            all_pdbs = [line.strip() for line in f if line.strip()]
        
        # Calculate batch size and range
        batch_size = len(all_pdbs) // total_batches + (1 if len(all_pdbs) % total_batches else 0)
        start_idx = (batch_num - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(all_pdbs))
        
        batch_pdbs = all_pdbs[start_idx:end_idx]
        
        print(f"📦 Batch {batch_num}/{total_batches}: {len(batch_pdbs)} PDB IDs")
        print(f"   Range: {start_idx+1} to {end_idx} of {len(all_pdbs)} total")
        
        return batch_pdbs
    
    def model_single_pdb(self, pdb_id: str) -> dict:
        """
        Run pharmacophore modeling for a single PDB
        
        Args:
            pdb_id: PDB identifier
        
        Returns:
            Dictionary with modeling results
        """
        print(f"\n🔬 Modeling {pdb_id}...")
        
        result = {
            'pdb_id': pdb_id,
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
        }
        
        try:
            # Build modeling command
            cmd = [
                'python', 'modeling.py',
                '--pdb', pdb_id,
                '--prefix', pdb_id,
            ]
            
            if self.cuda:
                cmd.append('--cuda')
            
            # Run modeling
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per PDB
            )
            
            if process.returncode == 0:
                result['status'] = 'success'
                result['stdout'] = process.stdout
                
                # Check if model file was created
                model_file = self.output_dir / f"{pdb_id}_model.pm"
                if model_file.exists():
                    result['model_file'] = str(model_file)
                    print(f"   ✅ Model saved: {model_file.name}")
                else:
                    result['status'] = 'no_model'
                    result['error'] = 'Model file not created'
                    print(f"   ⚠️ Warning: Model file not found")
            
            else:
                result['status'] = 'failed'
                result['error'] = process.stderr
                print(f"   ❌ Failed: {process.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['error'] = 'Modeling timeout (10 minutes)'
            print(f"   ⏱️ Timeout: Exceeded 10 minutes")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"   ❌ Error: {str(e)}")
        
        # Save individual log
        log_file = self.log_dir / f"{pdb_id}_modeling.json"
        with open(log_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
    
    def process_batch(self, pdb_ids: List[str]) -> dict:
        """
        Process a batch of PDB IDs
        
        Args:
            pdb_ids: List of PDB identifiers
        
        Returns:
            Dictionary with batch statistics
        """
        results = []
        stats = {
            'total': len(pdb_ids),
            'success': 0,
            'failed': 0,
            'timeout': 0,
            'error': 0,
        }
        
        for i, pdb_id in enumerate(pdb_ids, 1):
            print(f"\n{'='*80}")
            print(f"Progress: {i}/{len(pdb_ids)} ({i/len(pdb_ids)*100:.1f}%)")
            
            result = self.model_single_pdb(pdb_id)
            results.append(result)
            
            # Update statistics
            stats[result['status']] += 1
        
        # Save batch summary
        summary = {
            'statistics': stats,
            'results': results,
            'timestamp': datetime.now().isoformat(),
        }
        
        summary_file = self.log_dir / f"batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description='Batch pharmacophore modeling with PharmacoNet'
    )
    parser.add_argument(
        '--pdb_list',
        type=Path,
        required=True,
        help='File containing PDB IDs (one per line)'
    )
    parser.add_argument(
        '--batch_num',
        type=int,
        required=True,
        help='Current batch number (1-indexed)'
    )
    parser.add_argument(
        '--total_batches',
        type=int,
        required=True,
        help='Total number of batches'
    )
    parser.add_argument(
        '--output_dir',
        type=Path,
        required=True,
        help='Output directory for pharmacophore models'
    )
    parser.add_argument(
        '--log_dir',
        type=Path,
        required=True,
        help='Output directory for logs'
    )
    parser.add_argument(
        '--cuda',
        action='store_true',
        help='Enable CUDA acceleration'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🔬 PharmacoNet Batch Pharmacophore Modeling")
    print("="*80)
    print(f"Batch: {args.batch_num}/{args.total_batches}")
    print(f"CUDA: {'Enabled' if args.cuda else 'Disabled'}")
    print(f"Output: {args.output_dir}")
    print("="*80)
    
    # Initialize modeler
    modeler = BatchModeler(args.output_dir, args.log_dir, args.cuda)
    
    # Load PDB IDs for this batch
    pdb_ids = modeler.load_pdb_list(args.pdb_list, args.batch_num, args.total_batches)
    
    if not pdb_ids:
        print("⚠️ No PDB IDs to process in this batch")
        return 0
    
    # Process batch
    stats = modeler.process_batch(pdb_ids)
    
    # Display final statistics
    print("\n" + "="*80)
    print("📊 BATCH MODELING STATISTICS")
    print("="*80)
    print(f"Total PDBs: {stats['total']}")
    print(f"✅ Successful: {stats['success']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏱️ Timeout: {stats['timeout']}")
    print(f"⚠️ Errors: {stats['error']}")
    print(f"Success Rate: {stats['success']/stats['total']*100:.1f}%")
    print("="*80)
    
    print("\n🎉 Batch modeling complete!")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
