#!/usr/bin/env python3
"""Regenerate the app's original, type-balanced practice bank via question_factory.js."""
import argparse
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261002)
    parser.add_argument('--count', type=int, default=10, help='new items per area (1–40)')
    parser.add_argument('--output', default='extra.json')
    args = parser.parse_args()
    subprocess.run([
        'node', str(ROOT / 'generate_question_bank.js'),
        '--seed', str(args.seed), '--count', str(args.count),
        '--output', str(pathlib.Path(args.output).resolve())
    ], check=True)

if __name__ == '__main__':
    main()
