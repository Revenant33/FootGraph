# import pandas as pd

# # Load players
# players_df = pd.read_csv("data/FootStats22.csv", encoding='ISO-8859-1', sep=';')
# print(players_df.columns)

# # Load matches
# matches_df = pd.read_csv("data/20222023 (1).csv")

# # --- NEW STEP: Remove rows with 'women' in any column (case-insensitive) ---
# matches_df = matches_df[~matches_df.apply(lambda row: row.astype(str).str.lower().str.contains("women").any(), axis=1)]

# # Continue with existing processing
# official_clubs = (
#     players_df["Squad"]
#     .dropna()
#     .unique()
# )

# official_leagues = (
#     players_df["Comp"]
#     .dropna()
#     .unique()
# )

# official_clubs = [c.strip() for c in official_clubs]
# official_leagues = [l.strip() for l in official_leagues]

# def normalize(name):
#     return (
#         name.lower()
#         .replace("utd", "united")
#         .replace(".", "")
#         .strip()
#     )

# club_mapping = {}
# for club in official_clubs:
#     club_mapping[normalize(club)] = club

# def harmonize_club(name):
#     if pd.isna(name):
#         return None
#     key = normalize(name)
#     return club_mapping.get(key, name)

# matches_df["Home Team"] = matches_df["Home Team"].apply(harmonize_club)
# matches_df["Away Team"] = matches_df["Away Team"].apply(harmonize_club)

# def harmonize_competition(name):
#     if pd.isna(name):
#         return None

#     key = name.lower()
#     if "champions league" in key:
#         return "Champions League"
#     if "europa conference" in key:
#         return "Europa Conference League"
#     if "europa league" in key:
#         return "Europa League"
#     if "fa cup" in key:
#         return "FA Cup"
#     if "premier league" in key:
#         return "Premier League"
#     if "la liga" in key:
#         return "La Liga"
#     if "ligue 1" in key:
#         return "Ligue 1"
#     if "serie a" in key:
#         return "Serie A"
#     if "bundesliga" in key:
#         return "Bundesliga"

#     return None

# matches_df["Competition"] = matches_df["Competition"].apply(harmonize_competition)

# allowed_competitions = [
#     "Premier League",
#     "La Liga",
#     "Serie A",
#     "Bundesliga",
#     "Ligue 1",
#     "Champions League",
#     "Europa League",
#     "Europa Conference League",
#     "FA Cup",
# ]

# matches_df = matches_df[matches_df["Competition"].isin(allowed_competitions)]

# matches_df.to_csv("data/20222023_clean.csv", index=False)
# print("✅ Dataset nettoyé et harmonisé")
# print(matches_df["Competition"].value_counts())
# =============================================
# FOOTBALL SCOUTING - COMPLETE DATA HARMONIZATION
# Harmonize club names between FootStats and Matches CSVs
# =============================================

import pandas as pd

print("="*70)
print("🔧 FIXING CLUB NAMES IN MATCHES CSV")
print("="*70)

# Load matches CSV
matches_df = pd.read_csv("data/20222023_clean.csv")
print(f"\n✅ Loaded: {len(matches_df)} matches")

# =============================================
# CLUB NAME MAPPING
# Format: "Wrong Name in Matches" : "Correct Name from FootStats"
# =============================================

club_name_mapping = {
    # PREMIER LEAGUE
    "AFC Bournemouth": "Bournemouth",
    "Brighton & Hove Albion": "Brighton",
    "Nottingham Forest": "Nott'ham Forest",
    "Tottenham Hotspur": "Tottenham",
    "West Ham United": "West Ham",
    "Wolverhampton Wanderers": "Wolves",
    
    # LA LIGA
    "Athletic Bilbao": "Athletic Club",
    "Real Betis": "Betis",
    "Real Valladolid": "Valladolid",
    
    # SERIE A
    "AC Milan": "Milan",
    "Inter Milan": "Inter",
    
    # BUNDESLIGA
    "1 FC Köln": "Köln",
    "1 FC Union Berlin": "Union Berlin",
    "1899 Hoffenheim": "Hoffenheim",
    "Bayer 04 Leverkusen": "Leverkusen",
    "Borussia Dortmund": "Dortmund",
    "Borussia Mönchengladbach": "M'Gladbach",
    "Eintracht Frankfurt": "Eint Frankfurt",
    "FC Augsburg": "Augsburg",
    "FC Schalke 04": "Schalke 04",
    "Hertha Berlin": "Hertha BSC",
    "SC Freiburg": "Freiburg",
    "VfB Stuttgart": "Stuttgart",
    "VfL Bochum": "Bochum",
    "VfL Wolfsburg": "Wolfsburg",
    
    # LIGUE 1
    "Clermont": "Clermont Foot",
    "Paris St Germain": "Paris S-G",
}

