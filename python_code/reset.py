from daily_challenge_manager import get_challenges

if __name__ == '__main__':
    result = get_challenges()
    print(f"\n✅ Daily challenges generated with {len(result['pairs'])} pairs.")
    print(f"Start: {result['start']}")
    print(f"Expires: {result['expires']}")