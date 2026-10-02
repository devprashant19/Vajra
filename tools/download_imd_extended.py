import os
import time

def download_imd():
    raw_dir = "data/raw/imd"
    rain_dir = os.path.join(raw_dir, "rain")
    os.makedirs(rain_dir, exist_ok=True)
    import imdlib as imd
    
    for year in range(2000, 2025):
        file_path = os.path.join(rain_dir, f"{year}.grd")
        if os.path.exists(file_path):
            continue
            
        print(f"Downloading IMD data for {year}...")
        attempts = 0
        while attempts < 3:
            try:
                imd.get_data('rain', year, year, fn_format='yearwise', file_dir=raw_dir)
                print(f"Downloaded {year} successfully.")
                break
            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts} failed for {year}: {e}")
                if attempts < 3:
                    time.sleep(2 ** attempts)
                else:
                    print(f"Failed to download {year} after 3 attempts.")

if __name__ == "__main__":
    download_imd()
