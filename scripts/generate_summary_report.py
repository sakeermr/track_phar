#!/usr/bin/env python3
"""
Generate Final Integrated Report
Combines Trac screening results with PharmacoNet reverse screening
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List


class ReportGenerator:
    """Generate comprehensive final report from integrated pipeline"""
    
    def __init__(self, trac_results: Path, screening_results_dir: Path, output_dir: Path):
        self.trac_results = trac_results
        self.screening_results_dir = screening_results_dir
        self.output_dir = output_dir
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.trac_data = None
        self.screening_data = None
    
    def load_trac_results(self) -> bool:
        """Load and parse Trac screening results"""
        print("📖 Loading Trac screening results...")
        
        try:
            # Parse Trac results into structured format
            results = {}
            current_molecule = None
            current_targets = []
            
            with open(self.trac_results, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    if line.startswith('MOLECULE:'):
                        if current_molecule:
                            results[current_molecule] = current_targets
                        current_molecule = line.split('MOLECULE:')[1].strip()
                        current_targets = []
                    
                    elif current_molecule and line and not line.startswith('-') and not line.startswith('Rank'):
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                rank = int(parts[0])
                                pdb_id = parts[1]
                                tanimoto = float(parts[2])
                                organism = ' '.join(parts[3:]).split('Yes')[0].strip()
                                
                                current_targets.append({
                                    'rank': rank,
                                    'pdb_id': pdb_id,
                                    'tanimoto_score': tanimoto,
                                    'organism': organism
                                })
                            except (ValueError, IndexError):
                                continue
                
                if current_molecule:
                    results[current_molecule] = current_targets
            
            self.trac_data = results
            print(f"✅ Loaded Trac results for {len(results)} chemicals")
            return True
        
        except Exception as e:
            print(f"❌ Error loading Trac results: {str(e)}")
            return False
    
    def load_screening_results(self) -> bool:
        """Load PharmacoNet screening results"""
        print("📖 Loading PharmacoNet screening results...")
        
        try:
            master_file = self.screening_results_dir / "master_screening_results.csv"
            
            if not master_file.exists():
                print(f"❌ Master results file not found: {master_file}")
                return False
            
            self.screening_data = pd.read_csv(master_file)
            print(f"✅ Loaded {len(self.screening_data)} screening results")
            return True
        
        except Exception as e:
            print(f"❌ Error loading screening results: {str(e)}")
            return False
    
    def generate_integrated_report(self):
        """Generate comprehensive integrated report"""
        print("\n📊 Generating integrated report...")
        
        report_lines = []
        
        # Header
        report_lines.append("=" * 100)
        report_lines.append("INTEGRATED DRUG DISCOVERY PIPELINE - FINAL REPORT")
        report_lines.append("=" * 100)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Pipeline overview
        report_lines.append("PIPELINE OVERVIEW:")
        report_lines.append("-" * 100)
        report_lines.append("Stage 1: Trac PDB Ligand Screening → Identified potential protein targets")
        report_lines.append("Stage 2: PDB Target Extraction → Selected top targets per chemical")
        report_lines.append("Stage 3: PharmacoNet Modeling → Generated pharmacophore models")
        report_lines.append("Stage 4: Reverse Screening → Screened chemicals against pharmacophores")
        report_lines.append("")
        
        # Stage 1: Trac Results Summary
        report_lines.append("=" * 100)
        report_lines.append("STAGE 1: TRAC PDB SCREENING RESULTS")
        report_lines.append("=" * 100)
        report_lines.append(f"Total Chemicals Analyzed: {len(self.trac_data)}")
        
        all_trac_pdbs = set()
        for targets in self.trac_data.values():
            for target in targets:
                all_trac_pdbs.add(target['pdb_id'])
        
        report_lines.append(f"Total Unique PDB Targets Identified: {len(all_trac_pdbs)}")
        report_lines.append("")
        
        for chemical, targets in self.trac_data.items():
            report_lines.append(f"\nChemical: {chemical}")
            report_lines.append(f"  Top Targets: {len(targets)}")
            
            if targets:
                top_3 = targets[:3]
                for target in top_3:
                    report_lines.append(
                        f"    {target['rank']}. {target['pdb_id']} "
                        f"(Tanimoto: {target['tanimoto_score']:.4f}, {target['organism']})"
                    )
        
        report_lines.append("")
        
        # Stage 4: PharmacoNet Screening Results
        report_lines.append("=" * 100)
        report_lines.append("STAGE 4: PHARMACONET REVERSE SCREENING RESULTS")
        report_lines.append("=" * 100)
        
        successful_screenings = self.screening_data[self.screening_data['status'] == 'success']
        
        report_lines.append(f"Total Screenings Performed: {len(self.screening_data)}")
        report_lines.append(f"Successful Screenings: {len(successful_screenings)}")
        report_lines.append(f"Success Rate: {len(successful_screenings)/len(self.screening_data)*100:.1f}%")
        report_lines.append("")
        
        if len(successful_screenings) > 0:
            report_lines.append("Score Statistics:")
            report_lines.append(f"  Mean Score: {successful_screenings['score'].mean():.4f}")
            report_lines.append(f"  Median Score: {successful_screenings['score'].median():.4f}")
            report_lines.append(f"  Max Score: {successful_screenings['score'].max():.4f}")
            report_lines.append(f"  Min Score: {successful_screenings['score'].min():.4f}")
            report_lines.append("")
            
            # Top hits
            report_lines.append("\n🏆 TOP 20 CHEMICAL-TARGET INTERACTIONS:")
            report_lines.append("-" * 100)
            report_lines.append(f"{'Rank':<6} {'Chemical':<35} {'PDB ID':<10} {'Score':<10} {'Status'}")
            report_lines.append("-" * 100)
            
            top_hits = successful_screenings.nlargest(20, 'score')
            for i, row in enumerate(top_hits.itertuples(), 1):
                report_lines.append(
                    f"{i:<6} {row.chemical_name[:34]:<35} {row.pdb_id:<10} "
                    f"{row.score:<10.4f} {row.status}"
                )
            
            report_lines.append("")
        
        # Per-chemical summary
        report_lines.append("\n" + "=" * 100)
        report_lines.append("PER-CHEMICAL SUMMARY")
        report_lines.append("=" * 100)
        
        for chemical in self.screening_data['chemical_name'].unique():
            chem_data = successful_screenings[successful_screenings['chemical_name'] == chemical]
            
            if len(chem_data) > 0:
                report_lines.append(f"\n{chemical}:")
                report_lines.append(f"  Targets Screened: {len(chem_data)}")
                report_lines.append(f"  Mean Score: {chem_data['score'].mean():.4f}")
                report_lines.append(f"  Best Score: {chem_data['score'].max():.4f}")
                
                best_target = chem_data.nlargest(1, 'score').iloc[0]
                report_lines.append(f"  Best Target: {best_target['pdb_id']} (Score: {best_target['score']:.4f})")
                
                # Top 5 targets
                top_5 = chem_data.nlargest(5, 'score')
                report_lines.append(f"  Top 5 Targets:")
                for i, row in enumerate(top_5.itertuples(), 1):
                    report_lines.append(f"    {i}. {row.pdb_id}: {row.score:.4f}")
        
        # Save report
        report_file = self.output_dir / "FINAL_INTEGRATED_REPORT.txt"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✅ Report saved: {report_file}")
        
        # Also save as formatted CSV
        self.generate_csv_summary()
    
    def generate_csv_summary(self):
        """Generate CSV summary combining both datasets"""
        print("📊 Generating CSV summary...")
        
        summary_data = []
        
        for chemical in self.trac_data.keys():
            # Get Trac data
            trac_targets = self.trac_data[chemical]
            
            # Get screening data
            chem_screening = self.screening_data[
                self.screening_data['chemical_name'] == chemical
            ]
            successful = chem_screening[chem_screening['status'] == 'success']
            
            # Combine information
            for target in trac_targets:
                pdb_id = target['pdb_id']
                
                # Find corresponding screening result
                screen_result = successful[successful['pdb_id'] == pdb_id]
                
                pharma_score = None
                if len(screen_result) > 0:
                    pharma_score = screen_result.iloc[0]['score']
                
                summary_data.append({
                    'chemical': chemical,
                    'pdb_id': pdb_id,
                    'trac_rank': target['rank'],
                    'tanimoto_score': target['tanimoto_score'],
                    'organism': target['organism'],
                    'pharmaconet_score': pharma_score,
                    'combined_rank': None  # Will calculate after
                })
        
        df_summary = pd.DataFrame(summary_data)
        
        # Calculate combined ranking (normalize and average scores)
        if len(df_summary) > 0:
            # Normalize Tanimoto (0-1) and PharmacoNet scores
            df_summary['tanimoto_norm'] = df_summary['tanimoto_score']
            
            if df_summary['pharmaconet_score'].notna().any():
                max_pharma = df_summary['pharmaconet_score'].max()
                min_pharma = df_summary['pharmaconet_score'].min()
                
                if max_pharma > min_pharma:
                    df_summary['pharmaconet_norm'] = (
                        (df_summary['pharmaconet_score'] - min_pharma) / 
                        (max_pharma - min_pharma)
                    )
                else:
                    df_summary['pharmaconet_norm'] = 0.5
                
                # Combined score (average of normalized scores)
                df_summary['combined_score'] = (
                    df_summary['tanimoto_norm'] + df_summary['pharmaconet_norm'].fillna(0)
                ) / 2
                
                df_summary = df_summary.sort_values('combined_score', ascending=False)
                df_summary['combined_rank'] = range(1, len(df_summary) + 1)
        
        # Save CSV
        csv_file = self.output_dir / "integrated_summary.csv"
        df_summary.to_csv(csv_file, index=False)
        print(f"✅ CSV summary saved: {csv_file}")
        
        # Save top hits
        if len(df_summary) > 0:
            top_hits = df_summary.head(50)
            top_file = self.output_dir / "top_50_hits.csv"
            top_hits.to_csv(top_file, index=False)
            print(f"✅ Top 50 hits saved: {top_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate final integrated report'
    )
    parser.add_argument(
        '--trac_results',
        type=Path,
        required=True,
        help='Trac screening results file'
    )
    parser.add_argument(
        '--screening_results',
        type=Path,
        required=True,
        help='Directory containing PharmacoNet screening results'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output directory for final reports'
    )
    
    args = parser.parse_args()
    
    print("="*100)
    print("📊 Generating Final Integrated Report")
    print("="*100)
    
    generator = ReportGenerator(
        args.trac_results,
        args.screening_results,
        args.output
    )
    
    # Load data
    if not generator.load_trac_results():
        return 1
    
    if not generator.load_screening_results():
        return 1
    
    # Generate reports
    generator.generate_integrated_report()
    
    print("\n🎉 Report generation complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
