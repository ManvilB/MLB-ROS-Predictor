import pybaseball as pyb
import pandas as pd
import os

class DataLoader:
    def __init__(self, start_dt, end_dt, data_dir="data"):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _fetch_statcast(self, start, end):
        """Internal method to fetch pitch-by-pitch data for a specific window."""
        print(f"Fetching Statcast pitches from {start} to {end}...")
        return pyb.statcast(start_dt=start, end_dt=end)
        
    def _fetch_player_registry(self):
        """Internal method to fetch the MLB player ID registry."""
        return pyb.chadwick_register()
        
    def _get_season_summary(self, start, end, registry):
        """Generates aggregated player metrics for a given date range."""
        pitches = self._fetch_statcast(start, end)
        
        # Map player IDs to names safely
        registry['name_first'] = registry['name_first'].fillna('')
        registry['name_last'] = registry['name_last'].fillna('')
        registry['batter_name'] = registry['name_first'] + ' ' + registry['name_last']
        registry['batter_name'] = registry['batter_name'].str.title().str.strip()
        
        mapping = registry[['key_mlbam', 'batter_name']]
        pitches = pitches.merge(mapping, left_on='batter', right_on='key_mlbam', how='left')
        
        batted_balls = pitches.dropna(subset=['launch_speed', 'launch_angle', 'estimated_woba_using_speedangle'])
        
        stats = batted_balls.groupby('batter_name').agg(
            total_batted_balls=('events', 'count'),
            avg_exit_velocity=('launch_speed', 'mean'),
            max_exit_velocity=('launch_speed', 'max'),
            avg_launch_angle=('launch_angle', 'mean'),
            xwOBA=('estimated_woba_using_speedangle', 'mean'),
            hard_hits=('launch_speed', lambda x: (x >= 95).sum()),
            home_runs=('events', lambda x: (x == 'home_run').sum())
        ).reset_index()
        
        stats['hard_hit_rate'] = stats['hard_hits'] / stats['total_batted_balls']
        return stats.drop(columns=['hard_hits'])

    def get_clean_hitter_matrix(self, min_batted_balls=50):
        """Public method to generate a feature matrix combining 2026 and historical lags."""
        registry = self._fetch_player_registry()
        
        # 1. Fetch historical frames for matching calendar windows
        print("\n--- Processing Historical Lags ---")
        stats_2024 = self._get_season_summary("2024-03-28", "2024-05-31", registry)
        stats_2025 = self._get_season_summary("2025-03-27", "2025-05-31", registry)
        
        # 2. Fetch current 2026 data
        print("\n--- Processing Current 2026 Context ---")
        stats_2026 = self._get_season_summary(self.start_dt, self.end_dt, registry)
        
        # 3. Clean and isolate historical columns to prevent naming collisions
        stats_2024 = stats_2024[['batter_name', 'xwOBA', 'home_runs']].rename(
            columns={'xwOBA': 'xwOBA_2024', 'home_runs': 'hr_2024'}
        )
        stats_2025 = stats_2025[['batter_name', 'xwOBA', 'home_runs']].rename(
            columns={'xwOBA': 'xwOBA_2025', 'home_runs': 'hr_2025'}
        )
        
        # 4. Merge histories onto the current season matrix
        print("\nAssembling multi-year lag feature matrix...")
        matrix = stats_2026.merge(stats_2025, on='batter_name', how='left')
        matrix = matrix.merge(stats_2024, on='batter_name', how='left')
        
        # Filter rows by current season minimum sample size
        matrix = matrix[matrix['total_batted_balls'] >= min_batted_balls]
        
        # 5. Handle Rookies / Missing Data via League-Average Imputation
        matrix['xwOBA_2025'] = matrix['xwOBA_2025'].fillna(matrix['xwOBA'].mean())
        matrix['hr_2025'] = matrix['hr_2025'].fillna(matrix['home_runs'].mean())
        matrix['xwOBA_2024'] = matrix['xwOBA_2024'].fillna(matrix['xwOBA'].mean())
        matrix['hr_2024'] = matrix['hr_2024'].fillna(matrix['home_runs'].mean())
        
        return matrix