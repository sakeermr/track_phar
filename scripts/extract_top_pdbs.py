#!/usr/bin/env python3
"""
Extract Top PDB Targets from Trac Screening Results
Extracts the top N PDB IDs for each chemical compound from Trac analysis
"""

import argparse
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


def parse_trac_results(input_file: Path, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
    """
    Parse Trac screening results and extract top N PDB IDs per chemical
    
    Args:
        input_file: Path to Trac screening results
        top_n: Number of top targets to extract per chemical
    
    Returns:
        Dictionary mapping chemical names to list of (PDB_ID, Tanimoto_score) tuples
    """
    results = {}
    current_molecule = None
    current_targets = []
    
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Detect molecule header
            if line.startswith('MOLECULE:'):
                # Save previous molecule's data
                if current_molecule and current_targets:
                    results[current_molecule] = current_targets[:top_n]
                
                # Extract molecule name
                current_molecule = line.split('MOLECULE:')[1].strip()
                current_targets = []
                print(f"📋 Processing: {current_molecule}")
            
            # Parse PDB target lines
            elif current_molecule and line and not line.startswith('-') and not line.startswith('Rank'):
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        rank = int(parts[0])
                        pdb_id = parts[1]
                        tanimoto = float(parts[2])
                        
                        # Validate PDB ID format (4 characters)
                        if len(pdb_id) == 4 and pdb_id.isalnum():
                            current_targets.append((pdb_id, tanimoto))
                    except (ValueError, IndexError):
                        continue
    
    # Save last molecule
    if current_molecule and current_targets:
        results[current_molecule] = current_targets[:top_n]
    
    return results


def write_pdb_list(results: Dict[str, List[Tuple[str, float]]], output_file: Path):
    """
    Write unique PDB IDs to file (one per line)
    
    Args:
        results: Dictionary of chemical -> [(PDB_ID, score), ...]
        output_file: Output file path
    """
    # Collect all unique PDB IDs
    all_pdbs = set()
    for targets in results.values():
        for pdb_id, score in targets:
            all_pdbs.add(pdb_id)
    
    # Sort for consistent ordering
    sorted_pdbs = sorted(all_pdbs)
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        for pdb_id in sorted_pdbs:
            f.write(f"{pdb_id}\n")
    
    print(f"\n✅ Wrote {len(sorted_pdbs)} unique PDB IDs to {output_file}")


def write_detailed_mapping(results: Dict[str, List[Tuple[str, float]]], output_dir: Path):
    """
    Write detailed chemical-to-PDB mapping
    
    Args:
        results: Dictionary of chemical -> [(PDB_ID, score), ...]
        output_dir: Output directory path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping_file = output_dir / "chemical_pdb_mapping.csv"
    
    with open(mapping_file, 'w') as f:
        f.write("Chemical,PDB_ID,Tanimoto_Score,Rank\n")
        
        for chemical, targets in results.items():
            for rank, (pdb_id, score) in enumerate(targets, 1):
                f.write(f"{chemical},{pdb_id},{score:.4f},{rank}\n")
    
    print(f"✅ Wrote detailed mapping to {mapping_file}")


def generate_statistics(results: Dict[str, List[Tuple[str, float]]]) -> Dict:
    """
    Generate statistics about extracted PDB targets
    
    Args:
        results: Dictionary of chemical -> [(PDB_ID, score), ...]
    
    Returns:
        Dictionary with statistics
    """
    all_pdbs = set()
    total_entries = 0
    scores = []
    
    for targets in results.values():
        total_entries += len(targets)
        for pdb_id, score in targets:
            all_pdbs.add(pdb_id)
            scores.append(score)
    
    stats = {
        'total_chemicals': len(results),
        'total_entries': total_entries,
        'unique_pdbs': len(all_pdbs),
        'avg_score': sum(scores) / len(scores) if scores else 0,
        'max_score': max(scores) if scores else 0,
        'min_score': min(scores) if scores else 0,
    }
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Extract top PDB targets from Trac screening results'
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input Trac screening results file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output PDB list file'
    )
    parser.add_argument(
        '--top_n',
        type=int,
        default=10,
        help='Number of top targets per chemical (default: 10)'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Generate detailed chemical-PDB mapping CSV'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🔍 Extracting Top PDB Targets from Trac Results")
    print("="*80)
    
    # Parse results
    print(f"\n📖 Reading: {args.input}")
    results = parse_trac_results(args.input, args.top_n)
    
    if not results:
        print("❌ No results found in input file!")
        return 1
    
    # Write PDB list
    write_pdb_list(results, args.output)
    
    # Write detailed mapping if requested
    if args.detailed:
        write_detailed_mapping(results, args.output.parent)
    
    # Generate and display statistics
    stats = generate_statistics(results)
    
    print("\n" + "="*80)
    print("📊 EXTRACTION STATISTICS")
    print("="*80)
    print(f"Total chemicals processed: {stats['total_chemicals']}")
    print(f"Total PDB entries extracted: {stats['total_entries']}")
    print(f"Unique PDB IDs: {stats['unique_pdbs']}")
    print(f"Average Tanimoto score: {stats['avg_score']:.4f}")
    print(f"Score range: {stats['min_score']:.4f} - {stats['max_score']:.4f}")
    print("="*80)
    
    # List all chemicals processed
    print("\n✅ Chemicals Processed:")
    for i, chemical in enumerate(results.keys(), 1):
        print(f"  {i}. {chemical} ({len(results[chemical])} targets)")
    
    print("\n🎉 Extraction complete!")
    return 0


if __name__ == '__main__':
    exit(main())