print(f"\n📋 Club name mappings to apply: {len(club_name_mapping)}")

# =============================================
# APPLY MAPPING TO HOME AND AWAY TEAMS
# =============================================

print("\n🔄 Applying club name fixes...")

# Count changes
home_changes = 0
away_changes = 0

# Replace home teams
for wrong_name, correct_name in club_name_mapping.items():
    home_mask = matches_df['Home Team'] == wrong_name
    home_count = home_mask.sum()
    if home_count > 0:
        matches_df.loc[home_mask, 'Home Team'] = correct_name
        home_changes += home_count
        print(f"   ✓ Home: '{wrong_name}' → '{correct_name}' ({home_count} matches)")

# Replace away teams
for wrong_name, correct_name in club_name_mapping.items():
    away_mask = matches_df['Away Team'] == wrong_name
    away_count = away_mask.sum()
    if away_count > 0:
        matches_df.loc[away_mask, 'Away Team'] = correct_name
        away_changes += away_count
        print(f"   ✓ Away: '{wrong_name}' → '{correct_name}' ({away_count} matches)")

print(f"\n✅ Total changes: {home_changes + away_changes}")
print(f"   - Home teams: {home_changes}")
print(f"   - Away teams: {away_changes}")

# =============================================
# SAVE FIXED CSV
# =============================================

output_file = "data/20222023_clean_fixed.csv"
matches_df.to_csv(output_file, index=False)

print(f"\n💾 Saved fixed data to: {output_file}")

# =============================================
# VERIFICATION
# =============================================

print("\n🔍 VERIFICATION:")
print("-"*70)

# Check that old names are gone
old_names_remaining = []
for wrong_name in club_name_mapping.keys():
    home_count = (matches_df['Home Team'] == wrong_name).sum()
    away_count = (matches_df['Away Team'] == wrong_name).sum()
    if home_count > 0 or away_count > 0:
        old_names_remaining.append((wrong_name, home_count + away_count))

if old_names_remaining:
    print("\n⚠️  WARNING: Some old names still exist:")
    for name, count in old_names_remaining:
        print(f"   - '{name}': {count} occurrences")
else:
    print("\n✅ All old club names successfully replaced!")

# Check that new names exist
print("\n📊 New club names in fixed data:")
new_names_found = []
for correct_name in club_name_mapping.values():
    home_count = (matches_df['Home Team'] == correct_name).sum()
    away_count = (matches_df['Away Team'] == correct_name).sum()
    total = home_count + away_count
    if total > 0:
        new_names_found.append((correct_name, total))
        print(f"   ✓ '{correct_name}': {total} matches")

# =============================================
# SUMMARY
# =============================================

print("\n" + "="*70)
print("📊 SUMMARY")
print("="*70)
print(f"Original file: data/20222023_clean.csv")
print(f"Fixed file:    {output_file}")
print(f"Total matches: {len(matches_df)}")
print(f"Clubs fixed:   {len(club_name_mapping)}")
print(f"Changes made:  {home_changes + away_changes}")

print("\n✅ DONE! Club names harmonized with FootStats.")
print("="*70)
print("\n📝 Next steps:")
print("   1. Verify the changes look correct")
print("   2. Use '20222023_clean_fixed.csv' for Neo4j import")
print("   3. All club names now match FootStats perfectly!")
print("\n")