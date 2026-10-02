#!/usr/bin/env python3
"""
SEVIR Remote Extraction Script

Extracts selected events from SEVIR S3 bucket and writes them to Zarr shards.
Can be run on Google Colab, Kaggle, or any machine with fast AWS S3 access.

Requirements:
pip install pandas h5py zarr fsspec s3fs requests
"""

import os
import json
import hashlib
import pandas as pd
import h5py
import zarr
import urllib.request
import time
import argparse

CATALOG_PATH = "data/catalog/sevir_tranche1_events.csv"
OUTPUT_DIR = "data/sevir_extracted"
MANIFEST_PATH = os.path.join(OUTPUT_DIR, "manifest.json")

def fetch_chunk(url, offset, size, retries=3):
    headers = {'Range': f'bytes={offset}-{offset + size - 1}'}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            if attempt == retries - 1:
                raise e
            time.sleep(2 ** attempt)

def extract_events_from_file(file_name, event_indices, modality):
    url = f"https://sevir.s3.amazonaws.com/data/{file_name}"
    
    print(f"Opening {file_name} remotely...")
    import s3fs
    fs = s3fs.S3FileSystem(anon=True)
    with fs.open(f"sevir/data/{file_name}", "rb") as f:
        with h5py.File(f, "r") as hf:
            ds = hf[modality]
            shape = ds.shape
            dtype = ds.dtype
            chunks = ds.chunks
            
            extracted = {}
            
            for idx in event_indices:
                if chunks is None:
                    # Contiguous layout handling
                    event_size = ds.id.get_storage_size() // shape[0]
                    offset = ds.id.get_offset() + idx * event_size
                    print(f"Fetching contiguous event {idx} at {offset} size {event_size}...")
                    data_bytes = fetch_chunk(url, offset, event_size)
                    import numpy as np
                    event_data = np.frombuffer(data_bytes, dtype=dtype).reshape(shape[1:])
                    extracted[idx] = event_data
                else:
                    # Chunked layout handling (using h5py directly as it handles B-Trees on fast network)
                    print(f"Fetching chunked event {idx} via h5py...")
                    event_data = ds[idx]
                    extracted[idx] = event_data
                    
            return extracted

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=int, help="Verify mode: exit after downloading N events", default=None)
    args = parser.parse_args()

    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog not found at {CATALOG_PATH}")
        print("Please upload sevir_tranche1_events.csv to data/catalog/ before running.")
        return
        
    df = pd.read_csv(CATALOG_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            manifest = json.load(f)
            
    grouped = df.groupby(['file_name', 'img_type'])
    
    for (file_name, img_type), group in grouped:
        indices = group['file_index'].tolist()
        event_ids = group['id'].tolist()
        
        all_done = True
        for eid in event_ids:
            if f"{eid}_{img_type}.zarr" not in manifest:
                all_done = False
                break
                
        if all_done:
            print(f"Skipping {file_name}, all events already extracted.")
            continue
            
        print(f"Processing {len(indices)} events from {file_name}")
        try:
            if args.verify:
                indices = indices[:args.verify]
                event_ids = event_ids[:args.verify]
                
            extracted_data = extract_events_from_file(file_name, indices, img_type)
            
            for eid, idx in zip(event_ids, indices):
                out_name = f"{eid}_{img_type}.zarr"
                out_path = os.path.join(OUTPUT_DIR, out_name)
                
                z = zarr.open(out_path, mode='w', shape=extracted_data[idx].shape, dtype=extracted_data[idx].dtype, chunks=extracted_data[idx].shape)
                z[:] = extracted_data[idx]
                
                manifest[out_name] = {"checksum": "zarr_dir", "status": "completed"}
                
            with open(MANIFEST_PATH, "w") as f:
                json.dump(manifest, f, indent=2)
                
            if args.verify:
                print(f"Verify mode: successfully processed chunk for {file_name}. Exiting.")
                return
                
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            
    print("Extraction complete. Compress data/sevir_extracted to download.")

if __name__ == "__main__":
    main()
